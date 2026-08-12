import React, { useCallback, useRef, useState } from 'react';
import { uploadDocument, pollDocumentStatus } from '../api/documents.js';
import { formatFileSize, truncateFilename } from '../utils/format.js';

const ACCEPTED_TYPE = 'application/pdf';

export default function UploadForm({ onComplete }) {
  const [file, setFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [progress, setProgress] = useState(0);
  const [phase, setPhase] = useState('idle');
  const [error, setError] = useState(null);
  const [documentId, setDocumentId] = useState(null);
  const inputRef = useRef(null);

  const validateAndSetFile = (candidate) => {
    setError(null);
    if (!candidate) return;
    if (candidate.type !== ACCEPTED_TYPE) {
      setError('Only PDF files are supported.');
      return;
    }
    if (candidate.size > 25 * 1024 * 1024) {
      setError('File is larger than the 25 MB limit.');
      return;
    }
    setFile(candidate);
  };

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setIsDragging(false);
    validateAndSetFile(e.dataTransfer.files?.[0]);
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;
    setError(null);
    setPhase('uploading');
    setProgress(0);

    try {
      const { document_id: id } = await uploadDocument(file, {
        onProgress: setProgress,
      });
      setDocumentId(id);
      setPhase('processing');

      const finalStatus = await pollDocumentStatus(id, {
        onTick: () => {},
      });

      if (finalStatus.status === 'completed') {
        setPhase('completed');
        onComplete?.(id);
      } else {
        setPhase('failed');
        setError('Processing failed on the server. Please try a different file.');
      }
    } catch (err) {
      setPhase('failed');
      setError(err.message);
    }
  };

  const reset = () => {
    setFile(null);
    setPhase('idle');
    setProgress(0);
    setError(null);
    setDocumentId(null);
  };

  const busy = phase === 'uploading' || phase === 'processing';

  return (
    <form onSubmit={handleSubmit} className="max-w-xl">
      <label className="field-label">Financial document (PDF)</label>

      <div
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
        className={[
          'border border-dashed rounded-sm px-6 py-10 text-center cursor-pointer transition-colors',
          isDragging ? 'border-sage bg-sage-light/40' : 'border-rule bg-white/50',
        ].join(' ')}
      >
        <input
          ref={inputRef}
          type="file"
          accept="application/pdf"
          className="hidden"
          onChange={(e) => validateAndSetFile(e.target.files?.[0])}
        />
        {file ? (
          <div className="font-mono text-sm">
            <div className="text-ink">{truncateFilename(file.name)}</div>
            <div className="text-inkmuted text-xs mt-1">{formatFileSize(file.size)}</div>
          </div>
        ) : (
          <div>
            <div className="font-display text-lg">Drop a PDF, or click to browse</div>
            <div className="axis-label mt-2">10-K, 10-Q, earnings release — up to 25 MB</div>
          </div>
        )}
      </div>

      {error && (
        <p className="mt-3 text-sm text-rust font-body" role="alert">
          {error}
        </p>
      )}

      {busy && (
        <div className="mt-4">
          <div className="axis-label mb-1.5">
            {phase === 'uploading' ? `Uploading — ${progress}%` : 'Processing document…'}
          </div>
          <div className="h-1.5 w-full bg-rule/50 rounded-full overflow-hidden">
            <div
              className="h-full bg-sage transition-all duration-300"
              style={{
                width: phase === 'uploading' ? `${progress}%` : '100%',
              }}
            />
          </div>
        </div>
      )}

      {phase === 'completed' && (
        <p className="mt-4 text-sm text-sage-dark font-mono">
          Done — document {documentId} is ready.
        </p>
      )}

      <div className="mt-6 flex gap-3">
        <button type="submit" className="btn-primary" disabled={!file || busy}>
          {busy ? 'Working…' : 'Upload & process'}
        </button>
        {(file || phase !== 'idle') && (
          <button type="button" className="btn-secondary" onClick={reset} disabled={busy}>
            Reset
          </button>
        )}
      </div>
    </form>
  );
}
