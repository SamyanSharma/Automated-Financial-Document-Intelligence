import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import LoginPage from '../pages/LoginPage.jsx';
import * as authApi from '../api/auth.js';

vi.mock('../api/auth.js');

function renderLoginPage(initialEntries = ['/login']) {
  return render(
    <MemoryRouter initialEntries={initialEntries}>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/" element={<div>Home page</div>} />
        <Route path="/upload" element={<div>Upload page</div>} />
      </Routes>
    </MemoryRouter>
  );
}

describe('LoginPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  it('stores the token and navigates home on successful login', async () => {
    authApi.login.mockResolvedValue({ access_token: 'tok_abc123', token_type: 'bearer' });
    const user = userEvent.setup();
    renderLoginPage();

    await user.type(screen.getByLabelText(/email/i), 'analyst@example.com');
    await user.type(screen.getByLabelText(/password/i), 'hunter2');
    await user.click(screen.getByRole('button', { name: /sign in/i }));

    await waitFor(() => expect(screen.getByText('Home page')).toBeInTheDocument());
    expect(localStorage.getItem('auth_token')).toBe('tok_abc123');
    expect(authApi.login).toHaveBeenCalledWith('analyst@example.com', 'hunter2');
  });

  it('shows an inline error and does not store a token on failure', async () => {
    authApi.login.mockRejectedValue(new Error('Invalid credentials'));
    const user = userEvent.setup();
    renderLoginPage();

    await user.type(screen.getByLabelText(/email/i), 'analyst@example.com');
    await user.type(screen.getByLabelText(/password/i), 'wrong');
    await user.click(screen.getByRole('button', { name: /sign in/i }));

    expect(await screen.findByText('Invalid credentials')).toBeInTheDocument();
    expect(localStorage.getItem('auth_token')).toBeNull();
  });

  it('errors clearly if the server response has no access_token', async () => {
    authApi.login.mockResolvedValue({});
    const user = userEvent.setup();
    renderLoginPage();

    await user.type(screen.getByLabelText(/email/i), 'a@b.com');
    await user.type(screen.getByLabelText(/password/i), 'pw');
    await user.click(screen.getByRole('button', { name: /sign in/i }));

    expect(await screen.findByText(/no access token returned/i)).toBeInTheDocument();
  });
});
