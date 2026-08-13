import '@testing-library/jest-dom/vitest';
import { afterEach, beforeEach, vi } from 'vitest';
import { cleanup } from '@testing-library/react';

afterEach(() => {
  cleanup();
  localStorage.clear();
  vi.restoreAllMocks();
});

beforeEach(() => {
  if (!globalThis.fetch) {
    globalThis.fetch = vi.fn(() => Promise.reject(new Error('fetch not mocked in this test')));
  }
});
