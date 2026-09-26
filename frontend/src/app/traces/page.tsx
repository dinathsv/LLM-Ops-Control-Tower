'use client';
import { useEffect, useState } from 'react';

interface Trace {
  trace_id: string;
  timestamp: string;
  project_id: string;
  application_name: string;
  model_version: string;
  prompt: string;
  response: string;
  latency_ms: number;
  input_tokens: number;
  output_tokens: number;
  cost_usd: number;
}

export default function TraceExplorer() {
  const [traces, setTraces] = useState<Trace[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedTrace, setSelectedTrace] = useState<Trace | null>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    fetch('http://127.0.0.1:8000/api/traces')
      .then(res => res.json())
      .then(d => {
        setTraces(d);
        setLoading(false);
      })
      .catch(e => {
        console.error(e);
        setError('Failed to load traces. Ensure FastAPI is running on port 8000.');
        setLoading(false);
      });
  }, []);

  return (
    <div>
      <div className="page-header">
        <h2 className="page-title">Trace Explorer</h2>
        <p className="page-subtitle">Searchable, filterable view of all LLM requests and responses.</p>
      </div>

      {error ? (
        <div style={{ color: 'var(--danger)', marginBottom: '24px' }}>{error}</div>
      ) : null}

      <div className="table-container" style={{ marginBottom: '32px' }}>
        <table>
          <thead>
            <tr>
              <th>Timestamp</th>
              <th>App / Model</th>
              <th>Latency</th>
              <th>Cost</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={5}>Loading...</td></tr>
            ) : traces.length === 0 ? (
              <tr><td colSpan={5}>No traces found</td></tr>
            ) : (
              traces.map(trace => (
                <tr key={trace.trace_id} style={{ cursor: 'pointer', backgroundColor: selectedTrace?.trace_id === trace.trace_id ? 'rgba(255,255,255,0.05)' : '' }} onClick={() => setSelectedTrace(trace)}>
                  <td>{new Date(trace.timestamp).toLocaleString()}</td>
                  <td>
                    <div><strong>{trace.application_name}</strong></div>
                    <div style={{ fontSize: '0.8rem', color: 'var(--muted)' }}>{trace.model_version}</div>
                  </td>
                  <td>{trace.latency_ms}ms</td>
                  <td>${trace.cost_usd.toFixed(4)}</td>
                  <td>
                    <button style={{ padding: '6px 12px', borderRadius: '6px', backgroundColor: 'var(--primary)', color: '#fff', border: 'none', cursor: 'pointer' }} onClick={(e) => { e.stopPropagation(); setSelectedTrace(trace); }}>
                      View Details
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {selectedTrace && (
        <div className="card" style={{ marginTop: '32px' }}>
          <h3 style={{ marginBottom: '24px', fontSize: '1.25rem' }}>Trace Details: <span style={{ color: 'var(--muted)', fontSize: '1rem' }}>{selectedTrace.trace_id}</span></h3>
          <div className="detail-pane">
            <div>
              <div style={{ marginBottom: '8px', fontWeight: 500, color: 'var(--primary)' }}>Prompt</div>
              <div className="code-block">{selectedTrace.prompt}</div>
            </div>
            <div>
              <div style={{ marginBottom: '8px', fontWeight: 500, color: 'var(--success)' }}>Response</div>
              <div className="code-block">{selectedTrace.response}</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
