import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import UploadForm from '../components/UploadForm.jsx';
import * as documentsApi from '../api/documents.js';

vi.mock('../api/documents.js');

function makePdfFile(name = 'report.pdf', sizeBytes = 1024) {
  const file = new File([new Uint8Array(sizeBytes)], name, { type: 'application/pdf' });
  return file;
}

describe('UploadForm', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('rejects non-PDF files before calling the API', async () => {
    const user = userEvent.setup();
    render(<UploadForm />);

    const input = document.querySelector('input[type="file"]');
    const badFile = new File(['not a pdf'], 'notes.txt', { type: 'text/plain' });

    await user.upload(input, badFile);

    expect(await screen.findByText(/only pdf files are supported/i)).toBeInTheDocument();
    expect(documentsApi.uploadDocument).not.toHaveBeenCalled();
  });

  it('rejects files over the 25MB limit', async () => {
    const user = userEvent.setup();
    render(<UploadForm />);

    const input = document.querySelector('input[type="file"]');
    const bigFile = makePdfFile('big.pdf', 26 * 1024 * 1024);

    await user.upload(input, bigFile);

    expect(await screen.findByText(/larger than the 25 MB limit/i)).toBeInTheDocument();
    expect(documentsApi.uploadDocument).not.toHaveBeenCalled();
  });

  it('uploads a valid PDF, polls status, and calls onComplete', async () => {
    documentsApi.uploadDocument.mockResolvedValue({ document_id: 42, status: 'processing' });
    documentsApi.pollDocumentStatus.mockResolvedValue({ status: 'completed' });

    const onComplete = vi.fn();
    const user = userEvent.setup();
    render(<UploadForm onComplete={onComplete} />);

    const input = document.querySelector('input[type="file"]');
    await user.upload(input, makePdfFile());

    const submitButton = screen.getByRole('button', { name: /upload & process/i });
    await user.click(submitButton);

    await waitFor(() => expect(onComplete).toHaveBeenCalledWith(42));
    expect(documentsApi.uploadDocument).toHaveBeenCalledTimes(1);
    expect(documentsApi.pollDocumentStatus).toHaveBeenCalledWith(42, expect.any(Object));
    expect(await screen.findByText(/document 42 is ready/i)).toBeInTheDocument();
  });

  it('shows an error and does not call onComplete when processing fails', async () => {
    documentsApi.uploadDocument.mockResolvedValue({ document_id: 7, status: 'processing' });
    documentsApi.pollDocumentStatus.mockResolvedValue({ status: 'failed' });

    const onComplete = vi.fn();
    const user = userEvent.setup();
    render(<UploadForm onComplete={onComplete} />);

    await user.upload(document.querySelector('input[type="file"]'), makePdfFile());
    await user.click(screen.getByRole('button', { name: /upload & process/i }));

    expect(await screen.findByText(/processing failed on the server/i)).toBeInTheDocument();
    expect(onComplete).not.toHaveBeenCalled();
  });

  it('surfaces a network/API error message', async () => {
    documentsApi.uploadDocument.mockRejectedValue(new Error('Network Error'));

    const user = userEvent.setup();
    render(<UploadForm />);

    await user.upload(document.querySelector('input[type="file"]'), makePdfFile());
    await user.click(screen.getByRole('button', { name: /upload & process/i }));

    expect(await screen.findByText('Network Error')).toBeInTheDocument();
  });

  it('reset clears the selected file and returns to idle', async () => {
    const user = userEvent.setup();
    render(<UploadForm />);

    await user.upload(document.querySelector('input[type="file"]'), makePdfFile('report.pdf'));
    expect(screen.getByText('report.pdf')).toBeInTheDocument();

    await user.click(screen.getByRole('button', { name: /reset/i }));

    expect(screen.queryByText('report.pdf')).not.toBeInTheDocument();
    expect(screen.getByRole('button', { name: /upload & process/i })).toBeDisabled();
  });
});
