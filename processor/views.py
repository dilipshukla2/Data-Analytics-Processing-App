# processor/views.py
import logging
import time

from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import ProcessingJob, FraudAnalysisResult
from .services import (
    run_ec2_heavy_pipeline,
    run_step1_only,
    run_step2_3_on_slice,
    run_ram_bomb,
    PIPELINE_SEMAPHORE,
    PIPELINE_QUEUE_TIMEOUT,
)

logger = logging.getLogger(__name__)


class TriggerPipelineView(APIView):
    """
    POST /api/v1/pipeline/trigger/
    Master API with an infinite back-pressure queue.
    """
    def post(self, request):
        logger.info("MASTER API: request received, waiting for a free pipeline slot...")

        # Blocking acquire with no timeout.
        # The request will remain queued until a pipeline slot becomes available.
        # All requests will be processed, and none will return a 503 response.
        PIPELINE_SEMAPHORE.acquire()

        try:
            started = time.time()
            job = run_ec2_heavy_pipeline()

            return Response({
                "message": "Heavy parallel pipeline completed.",
                "job_id": str(job.job_id),
                "status": job.status,
                "records_processed": job.records_processed,
                "worker_peak_memory_mb": job.peak_memory_mb,
                "duration_seconds": round(time.time() - started, 2),
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Pipeline trigger failed: {e}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        finally:
            # Always release the semaphore so another queued request can proceed.
            PIPELINE_SEMAPHORE.release()


class Step1View(APIView):
    """
    POST /api/v1/pipeline/step1/
    RAM spike demo only.
    """
    def post(self, request):
        count, mem, secs = run_step1_only()
        return Response({
            "step": 1,
            "objects_loaded_in_ram": count,
            "peak_memory_mb": mem,
            "seconds": round(secs, 2),
        }, status=status.HTTP_200_OK)


class Step2And3View(APIView):
    """
    POST /api/v1/pipeline/step2-3/
    CPU spike demo on 25% data slice.
    """
    def post(self, request):
        groups, mem = run_step2_3_on_slice()
        return Response({
            "step": "2+3",
            "merchant_groups": groups,
            "peak_memory_mb": mem,
        }, status=status.HTTP_200_OK)


class GetResultView(APIView):
    """
    GET /api/v1/pipeline/<job_id>/result/
    Final result API.
    """
    def get(self, request, job_id):
        job = get_object_or_404(ProcessingJob, job_id=job_id)
        if job.status != "completed":
            return Response(
                {"error": f"Job status is: {job.status}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        rows = (
            FraudAnalysisResult.objects.filter(job=job)
            .select_related("merchant")
            .order_by("-total_suspicious_amount")[:50]
        )
        data = [{
            "merchant": r.merchant.name,
            "total_suspicious_amount": r.total_suspicious_amount,
            "transaction_count": r.transaction_count,
            "risk_hash": r.complex_risk_hash,
        } for r in rows]

        return Response({
            "job_id": str(job.job_id),
            "records_processed": job.records_processed,
            "worker_peak_memory_mb": job.peak_memory_mb,
            "top_merchants": data,
        }, status=status.HTTP_200_OK)


class RamBombView(APIView):
    """
    POST /api/v1/pipeline/ram-bomb/
    Instant 100% memory + CPU demo in a single process.
    """
    def post(self, request):
        return Response(
            run_ram_bomb(),
            status=status.HTTP_200_OK
        )