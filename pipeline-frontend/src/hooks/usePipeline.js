import { useCallback, useEffect, useState } from "react";
import {
  triggerPipeline,
  runStep1,
  runStep2And3,
  runRamBomb,
  getResult,
} from "../api/client";

const HISTORY_KEY = "pipeline_history";
const MAX_HISTORY = 20;

export function usePipeline() {
  const [loading, setLoading] = useState(null);
  const [statusText, setStatusText] = useState("");
  const [metrics, setMetrics] = useState(null);
  const [currentResult, setCurrentResult] = useState(null);
  const [error, setError] = useState(null);

  const [history, setHistory] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem(HISTORY_KEY) || "[]");
    } catch {
      return [];
    }
  });

  useEffect(() => {
    localStorage.setItem(
      HISTORY_KEY,
      JSON.stringify(history.slice(0, MAX_HISTORY))
    );
  }, [history]);

  const clearHistory = useCallback(() => {
    setHistory([]);
    localStorage.removeItem(HISTORY_KEY);
  }, []);

  const reset = useCallback(() => {
    setError(null);
    setMetrics(null);
    setCurrentResult(null);
  }, []);

  const handleTrigger = useCallback(async () => {
    setLoading("trigger");
    reset();
    setStatusText("Request sent. Waiting for a free pipeline slot (may be queued)…");

    const startedAt = Date.now();
    try {
      const res = await triggerPipeline();
      const {
        job_id,
        status,
        records_processed,
        worker_peak_memory_mb,
        duration_seconds,
      } = res.data;

      setMetrics({
        type: "Master Pipeline",
        jobId: job_id,
        status,
        recordsProcessed: records_processed,
        peakMemoryMb: worker_peak_memory_mb,
        durationSeconds: duration_seconds,
        wallClock: ((Date.now() - startedAt) / 1000).toFixed(2),
      });

      setHistory((h) => [
        {
          jobId: job_id,
          time: new Date().toISOString(),
          records: records_processed,
          memory: worker_peak_memory_mb,
          duration: duration_seconds,
        },
        ...h,
      ]);

      setStatusText("Fetching top merchants…");
      const resultRes = await getResult(job_id);
      setCurrentResult(resultRes.data);
      setStatusText("Completed ✅");
    } catch (err) {
      const msg =
        err.response?.data?.error ||
        err.message ||
        "Pipeline failed. Check backend logs.";
      setError(msg);
      setStatusText("Failed ❌");
    } finally {
      setLoading(null);
    }
  }, [reset]);

  const handleStep1 = useCallback(async () => {
    setLoading("step1");
    reset();
    setStatusText("Loading all flagged transactions into RAM…");

    const startedAt = Date.now();
    try {
      const res = await runStep1();
      setMetrics({
        type: "Step 1 — RAM Spike",
        objectsLoaded: res.data.objects_loaded_in_ram,
        peakMemoryMb: res.data.peak_memory_mb,
        seconds: res.data.seconds,
        wallClock: ((Date.now() - startedAt) / 1000).toFixed(2),
      });
      setStatusText("Completed ✅");
    } catch (err) {
      setError(err.response?.data?.error || err.message);
      setStatusText("Failed ❌");
    } finally {
      setLoading(null);
    }
  }, [reset]);

  const handleStep2And3 = useCallback(async () => {
    setLoading("step23");
    reset();
    setStatusText("Running CPU-heavy aggregation on 25% slice…");

    const startedAt = Date.now();
    try {
      const res = await runStep2And3();
      setMetrics({
        type: "Step 2+3 — CPU Spike",
        merchantGroups: res.data.merchant_groups,
        peakMemoryMb: res.data.peak_memory_mb,
        wallClock: ((Date.now() - startedAt) / 1000).toFixed(2),
      });
      setStatusText("Completed ✅");
    } catch (err) {
      setError(err.response?.data?.error || err.message);
      setStatusText("Failed ❌");
    } finally {
      setLoading(null);
    }
  }, [reset]);

  const handleRamBomb = useCallback(async () => {
    setLoading("rambomb");
    reset();
    setStatusText("Firing RAM bomb — expect a hard memory spike…");

    const startedAt = Date.now();
    try {
      const res = await runRamBomb();
      setMetrics({
        type: "RAM Bomb",
        objectsLoaded: res.data.objects_loaded_in_ram,
        giantStringMb: res.data.giant_string_mb,
        sha256: res.data.sha256,
        cpuBurnChecksum: res.data.cpu_burn_checksum,
        peakMemoryMb: res.data.peak_memory_mb,
        seconds: res.data.seconds,
        wallClock: ((Date.now() - startedAt) / 1000).toFixed(2),
      });
      setStatusText("Completed ✅");
    } catch (err) {
      setError(err.response?.data?.error || err.message);
      setStatusText("Failed ❌");
    } finally {
      setLoading(null);
    }
  }, [reset]);

  return {
    loading,
    statusText,
    metrics,
    currentResult,
    error,
    history,
    isBusy: loading !== null,
    actions: {
      trigger: handleTrigger,
      step1: handleStep1,
      step23: handleStep2And3,
      rambomb: handleRamBomb,
    },
    clearHistory,
  };
}