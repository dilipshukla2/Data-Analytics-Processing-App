import { formatMoney, formatNumber, formatHash } from "../utils/format";

export default function ResultTable({ result }) {
  if (!result) return null;

  const merchants = result.top_merchants || [];

  return (
    <div className="card">
      <h2>🏆 Top Suspicious Merchants</h2>
      <p className="meta">
        Job: <code>{result.job_id}</code> • Records processed:{" "}
        <strong>{formatNumber(result.records_processed)}</strong> • Peak memory:{" "}
        <strong>{result.worker_peak_memory_mb} MB</strong>
      </p>

      {merchants.length === 0 ? (
        <p className="empty">No merchants returned.</p>
      ) : (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>#</th>
                <th>Merchant</th>
                <th>Suspicious Amount</th>
                <th>Tx Count</th>
                <th>Risk Hash</th>
              </tr>
            </thead>
            <tbody>
              {merchants.map((m, i) => (
                <tr key={m.risk_hash || i}>
                  <td>{i + 1}</td>
                  <td>{m.merchant}</td>
                  <td>{formatMoney(m.total_suspicious_amount)}</td>
                  <td>{formatNumber(m.transaction_count)}</td>
                  <td className="hash" title={m.risk_hash}>
                    {formatHash(m.risk_hash)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}