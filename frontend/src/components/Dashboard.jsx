import React, { useEffect, useState } from 'react';
import { getDocumentSummary } from '../api/documents.js';
import { formatReportDate } from '../utils/format.js';

export default function Dashboard({ documentId }) {
  const [summary, setSummary] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!documentId) return;
    setLoading(true);
    setError(null);
    getDocumentSummary(documentId)
      .then(setSummary)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [documentId]);

  if (!documentId) {
    return <p className="axis-label">Upload a document to see its overview here.</p>;
  }
  if (loading) {
    return <p className="axis-label">Loading summary…</p>;
  }
  if (error) {
    return <p className="text-sm text-rust">{error}</p>;
  }
  if (!summary) return null;

  return (
    <div className="card px-6 py-6">
      <div className="flex items-baseline justify-between flex-wrap gap-2">
        <h2 className="font-display text-2xl font-semibold">{summary.company_name}</h2>
        <span className="font-mono text-xs text-inkmuted">
          {formatReportDate(summary.report_date)}
        </span>
      </div>

      <div className="axis-divider my-5" />

      {summary.highlights?.length > 0 && (
        <div className="mb-6">
          <div className="axis-label mb-3">Highlights</div>
          <ul className="grid sm:grid-cols-2 gap-3">
            {summary.highlights.map((h, i) => (
              <li key={i} className="border border-rule rounded-sm px-4 py-3 bg-white/50">
                <div className="font-mono text-lg text-sage-dark">{h.value}</div>
                <div className="text-sm text-inkmuted mt-0.5">{h.label}</div>
              </li>
            ))}
          </ul>
        </div>
      )}

      <div>
        <div className="axis-label mb-2">Summary</div>
        <p className="font-body text-sm leading-relaxed text-inkmuted whitespace-pre-line">
          {summary.summary}
        </p>
      </div>
    </div>
  );
}
