import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { login } from '../api/auth.js';

/**
 * Minimal login screen. Posts credentials to POST /api/v1/auth/login,
 * expects { access_token } back, and stores it for api/client.js's
 * request interceptor to pick up on every subsequent call.
 */
export default function LoginPage({ onLogin }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  const redirectTo = location.state?.from?.pathname || '/';

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      const data = await login(email, password);
      if (!data?.access_token) {
        throw new Error('No access token returned by the server.');
      }
      localStorage.setItem('auth_token', data.access_token);
      onLogin?.(data.access_token);
      navigate(redirectTo, { replace: true });
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-paper px-5">
      <form onSubmit={handleSubmit} className="w-full max-w-sm">
        <div className="font-display text-2xl font-semibold tracking-tight mb-1">
          Ledger
        </div>
        <div className="axis-label mb-8">Sign in to continue</div>

        <label className="field-label" htmlFor="email">
          Email
        </label>
        <input
          id="email"
          type="email"
          required
          autoComplete="username"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full bg-white/60 border border-rule rounded-sm px-3 py-2 text-sm font-body mb-4 focus:border-sage outline-none"
        />

        <label className="field-label" htmlFor="password">
          Password
        </label>
        <input
          id="password"
          type="password"
          required
          autoComplete="current-password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full bg-white/60 border border-rule rounded-sm px-3 py-2 text-sm font-body mb-2 focus:border-sage outline-none"
        />

        {error && (
          <p className="mt-2 text-sm text-rust" role="alert">
            {error}
          </p>
        )}

        <button type="submit" className="btn-primary w-full justify-center mt-6" disabled={submitting}>
          {submitting ? 'Signing in…' : 'Sign in'}
        </button>
      </form>
    </div>
  );
}
