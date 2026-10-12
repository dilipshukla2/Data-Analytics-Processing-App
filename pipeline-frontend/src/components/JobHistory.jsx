import { formatDateTime, formatHash, formatNumber } from "../utils/format";

export default function JobHistory({ history, onClear }) {
  if (!history || history.length === 0) return null;

  return (
    <div className="card">
      <div className="history-header">
        <h2>🕓 Job History ({history.length})</h2>
        <button className="btn small" onClick={onClear}>
          Clear
        </button>
      </div>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Job ID</th>
              <th>Time</th>
              <th>Records</th>
              <th>Peak Mem (MB)</th>
              <th>Duration (s)</th>
            </tr>
          </thead>
          <tbody>
            {history.map((h) => (
              <tr key={h.jobId + h.time}>
                <td className="hash" title={h.jobId}>
                  {formatHash(h.jobId, 8)}
                </td>
                <td>{formatDateTime(h.time)}</td>
                <td>{formatNumber(h.records)}</td>
                <td>{h.memory}</td>
                <td>{h.duration}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}