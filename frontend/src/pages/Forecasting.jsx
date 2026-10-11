import React, { useState } from 'react'
import { useDataset } from '../api/DatasetContext.jsx'
import { datasetApi } from '../api/client.js'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

export default function Forecasting() {
  const { records, headers, datasetId } = useDataset()
  const numericHeaders = headers.filter(h => typeof records[0]?.[h] === 'number')
  const [dateCol, setDateCol] = useState(headers[0])
  const [valueCol, setValueCol] = useState(numericHeaders[0])
  const [periods, setPeriods] = useState(14)
  const [model, setModel] = useState('auto')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  if (records.length === 0) return <p>Upload a dataset first.</p>
  if (!datasetId) return <p>Upload this dataset to the platform before forecasting.</p>

  const run = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await datasetApi.forecast(datasetId, {
        records, date_column: dateCol, value_column: valueCol, periods, model,
      })
      setResult(res)
    } catch (e) {
      setError(e.response?.data?.detail || e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h2>Forecasting</h2>
      <div className="card">
        <label>Date column: </label>
        <select value={dateCol} onChange={e => setDateCol(e.target.value)} style={{ marginRight: 16 }}>
          {headers.map(h => <option key={h} value={h}>{h}</option>)}
        </select>
        <label>Value column: </label>
        <select value={valueCol} onChange={e => setValueCol(e.target.value)} style={{ marginRight: 16 }}>
          {numericHeaders.map(h => <option key={h} value={h}>{h}</option>)}
        </select>
        <label>Periods: </label>
        <input type="number" value={periods} min={1} max={365}
          onChange={e => setPeriods(Number(e.target.value))} style={{ width: 70, marginRight: 16 }} />
        <label>Model: </label>
        <select value={model} onChange={e => setModel(e.target.value)}>
          <option value="auto">Auto (rolling-origin backtest)</option>
          <option value="naive">Naive (last value)</option>
          <option value="seasonal_naive">Seasonal naive</option>
          <option value="holt">Holt's linear trend</option>
          <option value="arima">ARIMA</option>
          <option value="sarima">SARIMA</option>
          <option value="ensemble">Equal-weight ensemble</option>
        </select>
        <div style={{ marginTop: 16 }}>
          <button onClick={run} disabled={loading}>{loading ? 'Forecasting...' : 'Run forecast'}</button>
        </div>
        {error && <p style={{ color: '#e06c75' }}>{error}</p>}
      </div>

      {result && (
        <>
          <div className="card">
            <h3>Forecast — model used: {result.model_used}</h3>
            <div style={{ height: 300 }}>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={result.forecast}>
                  <CartesianGrid stroke="#262b3a" />
                  <XAxis dataKey="period" stroke="#a9adba" />
                  <YAxis stroke="#a9adba" />
                  <Tooltip contentStyle={{ background: '#171a23', border: '1px solid #262b3a' }} />
                  <Line type="monotone" dataKey="value" stroke="#7c9eff" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {result.meta_features && (
            <div className="card">
              <h3>How the model was chosen</h3>
              <p style={{ fontSize: 13 }}>
                Series: {result.meta_features.length} points, seasonal period {result.seasonal_period},
                seasonal strength {result.meta_features.seasonal_strength}, trend strength {result.meta_features.trend_strength}.
                Backtested {result.candidates_evaluated?.length} shortlisted candidates over {result.backtest_splits_used} rolling-origin splits;
                {result.selection_metric
                  ? ` the lowest average ${result.selection_metric} wins.`
                  : ` ${result.selection_message || 'No valid selection metric was available.'}`}
              </p>
            </div>
          )}

          {result.model_comparison && (
            <div className="card">
              <h3>Model comparison (rolling-origin backtest)</h3>
              <table>
                <thead><tr><th>Model</th><th>MAPE</th><th>RMSE</th><th>MASE</th></tr></thead>
                <tbody>
                  {Object.entries(result.model_comparison).map(([name, s]) => (
                    <tr key={name}>
                      <td>{name}{name === result.model_used ? ' ✓' : ''}</td>
                      <td>{s.mape != null ? `${s.mape}%` : '—'}</td>
                      <td>{s.rmse != null ? s.rmse : '—'}</td>
                      <td>{s.mase != null ? s.mase : '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}
    </div>
  )
}
