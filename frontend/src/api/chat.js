import apiClient from './client.js';

export async function sendChatMessage(documentId, query) {
  const { data } = await apiClient.post('/chat', {
    document_id: documentId,
    query,
  });
  return data;
}

export async function streamChatMessage(documentId, query, { onDelta, signal } = {}) {
  const base = import.meta.env.VITE_API_BASE_URL || '/api/v1';
  const token = localStorage.getItem('auth_token');

  const response = await fetch(`${base}/chat/stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify({ document_id: documentId, query }),
    signal,
  });

  if (!response.ok || !response.body) {
    throw new Error(`Chat request failed (${response.status})`);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';
  let answer = '';
  let citations = [];

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    const lines = buffer.split('\n');
    buffer = lines.pop() ?? '';

    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed) continue;
      try {
        const parsed = JSON.parse(trimmed);
        if (parsed.delta) {
          answer += parsed.delta;
          onDelta?.(parsed.delta);
        }
        if (parsed.citations) {
          citations = parsed.citations;
        }
      } catch {
        // Ignore malformed keep-alive lines.
      }
    }
  }

  return { answer, citations };
}
