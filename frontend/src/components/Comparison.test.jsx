import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Comparison from '../components/Comparison.jsx';
import * as documentsApi from '../api/documents.js';

vi.mock('../api/documents.js');

const DOC_A = { document_id: 'a1', company_name: 'Acme Corp', report_date: '2025-Q1', status: 'completed' };
const DOC_B = { document_id: 'b2', company_name: 'Acme Corp', report_date: '2026-Q1', status: 'completed' };

describe('Comparison', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('shows a message when there are no completed documents', async () => {
    documentsApi.listDocuments.mockResolvedValue([]);
    render(<Comparison />);
    expect(await screen.findByText(/no processed documents yet/i)).toBeInTheDocument();
  });

  it('shows a message when only one completed document exists', async () => {
    documentsApi.listDocuments.mockResolvedValue([DOC_A]);
    render(<Comparison />);
    expect(await screen.findByText(/only one processed document so far/i)).toBeInTheDocument();
  });

  it('fetches metrics for both documents and flags large moves as insights', async () => {
    documentsApi.listDocuments.mockResolvedValue([DOC_A, DOC_B]);
    documentsApi.getDocumentMetrics.mockImplementation((id) => {
      if (id === 'a1') return Promise.resolve({ revenue: 100, net_income: 10, eps: 1.0 });
      if (id === 'b2') return Promise.resolve({ revenue: 130, net_income: 10.5, eps: 1.05 });
      return Promise.reject(new Error('unknown id'));
    });

    const user = userEvent.setup();
    render(<Comparison />);

    const [selectA, selectB] = await screen.findAllByRole('combobox');
    await user.selectOptions(selectA, 'a1');
    await user.selectOptions(selectB, 'b2');
    await user.click(screen.getByRole('button', { name: /^compare$/i }));

    await waitFor(() => expect(documentsApi.getDocumentMetrics).toHaveBeenCalledTimes(2));

    // Revenue moved 30% (>=15% threshold) -> should appear as an insight.
    expect(await screen.findByText(/revenue increased between the two periods/i)).toBeInTheDocument();
    // Net income moved 5% (<15%) -> should NOT appear as an insight.
    expect(screen.queryByText(/net income increased between the two periods/i)).not.toBeInTheDocument();
  });

  it('disables Compare until two different documents are selected', async () => {
    documentsApi.listDocuments.mockResolvedValue([DOC_A, DOC_B]);
    const user = userEvent.setup();
    render(<Comparison />);

    const compareButton = await screen.findByRole('button', { name: /^compare$/i });
    expect(compareButton).toBeDisabled();

    const [selectA, selectB] = screen.getAllByRole('combobox');
    await user.selectOptions(selectA, 'a1');
    await user.selectOptions(selectB, 'a1');

    expect(compareButton).toBeDisabled();
    expect(screen.getByText(/choose two different documents/i)).toBeInTheDocument();
  });
});
