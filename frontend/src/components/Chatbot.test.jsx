import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Chatbot from '../components/Chatbot.jsx';
import * as chatApi from '../api/chat.js';

vi.mock('../api/chat.js');

describe('Chatbot', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('disables the input when no document is selected', () => {
    render(<Chatbot documentId={null} />);
    expect(screen.getByPlaceholderText(/select a document first/i)).toBeDisabled();
  });

  it('sends a message, streams the reply, and shows citation chips', async () => {
    chatApi.streamChatMessage.mockImplementation(async (documentId, query, { onDelta }) => {
      onDelta('Revenue grew ');
      onDelta('8% year over year.');
      return {
        answer: 'Revenue grew 8% year over year.',
        citations: [{ page: 4, chunk_id: 'c_12', snippet: 'Revenue increased 8%...' }],
      };
    });

    const user = userEvent.setup();
    render(<Chatbot documentId="doc_42" />);

    const input = screen.getByPlaceholderText(/ask about this document/i);
    await user.type(input, 'What was revenue growth?');
    await user.click(screen.getByRole('button', { name: /send/i }));

    expect(screen.getByText('What was revenue growth?')).toBeInTheDocument();

    await waitFor(() =>
      expect(screen.getByText('Revenue grew 8% year over year.')).toBeInTheDocument()
    );
    expect(screen.getByText('p.4')).toBeInTheDocument();
    expect(chatApi.streamChatMessage).toHaveBeenCalledWith(
      'doc_42',
      'What was revenue growth?',
      expect.any(Object)
    );
  });

  it('clears the input after sending', async () => {
    chatApi.streamChatMessage.mockResolvedValue({ answer: 'ok', citations: [] });
    const user = userEvent.setup();
    render(<Chatbot documentId="doc_1" />);

    const input = screen.getByPlaceholderText(/ask about this document/i);
    await user.type(input, 'Hello');
    await user.click(screen.getByRole('button', { name: /send/i }));

    await waitFor(() => expect(input).toHaveValue(''));
  });

  it('falls back to the non-streaming endpoint if streaming fails', async () => {
    chatApi.streamChatMessage.mockRejectedValue(new Error('stream not supported'));
    chatApi.sendChatMessage.mockResolvedValue({
      answer: 'Fallback answer.',
      citations: [],
    });

    const user = userEvent.setup();
    render(<Chatbot documentId="doc_9" />);

    await user.type(screen.getByPlaceholderText(/ask about this document/i), 'Test question');
    await user.click(screen.getByRole('button', { name: /send/i }));

    await waitFor(() => expect(screen.getByText('Fallback answer.')).toBeInTheDocument());
    expect(chatApi.sendChatMessage).toHaveBeenCalledWith('doc_9', 'Test question');
  });

  it('does not send an empty message', async () => {
    const user = userEvent.setup();
    render(<Chatbot documentId="doc_1" />);

    expect(screen.getByRole('button', { name: /send/i })).toBeDisabled();
    await user.click(screen.getByRole('button', { name: /send/i }));
    expect(chatApi.streamChatMessage).not.toHaveBeenCalled();
  });
});
