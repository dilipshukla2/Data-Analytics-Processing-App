import { usePipeline } from "./hooks/usePipeline";
import PipelineButton from "./components/PipelineButton";
import StatusBar from "./components/StatusBar";
import MetricsPanel from "./components/MetricsPanel";
import ResultTable from "./components/ResultTable";
import JobHistory from "./components/JobHistory";
import "./App.css";

export default function App() {
  const {
    loading,
    statusText,
    metrics,
    currentResult,
    error,
    history,
    isBusy,
    actions,
    clearHistory,
  } = usePipeline();

  const apiBase =
    import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api/v1";

  return (
    <div className="app">
      <header>
        <h1>🚀 Data Analytics Pipeline Dashboard</h1>
        <p className="subtitle">
          Backend: <code>{apiBase}</code>
        </p>
      </header>

      <section className="controls">
        <PipelineButton
          variant="primary"
          label="▶ Trigger Master Pipeline"
          loadingLabel="Running Master Pipeline…"
          loading={loading === "trigger"}
          disabled={isBusy}
          onClick={actions.trigger}
        />

        <PipelineButton
          label="🧠 Step 1 (RAM Spike)"
          loadingLabel="Loading RAM…"
          loading={loading === "step1"}
          disabled={isBusy}
          onClick={actions.step1}
        />

        <PipelineButton
          label="🔥 Step 2+3 (CPU Spike)"
          loadingLabel="Burning CPU…"
          loading={loading === "step23"}
          disabled={isBusy}
          onClick={actions.step23}
        />

        <PipelineButton
          variant="danger"
          label="💣 RAM Bomb"
          loadingLabel="Bombing…"
          loading={loading === "rambomb"}
          disabled={isBusy}
          onClick={actions.rambomb}
        />
      </section>

      <StatusBar text={statusText} isLoading={isBusy} error={error} />

      {isBusy && !metrics && <div className="spinner" />}

      <MetricsPanel metrics={metrics} />
      <ResultTable result={currentResult} />
      <JobHistory history={history} onClear={clearHistory} />
    </div>
  );
}