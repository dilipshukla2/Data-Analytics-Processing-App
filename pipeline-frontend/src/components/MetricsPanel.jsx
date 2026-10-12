import { humanLabel } from "../utils/format";

const MONO_KEYS = new Set(["jobId", "sha256", "cpuBurnChecksum"]);

export default function MetricsPanel({ metrics }) {
  if (!metrics) return null;

  const rows = Object.entries(metrics).filter(([k]) => k !== "type");

  return (
    <div className="card">
      <h2>📊 Metrics — {metrics.type}</h2>
      <table className="metrics-table">
        <tbody>
          {rows.map(([key, value]) => {
            const display =
              typeof value === "number" ? value.toLocaleString() : String(value);
            const mono = MONO_KEYS.has(key);
            return (
              <tr key={key}>
                <td className="label">{humanLabel(key)}</td>
                <td className={`value ${mono ? "mono" : ""}`}>{display}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}