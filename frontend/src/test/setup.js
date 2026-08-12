import '@testing-library/jest-dom/vitest';
import { afterEach, beforeEach, vi } from 'vitest';
import { cleanup } from '@testing-library/react';

afterEach(() => {
  cleanup();
  localStorage.clear();
  vi.restoreAllMocks();
});

beforeEach(() => {
  // Most component tests don't hit real network; individual tests mock
  // the api/* modules directly. This is a safety net for anything that
  // doesn't, so a stray fetch fails loudly instead of hanging.
  if (!globalThis.fetch) {
    globalThis.fetch = vi.fn(() => Promise.reject(new Error('fetch not mocked in this test')));
  }
});
