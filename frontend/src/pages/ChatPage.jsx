import React, { useEffect, useState } from 'react';
import { listDocuments } from '../api/documents.js';
import Chatbot from '../components/Chatbot.jsx';

export default function ChatPage() {
  const [documents, setDocuments] = useState([]);
  const [documentId, setDocumentId] = useState('');
  const [error, setError] = useState(null);

  useEffect(() => {
    listDocuments()
      .then((docs) => {
        const completed = docs.filter((d) => d.status === 'completed');
        setDocuments(completed);
        if (completed.length === 1) setDocumentId(completed[0].document_id);
      })
      .catch((err) => setError(err.message));
  }, []);

  return (
    <div>
      <div className="axis-label mb-2">Step 02</div>
      <h1 className="font-display text-3xl font-semibold mb-6">Ask a question</h1>

      <div className="max-w-sm mb-6">
        <label className="field-label">Document</label>
        <select
          value={documentId}
          onChange={(e) => setDocumentId(e.target.value)}
          className="w-full bg-white/60 border border-rule rounded-sm px-3 py-2 text-sm font-body"
        >
          <option value="">Select a processed document…</option>
          {documents.map((d) => (
            <option key={d.document_id} value={d.document_id}>
              {d.company_name} — {d.report_date}
            </option>
          ))}
        </select>
        {error && <p className="mt-2 text-sm text-rust">{error}</p>}
      </div>

      <Chatbot documentId={documentId || null} />
    </div>
  );
}
