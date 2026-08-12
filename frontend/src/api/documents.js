import apiClient from './client.js';

export async function uploadDocument(file, { onProgress } = {}) {
  const form = new FormData();
  form.append('file', file);

  const { data } = await apiClient.post('/documents/upload', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (event) => {
      if (onProgress && event.total) {
        onProgress(Math.round((event.loaded / event.total) * 100));
      }
    },
  });
  return data;
}

export async function getDocumentStatus(documentId) {
  const { data } = await apiClient.get(`/documents/${documentId}/status`);
  return data;
}

export async function pollDocumentStatus(
  documentId,
  { intervalMs = 2000, timeoutMs = 120000, onTick } = {}
) {
  const start = Date.now();
  while (true) {
    const status = await getDocumentStatus(documentId);
    onTick?.(status);
    if (status.status === 'completed' || status.status === 'failed') {
      return status;
    }
    if (Date.now() - start > timeoutMs) {
      throw new Error('Timed out waiting for document processing.');
    }
    await new Promise((resolve) => setTimeout(resolve, intervalMs));
  }
}

export async function getDocumentSummary(documentId) {
  const { data } = await apiClient.get(`/documents/${documentId}`);
  return data;
}

export async function getDocumentMetrics(documentId) {
  const { data } = await apiClient.get(`/documents/${documentId}/metrics`);
  return data;
}

export async function listDocuments() {
  const { data } = await apiClient.get('/documents');
  return data;
}
