import React, { useState } from 'react';
import { Routes, Route, NavLink } from 'react-router-dom';
import Home from './pages/Home.jsx';
import UploadPage from './pages/UploadPage.jsx';
import ChatPage from './pages/ChatPage.jsx';
import ComparePage from './pages/ComparePage.jsx';

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

export default function App() {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <div className="min-h-screen flex flex-col md:flex-row bg-paper">
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
        </nav>
      )}

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
          <p className="axis-label leading-relaxed">
            Session · local
            <br />
            v0.1.0
          </p>
        </div>
      </aside>

      <main className="flex-1 min-w-0">
        <div className="max-w-5xl mx-auto px-5 md:px-10 py-8 md:py-12">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/upload" element={<UploadPage />} />
            <Route path="/chat" element={<ChatPage />} />
            <Route path="/compare" element={<ComparePage />} />
          </Routes>
        </div>
      </main>
    </div>
  );
}
