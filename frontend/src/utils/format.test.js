import { describe, it, expect } from 'vitest';
import {
  formatCurrency,
  formatNumber,
  formatPercent,
  formatDelta,
  formatReportDate,
  formatFileSize,
  truncateFilename,
} from '../utils/format.js';

describe('formatCurrency', () => {
  it('formats large numbers compactly', () => {
    expect(formatCurrency(1234567)).toBe('$1.23M');
  });
  it('returns an em dash for null/undefined/NaN', () => {
    expect(formatCurrency(null)).toBe('—');
    expect(formatCurrency(undefined)).toBe('—');
    expect(formatCurrency(NaN)).toBe('—');
  });
});

describe('formatNumber', () => {
  it('adds thousands separators', () => {
    expect(formatNumber(1234567)).toBe('1,234,567');
  });
  it('respects the decimals option', () => {
    expect(formatNumber(12.3456, { decimals: 2 })).toBe('12.35');
  });
});

describe('formatPercent', () => {
  it('converts a ratio to a percent string', () => {
    expect(formatPercent(0.083)).toBe('8.3%');
  });
});

describe('formatDelta', () => {
  it('adds a plus sign for positive deltas', () => {
    expect(formatDelta(0.042)).toBe('+4.2%');
  });
  it('keeps the minus sign for negative deltas', () => {
    expect(formatDelta(-0.018)).toBe('-1.8%');
  });
  it('handles a zero delta without a sign', () => {
    expect(formatDelta(0)).toBe('0.0%');
  });
});

describe('formatReportDate', () => {
  it('formats an ISO date as a readable string', () => {
    expect(formatReportDate('2026-03-15')).toContain('2026');
  });
  it('returns the original string for an invalid date', () => {
    expect(formatReportDate('not-a-date')).toBe('not-a-date');
  });
  it('returns an em dash for a missing date', () => {
    expect(formatReportDate(null)).toBe('—');
  });
});

describe('formatFileSize', () => {
  it('formats bytes into KB/MB', () => {
    expect(formatFileSize(1024)).toBe('1.0 KB');
    expect(formatFileSize(1048576)).toBe('1.0 MB');
  });
  it('formats small byte counts without decimals', () => {
    expect(formatFileSize(512)).toBe('512 B');
  });
});

describe('truncateFilename', () => {
  it('leaves short names untouched', () => {
    expect(truncateFilename('report.pdf')).toBe('report.pdf');
  });
  it('truncates long names while preserving the extension', () => {
    const long = 'a-very-long-quarterly-earnings-report-file-name.pdf';
    const result = truncateFilename(long, 20);
    expect(result.endsWith('.pdf')).toBe(true);
    expect(result.length).toBeLessThanOrEqual(20 + 1); // "..." adds a little slack
  });
});
