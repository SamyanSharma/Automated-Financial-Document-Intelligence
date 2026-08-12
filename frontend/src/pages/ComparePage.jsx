import React from 'react';
import Comparison from '../components/Comparison.jsx';

export default function ComparePage() {
  return (
    <div>
      <div className="axis-label mb-2">Step 03</div>
      <h1 className="font-display text-3xl font-semibold mb-6">Compare two documents</h1>
      <Comparison />
    </div>
  );
}
