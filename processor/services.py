# processor/services.py
import hashlib
import json
import logging
import math
import multiprocessing as mp
import platform
import resource
import threading
import time
from collections import defaultdict

from django.db.models import Min, Max
from django.utils import timezone

from .models import Transaction, ProcessingJob, FraudAnalysisResult
from .worker_bootstrap import django_setup

logger = logging.getLogger(__name__)

# ======================================================================
# SAFE SATURATION MODE (Targets ~14GB Memory Used without hanging)
# ======================================================================
WORKER_PROCESSES = 8
MAX_CONCURRENT_PIPELINES = 1
INNER_ITERATIONS = 1500         
BALLAST_MB_PER_WORKER = 2200    # Increased to 1800 for ~14GB gauge target (safe & compressible)
PIPELINE_QUEUE_TIMEOUT = 2000

PIPELINE_SEMAPHORE = threading.BoundedSemaphore(MAX_CONCURRENT_PIPELINES)

# Worker-side caches (module globals live inside EACH worker process)
_ROW_CACHE = {}
_BALLAST = None

# Global pool (safe because MAX_CONCURRENT_PIPELINES = 1)
_POOL = None
_POOL_LOCK = threading.Lock()

def _get_pool():
    """Spawn the worker pool ONCE and reuse it for every pipeline."""
    global _POOL
    with _POOL_LOCK:
        if _POOL is None:
            ctx = mp.get_context("spawn")
            _POOL = ctx.Pool(
                processes=WORKER_PROCESSES,
                initializer=django_setup,
            )
            logger.info(f"Worker pool spawned | processes={WORKER_PROCESSES}")
        return _POOL

def _peak_memory_mb():
    """Returns peak RAM (RSS) of the current process in MB."""
    usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if platform.system() == "Darwin":
        return round(usage / (1024 * 1024), 2)
    return round(usage / 1024, 2)

def _get_flagged_bounds():
    """Get min/max IDs for flagged transactions."""
    agg = (
        Transaction.objects
        .filter(status="flagged")
        .aggregate(min_id=Min("id"), max_id=Max("id"))
    )
    return agg["min_id"] or 0, agg["max_id"] or 0

def _split_range(min_id, max_id, parts):
    """Split ID range into equal chunks."""
    if max_id <= min_id:
        return [(min_id, max_id)]
    span = (max_id - min_id) // parts
    chunks, start = [], min_id
    for i in range(parts):
        end = max_id if i == parts - 1 else start + span
        chunks.append((start, end))
        start = end + 1
    return chunks

def _process_chunk(chunk):
    """
    Worker: caches rows once, reserves SAFE compressible ballast once,
    then spends 100% of its life in pure CPU compute.
    """
    global _BALLAST
    start_id, end_id = chunk

    # ONE-TIME memory ballast (SAFE: macOS can compress this, preventing hangs)
    if _BALLAST is None:
        _BALLAST = bytearray(BALLAST_MB_PER_WORKER * 1024 * 1024)
        for offset in range(0, len(_BALLAST), 4096):
            _BALLAST[offset] = 1
        logger.info(
            f"Worker {mp.current_process().name} ballast "
            f"{BALLAST_MB_PER_WORKER} MB resident (compressible/safe)"
        )

    # ONE-TIME full dataset cache (Real data memory: harder to compress, pushes gauge up)
    if "ALL" not in _ROW_CACHE:
        _ROW_CACHE["ALL"] = list(
            Transaction.objects.filter(status="flagged").values(
                "id", "amount", "merchant_id",
                "merchant__name", "customer__email_hash", "product__sku",
            )
        )
        logger.info(
            f"Worker {mp.current_process().name} cached ALL "
            f"{len(_ROW_CACHE['ALL']):,} rows"
        )

    # ONE-TIME chunk load, cached for all future pipelines
    cache_key = (start_id, end_id)
    if cache_key not in _ROW_CACHE:
        _ROW_CACHE[cache_key] = [
            row for row in _ROW_CACHE["ALL"]
            if start_id <= row["id"] <= end_id
        ]
        logger.info(
            f"Worker {mp.current_process().name} cached "
            f"{len(_ROW_CACHE[cache_key]):,} chunk rows"
        )
    rows = _ROW_CACHE[cache_key]

    partial = defaultdict(
        lambda: {"name": "", "count": 0, "total": 0.0, "hashes": []}
    )

    # PURE CPU BURN
    for row in rows:
        amount = row["amount"]
        merchant_id = row["merchant_id"]

        score = 0.0
        for i in range(INNER_ITERATIONS):
            score += (
                math.sqrt(amount + i)
                * math.log(amount + i + 1)
                * math.sin(i)
            )

        raw = (
            f"{row['merchant__name']}_{row['customer__email_hash']}_"
            f"{row['product__sku']}_{amount}_{score}"
        )
        record_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()

        bucket = partial[merchant_id]
        bucket["name"] = row["merchant__name"]
        bucket["count"] += 1
        bucket["total"] += amount
        bucket["hashes"].append(record_hash)

    collapsed = {}
    for merchant_id, bucket in partial.items():
        collapsed[merchant_id] = {
            "name": bucket["name"],
            "count": bucket["count"],
            "total": bucket["total"],
            "combined_hash": hashlib.md5(
                "".join(bucket["hashes"]).encode("utf-8")
            ).hexdigest(),
        }

    return collapsed, _peak_memory_mb()

