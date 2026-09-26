'use client';
import { useEffect, useState } from 'react';

interface CostData {
  project_id: string;
  model_version: string;
  total_cost: number;
  total_input_tokens: number;
  total_output_tokens: number;
  total_requests: number;
}

export default function Dashboard() {
  const [data, setData] = useState<CostData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetch('http://127.0.0.1:8000/api/costs')
      .then(res => res.json())
      .then(d => {
        setData(d);
        setLoading(false);
      })
      .catch(e => {
        console.error(e);
        setError('Failed to load cost data. Ensure FastAPI is running on port 8000.');
        setLoading(false);
      });
  }, []);

  const totalCost = data.reduce((acc, curr) => acc + curr.total_cost, 0);
  const totalTokens = data.reduce((acc, curr) => acc + curr.total_input_tokens + curr.total_output_tokens, 0);
  const totalRequests = data.reduce((acc, curr) => acc + curr.total_requests, 0);

  return (
    <div>
      <div className="page-header">
        <h2 className="page-title">Cost Governor</h2>
        <p className="page-subtitle">Aggregate costs and token usage by project and model.</p>
      </div>

      {error ? (
        <div style={{ color: 'var(--danger)', marginBottom: '24px' }}>{error}</div>
      ) : null}

      <div className="grid-cards">
        <div className="card">
          <div className="stat-label">Total Cost</div>
          <div className="stat-value">${totalCost.toFixed(4)}</div>
        </div>
        <div className="card">
          <div className="stat-label">Total Tokens</div>
          <div className="stat-value">{totalTokens.toLocaleString()}</div>
        </div>
        <div className="card">
          <div className="stat-label">Total Requests</div>
          <div className="stat-value">{totalRequests.toLocaleString()}</div>
        </div>
      </div>

      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>Project</th>
              <th>Model</th>
              <th>Requests</th>
              <th>Tokens (In / Out)</th>
              <th>Total Cost</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={5}>Loading...</td></tr>
            ) : data.length === 0 ? (
              <tr><td colSpan={5}>No data available</td></tr>
            ) : (
              data.map((row, idx) => (
                <tr key={idx}>
                  <td>
                    <span className="badge badge-primary">{row.project_id}</span>
                  </td>
                  <td>{row.model_version}</td>
                  <td>{row.total_requests}</td>
                  <td>{row.total_input_tokens} / {row.total_output_tokens}</td>
                  <td style={{ fontWeight: 600, color: 'var(--success)' }}>
                    ${row.total_cost.toFixed(4)}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
