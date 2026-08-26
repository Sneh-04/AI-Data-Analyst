import React, { useState } from 'react'
import { useDataset } from '../api/DatasetContext.jsx'
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

export default function Visualization() {
  const { records, headers } = useDataset()
  const numericHeaders = headers.filter(h => typeof records[0]?.[h] === 'number')
  const [xCol, setXCol] = useState(headers[0])
  const [yCol, setYCol] = useState(numericHeaders[0])
  const [chartType, setChartType] = useState('line')

  if (records.length === 0) return <p>Upload a dataset first.</p>

  const data = records.slice(0, 200) // cap for render performance in this scaffold

  return (
    <div>
      <h2>Visualization</h2>
      <div className="card">
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

      <div className="card" style={{ height: 360 }}>
        <ResponsiveContainer width="100%" height="100%">
          {chartType === 'line' ? (
            <LineChart data={data}>
              <CartesianGrid stroke="#262b3a" />
              <XAxis dataKey={xCol} stroke="#a9adba" hide={data.length > 30} />
              <YAxis stroke="#a9adba" />
              <Tooltip contentStyle={{ background: '#171a23', border: '1px solid #262b3a' }} />
              <Line type="monotone" dataKey={yCol} stroke="#7c9eff" dot={false} />
            </LineChart>
          ) : (
            <BarChart data={data}>
              <CartesianGrid stroke="#262b3a" />
              <XAxis dataKey={xCol} stroke="#a9adba" hide={data.length > 30} />
              <YAxis stroke="#a9adba" />
              <Tooltip contentStyle={{ background: '#171a23', border: '1px solid #262b3a' }} />
              <Bar dataKey={yCol} fill="#7c9eff" />
            </BarChart>
          )}
        </ResponsiveContainer>
      </div>
    </div>
  )
}
