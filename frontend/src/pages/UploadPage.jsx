import React, { useState } from 'react';
import UploadForm from '../components/UploadForm.jsx';
import Dashboard from '../components/Dashboard.jsx';

export default function UploadPage() {
  const [documentId, setDocumentId] = useState(null);

  return (
    <div>
      <div className="axis-label mb-2">Step 01</div>
      <h1 className="font-display text-3xl font-semibold mb-6">Upload a document</h1>

      <UploadForm onComplete={setDocumentId} />

      {documentId && (
        <div className="mt-12">
          <div className="axis-divider mb-6" />
          <div className="axis-label mb-3">Overview</div>
          <Dashboard documentId={documentId} />
        </div>
      )}
    </div>
  );
}
