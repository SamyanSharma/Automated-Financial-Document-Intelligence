import React, { useState } from 'react';
import { Routes, Route, NavLink, Navigate } from 'react-router-dom';
import Home from './pages/Home.jsx';
import UploadPage from './pages/UploadPage.jsx';
import ChatPage from './pages/ChatPage.jsx';
import ComparePage from './pages/ComparePage.jsx';
import LoginPage from './pages/LoginPage.jsx';
import RequireAuth from './components/RequireAuth.jsx';

const NAV_ITEMS = [
  { to: '/', label: 'Overview', end: true },
  { to: '/upload', label: 'Upload' },
  { to: '/chat', label: 'Chat' },
  { to: '/compare', label: 'Compare' },
];

function NavItem({ to, label, end, onClick }) {
  return (
    <NavLink
      to={to}
      end={end}
      onClick={onClick}
      className={({ isActive }) =>
        [
          'group flex items-center gap-3 py-2.5 font-body text-sm transition-colors',
          isActive ? 'text-ink' : 'text-inkmuted hover:text-ink',
        ].join(' ')
      }
    >
      {({ isActive }) => (
        <>
          {/* tick mark that "lights up" on the active route, echoing the axis-divider motif */}
          <span
            className={[
              'h-3 w-px shrink-0 transition-colors',
              isActive ? 'bg-sage h-4 w-0.5' : 'bg-rule',
            ].join(' ')}
          />
          {label}
        </>
      )}
    </NavLink>
  );
}

function AppShell({ menuOpen, setMenuOpen, onLogout }) {
  return (
    <div className="min-h-screen flex flex-col md:flex-row bg-paper">
      {/* Mobile top bar */}
      <header className="md:hidden flex items-center justify-between px-5 py-4 border-b border-rule bg-paper sticky top-0 z-20">
        <span className="font-display text-lg font-semibold tracking-tight">
          Ledger
        </span>
        <button
          aria-label="Toggle navigation"
          onClick={() => setMenuOpen((v) => !v)}
          className="font-mono text-xs uppercase tracking-widest border border-rule px-3 py-1.5 rounded-sm"
        >
          {menuOpen ? 'Close' : 'Menu'}
        </button>
      </header>
      {menuOpen && (
        <nav className="md:hidden px-5 pb-4 border-b border-rule bg-paper flex flex-col">
          {NAV_ITEMS.map((item) => (
            <NavItem key={item.to} {...item} onClick={() => setMenuOpen(false)} />
          ))}
          <button onClick={onLogout} className="text-left py-2.5 font-body text-sm text-rust">
            Sign out
          </button>
        </nav>
      )}

      {/* Desktop sidebar */}
      <aside className="hidden md:flex md:flex-col md:w-60 md:shrink-0 border-r border-rule px-6 py-8 sticky top-0 h-screen">
        <div className="mb-10">
          <div className="font-display text-2xl font-semibold tracking-tight leading-none">
            Ledger
          </div>
          <div className="axis-label mt-2">Financial document intelligence</div>
        </div>
        <nav className="flex flex-col gap-0.5">
          {NAV_ITEMS.map((item) => (
            <NavItem key={item.to} {...item} />
          ))}
        </nav>
        <div className="mt-auto">
          <div className="axis-divider mb-4" />
          <button
            onClick={onLogout}
            className="axis-label leading-relaxed hover:text-rust transition-colors text-left"
          >
            Sign out
          </button>
          <p className="axis-label leading-relaxed mt-2">v0.1.0</p>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 min-w-0">
        <div className="max-w-5xl mx-auto px-5 md:px-10 py-8 md:py-12">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/upload" element={<UploadPage />} />
            <Route path="/chat" element={<ChatPage />} />
            <Route path="/compare" element={<ComparePage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </div>
      </main>
    </div>
  );
}

export default function App() {
  const [menuOpen, setMenuOpen] = useState(false);
  const isAuthed = Boolean(localStorage.getItem('auth_token'));

  const handleLogout = () => {
    localStorage.removeItem('auth_token');
    window.location.assign('/login');
  };

  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/*"
        element={
          <RequireAuth isAuthed={isAuthed}>
            <AppShell menuOpen={menuOpen} setMenuOpen={setMenuOpen} onLogout={handleLogout} />
          </RequireAuth>
        }
      />
    </Routes>
  );
}
