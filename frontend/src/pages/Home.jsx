import React from 'react';
import { Link } from 'react-router-dom';

const STEPS = [
  { to: '/upload', label: 'Upload', body: 'Drop in a 10-K, 10-Q, or earnings release. We parse and index it in the background.' },
  { to: '/chat', label: 'Chat', body: 'Ask questions in plain language and get answers grounded in the source pages.' },
  { to: '/compare', label: 'Compare', body: 'Line up two filings side by side and see what actually moved, and by how much.' },
];

export default function Home() {
  return (
    <div>
      <div className="max-w-2xl">
        <div className="axis-label mb-3">Financial document intelligence</div>
        <h1 className="font-display text-4xl md:text-5xl font-semibold leading-[1.1] tracking-tight">
          Read the filing.
          <br />
          Skip the skimming.
        </h1>
        <p className="mt-5 text-inkmuted leading-relaxed">
          Upload a financial report, ask it direct questions, and compare it against
          another period or company — with every answer traceable back to a page.
        </p>
      </div>

      <div className="axis-divider my-10" />

      <div className="grid sm:grid-cols-3 gap-6">
        {STEPS.map((step, i) => (
          <Link
            key={step.to}
            to={step.to}
            className="group block border border-rule rounded-sm px-5 py-5 bg-white/50 hover:border-sage transition-colors"
          >
            <div className="flex items-center gap-2 mb-3">
              <span className="font-mono text-xs text-sage-dark">0{i + 1}</span>
              <span className="axis-divider flex-1" />
            </div>
            <div className="font-display text-xl font-semibold mb-1.5 group-hover:text-sage-dark transition-colors">
              {step.label}
            </div>
            <p className="text-sm text-inkmuted leading-relaxed">{step.body}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}
