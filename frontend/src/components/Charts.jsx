import React from 'react';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { formatCurrency, formatNumber } from '../utils/format.js';

const COLORS = ['#4F7A69', '#C99A3B', '#B5533C', '#10202E'];

export function MetricBarChart({ data, valueLabel = 'Value', currency = true, height = 280 }) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={data} margin={{ top: 8, right: 8, left: 8, bottom: 8 }}>
        <CartesianGrid strokeDasharray="2 6" stroke="#C7CDBF" vertical={false} />
        <XAxis
          dataKey="label"
          tick={{ fontFamily: 'IBM Plex Mono', fontSize: 11, fill: '#3C4C5A' }}
          axisLine={{ stroke: '#C7CDBF' }}
          tickLine={false}
        />
        <YAxis
          tick={{ fontFamily: 'IBM Plex Mono', fontSize: 11, fill: '#3C4C5A' }}
          axisLine={false}
          tickLine={false}
          tickFormatter={(v) => (currency ? formatCurrency(v) : formatNumber(v))}
        />
        <Tooltip
          formatter={(v) => [currency ? formatCurrency(v) : formatNumber(v), valueLabel]}
          contentStyle={{ fontFamily: 'Inter', fontSize: 13, border: '1px solid #C7CDBF', borderRadius: 2 }}
        />
        <Bar dataKey="value" fill="#4F7A69" radius={[2, 2, 0, 0]} maxBarSize={64} />
      </BarChart>
    </ResponsiveContainer>
  );
}

export function ComparisonBarChart({ data, seriesLabels = ['A', 'B'], height = 320 }) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={data} margin={{ top: 8, right: 8, left: 8, bottom: 8 }}>
        <CartesianGrid strokeDasharray="2 6" stroke="#C7CDBF" vertical={false} />
        <XAxis
          dataKey="metric"
          tick={{ fontFamily: 'IBM Plex Mono', fontSize: 11, fill: '#3C4C5A' }}
          axisLine={{ stroke: '#C7CDBF' }}
          tickLine={false}
        />
        <YAxis
          tick={{ fontFamily: 'IBM Plex Mono', fontSize: 11, fill: '#3C4C5A' }}
          axisLine={false}
          tickLine={false}
        />
        <Tooltip contentStyle={{ fontFamily: 'Inter', fontSize: 13, border: '1px solid #C7CDBF', borderRadius: 2 }} />
        <Legend wrapperStyle={{ fontFamily: 'Inter', fontSize: 12 }} />
        <Bar dataKey="a" name={seriesLabels[0]} fill={COLORS[0]} radius={[2, 2, 0, 0]} maxBarSize={40} />
        <Bar dataKey="b" name={seriesLabels[1]} fill={COLORS[1]} radius={[2, 2, 0, 0]} maxBarSize={40} />
      </BarChart>
    </ResponsiveContainer>
  );
}

export function TrendLineChart({ data, valueLabel = 'Value', height = 260 }) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={data} margin={{ top: 8, right: 8, left: 8, bottom: 8 }}>
        <CartesianGrid strokeDasharray="2 6" stroke="#C7CDBF" vertical={false} />
        <XAxis
          dataKey="period"
          tick={{ fontFamily: 'IBM Plex Mono', fontSize: 11, fill: '#3C4C5A' }}
          axisLine={{ stroke: '#C7CDBF' }}
          tickLine={false}
        />
        <YAxis
          tick={{ fontFamily: 'IBM Plex Mono', fontSize: 11, fill: '#3C4C5A' }}
          axisLine={false}
          tickLine={false}
        />
        <Tooltip
          formatter={(v) => [formatNumber(v), valueLabel]}
          contentStyle={{ fontFamily: 'Inter', fontSize: 13, border: '1px solid #C7CDBF', borderRadius: 2 }}
        />
        <Line type="monotone" dataKey="value" stroke="#4F7A69" strokeWidth={2} dot={{ r: 3 }} />
      </LineChart>
    </ResponsiveContainer>
  );
}