def _merge_worker_results(worker_results):
    """Merge partial results from workers."""
    merged = {}
    peak = 0.0
    for collapsed, worker_mem in worker_results:
        peak = max(peak, worker_mem)
        for merchant_id, data in collapsed.items():
            if merchant_id not in merged:
                merged[merchant_id] = {
                    "name": data["name"],
                    "count": data["count"],
                    "total": data["total"],
                    "hash_parts": [data["combined_hash"]],
                }
            else:
                merged[merchant_id]["count"] += data["count"]
                merged[merchant_id]["total"] += data["total"]
                merged[merchant_id]["hash_parts"].append(data["combined_hash"])

    for data in merged.values():
        data["combined_hash"] = hashlib.md5(
            "".join(data["hash_parts"]).encode("utf-8")
        ).hexdigest()
        del data["hash_parts"]

    return merged, peak

def _persist_results(job, merged):
    """Persist results to database."""
    results = []
    for merchant_id, data in merged.items():
        json.dumps(data, indent=2)
        results.append(
            FraudAnalysisResult(
                job=job,
                merchant_id=merchant_id,
                total_suspicious_amount=data["total"],
                transaction_count=data["count"],
                complex_risk_hash=data["combined_hash"],
            )
        )
        if len(results) >= 1000:
            FraudAnalysisResult.objects.bulk_create(results)
            results = []
    if results:
        FraudAnalysisResult.objects.bulk_create(results)

def run_ec2_heavy_pipeline():
    """
    Main pipeline orchestrator.
    Uses the GLOBAL reused pool (spawned once) so workers stay hot.
    """
    job = ProcessingJob.objects.create(status="processing")
    logger.info(f"Pipeline started | Job {job.job_id}")
    started = time.time()

    try:
        min_id, max_id = _get_flagged_bounds()
        chunks = _split_range(min_id, max_id, WORKER_PROCESSES)

        logger.info(
            f"Step 1: flagged ids {min_id}..{max_id} -> {len(chunks)} chunks "
            f"| workers={WORKER_PROCESSES}"
        )

        # Reuse the global pool
        pool = _get_pool()
        worker_results = pool.map(_process_chunk, chunks)

        merged, worker_peak_mb = _merge_worker_results(worker_results)
        _persist_results(job, merged)

        job.status = "completed"
        job.records_processed = sum(d["count"] for d in merged.values())
        job.peak_memory_mb = worker_peak_mb
        job.completed_at = timezone.now()
        job.save()

        logger.info(f"Pipeline finished in {time.time() - started:.2f}s")
        return job

    except Exception as e:
        job.status = "failed"
        job.save()
        logger.error(f"Pipeline failed | Job {job.job_id} | {e}")
        raise

def run_ram_bomb():
    """Single process that loads entire DB into RAM + massive CPU burn."""
    started = time.time()
    qs = (
        Transaction.objects
        .select_related("merchant", "customer", "product")
        .filter(status="flagged")
    )
    objects = list(qs)
    object_count = len(objects)

    payload = [
        f"{o.id}|{o.amount}|{o.merchant.name}|{o.customer.email_hash}|{o.product.sku}"
        for o in objects
    ]
    giant = "\n".join(payload)
    giant_bytes = giant.encode("utf-8")

    digest = hashlib.sha256(giant_bytes).hexdigest()
    giant_mb = round(len(giant_bytes) / (1024 * 1024), 2)

    burn = 0.0
    for i in range(5_000_000):
        burn += math.sqrt(i % 997) * math.log((i % 997) + 1) * math.sin(i)

    peak = _peak_memory_mb()
    seconds = round(time.time() - started, 2)

    del objects, payload, giant, giant_bytes

    return {
        "objects_loaded_in_ram": object_count,
        "giant_string_mb": giant_mb,
        "sha256": digest,
        "cpu_burn_checksum": round(burn, 6),
        "peak_memory_mb": peak,
        "seconds": seconds,
    }

def run_step1_only():
    """Load all flagged objects into RAM (RAM spike demo)."""
    started = time.time()
    objs = list(
        Transaction.objects
        .select_related("merchant", "customer", "product")
        .filter(status="flagged")
    )
    return (len(objs), _peak_memory_mb(), time.time() - started)

def run_step2_3_on_slice():
    """CPU spike demo on 25% slice."""
    min_id, max_id = _get_flagged_bounds()
    quarter = min_id + (max_id - min_id) // 4
    collapsed, mem = _process_chunk((min_id, quarter))
    return len(collapsed), mem