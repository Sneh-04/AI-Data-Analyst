import React, { useState } from 'react'
import { useDataset } from '../api/DatasetContext.jsx'
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import EmptyState from '../components/EmptyState.jsx'
import PageHeading from '../components/PageHeading.jsx'

export default function Visualization() {
  const { records, headers } = useDataset()
  const numericHeaders = headers.filter(h => typeof records[0]?.[h] === 'number')
  const [xCol, setXCol] = useState(headers[0])
  const [yCol, setYCol] = useState(numericHeaders[0])
  const [chartType, setChartType] = useState('line')

  if (records.length === 0) return <EmptyState title="Visualize your data" description="Upload a dataset to create charts from the columns that matter to you." />

  const data = records.slice(0, 200) // cap for render performance in this scaffold

  return (
    <div>
      <PageHeading eyebrow="EXPLORE PATTERNS" title="Visualization"
        description="Build a quick chart by choosing the columns and view that work for your question." />
      <div className="card control-panel">
        <label>X axis: </label>
        <select value={xCol} onChange={e => setXCol(e.target.value)} style={{ marginRight: 16 }}>
          {headers.map(h => <option key={h} value={h}>{h}</option>)}
        </select>
        <label>Y axis: </label>
        <select value={yCol} onChange={e => setYCol(e.target.value)} style={{ marginRight: 16 }}>
          {numericHeaders.map(h => <option key={h} value={h}>{h}</option>)}
        </select>
        <label>Chart: </label>
        <select value={chartType} onChange={e => setChartType(e.target.value)}>
          <option value="line">Line</option>
          <option value="bar">Bar</option>
        </select>
      </div>

      <div className="card chart-card" style={{ height: 360 }}>
        <ResponsiveContainer width="100%" height="100%">
          {chartType === 'line' ? (
            <LineChart data={data}>
              <CartesianGrid stroke="#e9edf5" strokeDasharray="4 4" />
              <XAxis dataKey={xCol} stroke="#8995aa" hide={data.length > 30} tickLine={false} axisLine={false} />
              <YAxis stroke="#8995aa" tickLine={false} axisLine={false} />
              <Tooltip contentStyle={{ background: '#fff', border: '1px solid #e8ecf5', borderRadius: 10, boxShadow: '0 8px 24px rgba(32, 48, 82, .12)' }} />
              <Line type="monotone" dataKey={yCol} stroke="#4361ee" strokeWidth={2.5} dot={false} activeDot={{ r: 5 }} />
            </LineChart>
          ) : (
            <BarChart data={data}>
              <CartesianGrid stroke="#e9edf5" strokeDasharray="4 4" />
              <XAxis dataKey={xCol} stroke="#8995aa" hide={data.length > 30} tickLine={false} axisLine={false} />
              <YAxis stroke="#8995aa" tickLine={false} axisLine={false} />
              <Tooltip contentStyle={{ background: '#fff', border: '1px solid #e8ecf5', borderRadius: 10, boxShadow: '0 8px 24px rgba(32, 48, 82, .12)' }} />
              <Bar dataKey={yCol} fill="#7950f2" radius={[5, 5, 0, 0]} />
            </BarChart>
          )}
        </ResponsiveContainer>
      </div>
    </div>
  )
}
