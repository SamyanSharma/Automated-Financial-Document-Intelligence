import React from 'react';
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import RequireAuth from '../components/RequireAuth.jsx';

function renderGuarded(isAuthed) {
  return render(
    <MemoryRouter initialEntries={['/upload']}>
      <Routes>
        <Route path="/login" element={<div>Login page</div>} />
        <Route
          path="/upload"
          element={
            <RequireAuth isAuthed={isAuthed}>
              <div>Protected upload page</div>
            </RequireAuth>
          }
        />
      </Routes>
    </MemoryRouter>
  );
}

describe('RequireAuth', () => {
  it('renders the protected content when authenticated', () => {
    renderGuarded(true);
    expect(screen.getByText('Protected upload page')).toBeInTheDocument();
  });

  it('redirects to /login when not authenticated', () => {
    renderGuarded(false);
    expect(screen.getByText('Login page')).toBeInTheDocument();
    expect(screen.queryByText('Protected upload page')).not.toBeInTheDocument();
  });
});
