import React, { useEffect, useMemo, useState } from 'react';
import { listDocuments, getDocumentMetrics } from '../api/documents.js';
import { ComparisonBarChart } from './Charts.jsx';
import { formatCurrency, formatDelta } from '../utils/format.js';

const METRIC_LABELS = {
  revenue: 'Revenue',
  net_income: 'Net income',
  gross_margin: 'Gross margin',
  operating_expenses: 'Operating expenses',
  eps: 'EPS',
};

export default function Comparison() {
  const [documents, setDocuments] = useState([]);
  const [docAId, setDocAId] = useState('');
  const [docBId, setDocBId] = useState('');
  const [metricsA, setMetricsA] = useState(null);
  const [metricsB, setMetricsB] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    listDocuments()
      .then((docs) => setDocuments(docs.filter((d) => d.status === 'completed')))
      .catch((err) => setError(err.message));
  }, []);

  const handleCompare = async () => {
    if (!docAId || !docBId) return;
    setLoading(true);
    setError(null);
    try {
      const [a, b] = await Promise.all([
        getDocumentMetrics(docAId),
        getDocumentMetrics(docBId),
      ]);
      setMetricsA(a);
      setMetricsB(b);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const chartData = useMemo(() => {
    if (!metricsA || !metricsB) return [];
    return Object.keys(METRIC_LABELS)
      .filter((key) => key in metricsA && key in metricsB)
      .map((key) => ({
        metric: METRIC_LABELS[key],
        a: metricsA[key],
        b: metricsB[key],
      }));
  }, [metricsA, metricsB]);

  const insights = useMemo(() => {
    if (!metricsA || !metricsB) return [];
    return Object.keys(METRIC_LABELS)
      .filter((key) => key in metricsA && key in metricsB && metricsA[key] !== 0)
      .map((key) => {
        const delta = (metricsB[key] - metricsA[key]) / Math.abs(metricsA[key]);
        return { key, label: METRIC_LABELS[key], delta };
      })
      .filter((row) => Math.abs(row.delta) >= 0.15)
      .sort((a, b) => Math.abs(b.delta) - Math.abs(a.delta));
  }, [metricsA, metricsB]);

  const docLabel = (id) => {
    const doc = documents.find((d) => d.document_id === id);
    return doc ? `${doc.company_name} — ${doc.report_date}` : id;
  };

  return (
    <div>
      <div className="grid sm:grid-cols-2 gap-4 max-w-2xl">
        <div>
          <label className="field-label">Document A</label>
          <select
            value={docAId}
            onChange={(e) => setDocAId(e.target.value)}
            className="w-full bg-white/60 border border-rule rounded-sm px-3 py-2 text-sm font-body"
          >
            <option value="">Select a document…</option>
            {documents.map((d) => (
              <option key={d.document_id} value={d.document_id}>
                {d.company_name} — {d.report_date}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="field-label">Document B</label>
          <select
            value={docBId}
            onChange={(e) => setDocBId(e.target.value)}
            className="w-full bg-white/60 border border-rule rounded-sm px-3 py-2 text-sm font-body"
          >
            <option value="">Select a document…</option>
            {documents.map((d) => (
              <option key={d.document_id} value={d.document_id}>
                {d.company_name} — {d.report_date}
              </option>
            ))}
          </select>
        </div>
      </div>

      <button
        className="btn-primary mt-5"
        onClick={handleCompare}
        disabled={!docAId || !docBId || docAId === docBId || loading}
      >
        {loading ? 'Comparing…' : 'Compare'}
      </button>
      {docAId && docAId === docBId && (
        <p className="mt-2 text-sm text-rust">Choose two different documents.</p>
      )}
      {error && <p className="mt-2 text-sm text-rust">{error}</p>}

      {metricsA && metricsB && (
        <div className="mt-10 space-y-8">
          <div className="axis-divider" />

          <div>
            <div className="axis-label mb-3">Revenue & income, side by side</div>
            <div className="card px-4 py-4">
              <ComparisonBarChart
                data={chartData}
                seriesLabels={[docLabel(docAId), docLabel(docBId)]}
              />
            </div>
          </div>

          <div>
            <div className="axis-label mb-3">Metric table</div>
            <div className="card overflow-x-auto">
              <table className="w-full text-sm font-mono">
                <thead>
                  <tr className="border-b border-rule text-left">
                    <th className="px-4 py-2.5 font-body text-inkmuted font-medium">Metric</th>
                    <th className="px-4 py-2.5">{docLabel(docAId)}</th>
                    <th className="px-4 py-2.5">{docLabel(docBId)}</th>
                    <th className="px-4 py-2.5">Δ</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.keys(METRIC_LABELS)
                    .filter((key) => key in metricsA && key in metricsB)
                    .map((key) => {
                      const delta =
                        metricsA[key] !== 0 ? (metricsB[key] - metricsA[key]) / Math.abs(metricsA[key]) : null;
                      return (
                        <tr key={key} className="border-b border-rule last:border-0">
                          <td className="px-4 py-2.5 font-body">{METRIC_LABELS[key]}</td>
                          <td className="px-4 py-2.5">{formatCurrency(metricsA[key])}</td>
                          <td className="px-4 py-2.5">{formatCurrency(metricsB[key])}</td>
                          <td className={`px-4 py-2.5 ${delta >= 0 ? 'delta-up' : 'delta-down'}`}>
                            {delta === null ? '—' : formatDelta(delta)}
                          </td>
                        </tr>
                      );
                    })}
                </tbody>
              </table>
            </div>
          </div>

          <div>
            <div className="axis-label mb-3">Insights</div>
            {insights.length === 0 ? (
              <p className="text-sm text-inkmuted">No metric moved more than 15% between the two documents.</p>
            ) : (
              <ul className="space-y-2">
                {insights.map((row) => (
                  <li
                    key={row.key}
                    className="flex items-center gap-3 border border-rule rounded-sm px-4 py-3 bg-white/50"
                  >
                    <span
                      className={`font-mono text-sm ${row.delta >= 0 ? 'delta-up' : 'delta-down'}`}
                    >
                      {formatDelta(row.delta)}
                    </span>
                    <span className="text-sm">
                      {row.label} {row.delta >= 0 ? 'increased' : 'decreased'} between the two periods.
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
