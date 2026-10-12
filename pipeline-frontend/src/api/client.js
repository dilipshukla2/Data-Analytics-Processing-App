import axios from "axios";

const BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api/v1";

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 0, // pipeline requests can queue for minutes — do not abort
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use((config) => {
  config.metadata = { startTime: Date.now() };
  console.debug(`[API] → ${config.method?.toUpperCase()} ${config.url}`);
  return config;
});

api.interceptors.response.use(
  (response) => {
    const ms = Date.now() - (response.config.metadata?.startTime || Date.now());
    console.debug(
      `[API] ← ${response.status} ${response.config.url} (${ms}ms)`
    );
    return response;
  },
  (error) => {
    const cfg = error.config || {};
    const ms = Date.now() - (cfg.metadata?.startTime || Date.now());
    console.error(
      `[API] ✗ ${cfg.method?.toUpperCase()} ${cfg.url} (${ms}ms)`,
      error.message
    );
    return Promise.reject(error);
  }
);

export const triggerPipeline = () => api.post("/pipeline/trigger/", {});
export const runStep1 = () => api.post("/pipeline/step1/", {});
export const runStep2And3 = () => api.post("/pipeline/step2-3/", {});
export const runRamBomb = () => api.post("/pipeline/ram-bomb/", {});
export const getResult = (jobId) => api.get(`/pipeline/${jobId}/result/`);

export default api;