import React, { useEffect, useRef, useState } from 'react';
import { streamChatMessage, sendChatMessage } from '../api/chat.js';

export default function Chatbot({ documentId }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [streamingSupported, setStreamingSupported] = useState(true);
  const scrollRef = useRef(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const query = input.trim();
    if (!query || !documentId || isSending) return;

    setMessages((prev) => [...prev, { role: 'user', text: query }]);
    setInput('');
    setIsSending(true);

    setMessages((prev) => [...prev, { role: 'assistant', text: '', citations: [] }]);

    try {
      if (streamingSupported) {
        const { citations } = await streamChatMessage(documentId, query, {
          onDelta: (delta) => {
            setMessages((prev) => {
              const next = [...prev];
              const last = next[next.length - 1];
              next[next.length - 1] = { ...last, text: last.text + delta };
              return next;
            });
          },
        });
        setMessages((prev) => {
          const next = [...prev];
          next[next.length - 1] = { ...next[next.length - 1], citations };
          return next;
        });
      } else {
        const { answer, citations } = await sendChatMessage(documentId, query);
        setMessages((prev) => {
          const next = [...prev];
          next[next.length - 1] = { role: 'assistant', text: answer, citations };
          return next;
        });
      }
    } catch (err) {
      if (streamingSupported) {
        setStreamingSupported(false);
        try {
          const { answer, citations } = await sendChatMessage(documentId, query);
          setMessages((prev) => {
            const next = [...prev];
            next[next.length - 1] = { role: 'assistant', text: answer, citations };
            return next;
          });
        } catch (fallbackErr) {
          setMessages((prev) => {
            const next = [...prev];
            next[next.length - 1] = { role: 'assistant', text: `Error: ${fallbackErr.message}`, citations: [] };
            return next;
          });
        }
      } else {
        setMessages((prev) => {
          const next = [...prev];
          next[next.length - 1] = { role: 'assistant', text: `Error: ${err.message}`, citations: [] };
          return next;
        });
      }
    } finally {
      setIsSending(false);
    }
  };

  return (
    <div className="flex flex-col h-[65vh] card">
      <div ref={scrollRef} className="flex-1 overflow-y-auto px-5 py-5 space-y-5">
        {messages.length === 0 && (
          <p className="axis-label leading-relaxed">
            {documentId
              ? 'Ask a question about this document — e.g. "What was revenue growth year over year?"'
              : 'Upload and process a document first, then ask questions here.'}
          </p>
        )}
        {messages.map((m, i) => (
          <div key={i} className={m.role === 'user' ? 'text-right' : 'text-left'}>
            <div
              className={[
                'inline-block max-w-[85%] px-4 py-2.5 rounded-sm text-sm whitespace-pre-wrap',
                m.role === 'user' ? 'bg-ink text-paper' : 'bg-sage-light text-ink',
              ].join(' ')}
            >
              {m.text || (m.role === 'assistant' ? '…' : '')}
            </div>
            {m.citations?.length > 0 && (
              <div className="mt-1.5 flex flex-wrap gap-1.5 justify-start">
                {m.citations.map((c, ci) => (
                  
                    key={ci}
                    href={`#chunk-${c.chunk_id}`}
                    title={c.snippet}
                    className="font-mono text-[11px] px-1.5 py-0.5 rounded-sm border border-rule text-inkmuted hover:border-sage hover:text-sage-dark transition-colors"
                  >
                    p.{c.page}
                  </a>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>

      <form onSubmit={handleSubmit} className="border-t border-rule px-4 py-3 flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={documentId ? 'Ask about this document…' : 'Select a document first'}
          disabled={!documentId || isSending}
          className="flex-1 bg-transparent font-body text-sm px-2 py-2 border border-rule rounded-sm focus:border-sage outline-none disabled:opacity-50"
        />
        <button type="submit" className="btn-primary" disabled={!documentId || isSending || !input.trim()}>
          {isSending ? 'Sending…' : 'Send'}
        </button>
      </form>
    </div>
  );
}
