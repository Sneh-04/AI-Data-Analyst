import React, { useEffect, useMemo, useState } from 'react'
import { useDataset } from '../api/DatasetContext.jsx'
import { datasetApi } from '../api/client.js'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import EmptyState from '../components/EmptyState.jsx'
import PageHeading from '../components/PageHeading.jsx'
import { getDefaultForecastColumns } from '../utils/forecastDefaults.js'

export default function Forecasting() {
  const { records, headers, datasetId } = useDataset()
  const { dateColumn, valueColumn, numericHeaders, validDateColumns } = useMemo(
    () => getDefaultForecastColumns(headers, records),
    [headers, records],
  )
  const defaultDateColumn = dateColumn
  const defaultValueColumn = valueColumn
  const [dateCol, setDateCol] = useState(defaultDateColumn)
  const [valueCol, setValueCol] = useState(defaultValueColumn)
  const [periods, setPeriods] = useState(14)
  const [model, setModel] = useState('auto')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    const nextDate = validDateColumns[0] || headers.find(h => /date|time|timestamp/i.test(h)) || headers[0] || ''
    const nextValue = numericHeaders.find(h => h !== nextDate) || numericHeaders[0] || ''
    if (nextDate && dateCol !== nextDate) setDateCol(nextDate)
    if (nextValue && valueCol !== nextValue) setValueCol(nextValue)
  }, [dateCol, headers, numericHeaders, validDateColumns, valueCol])

  if (records.length === 0) return <EmptyState title="Forecast with your data" description="Upload a dataset with a time column and a numeric measure to get started." />
  if (!datasetId) return <EmptyState title="Save your dataset to continue" description="Upload this dataset to the platform before forecasting." />
  if (!validDateColumns.length || numericHeaders.length === 0) {
    return (
      <div>
        <PageHeading eyebrow="LOOK AHEAD" title="Forecasting"
          description="Select a date, measure, and model to explore what may come next." />
        <p className="alert alert-info" role="status">
          This dataset needs at least one date-like column and one numeric measure to build a forecast.
        </p>
      </div>
    )
  }

  const run = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await datasetApi.forecast(datasetId, {
        date_column: dateCol, value_column: valueCol, periods, model,
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
      <PageHeading eyebrow="LOOK AHEAD" title="Forecasting"
        description="Select a date, measure, and model to explore what may come next." />
      <div className="card control-panel">
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
        <div className="control-action">
          <button onClick={run} disabled={loading} data-loading={loading}>{loading ? 'Forecasting...' : 'Run forecast'}</button>
        </div>
        {error && <p className="alert alert-error" role="alert">{error}</p>}
      </div>

      {result && (
        <>
          <div className="card">
            <h3>Forecast — model used: {result.model_used}</h3>
            <div style={{ height: 300 }}>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={result.forecast}>
                  <CartesianGrid stroke="#e9edf5" strokeDasharray="4 4" />
                  <XAxis dataKey="period" stroke="#8995aa" tickLine={false} axisLine={false} />
                  <YAxis stroke="#8995aa" tickLine={false} axisLine={false} />
                  <Tooltip contentStyle={{ background: '#fff', border: '1px solid #e8ecf5', borderRadius: 10, boxShadow: '0 8px 24px rgba(32, 48, 82, .12)' }} />
                  <Line type="monotone" dataKey="value" stroke="#4361ee" strokeWidth={2.5} activeDot={{ r: 5 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {result.meta_features && (
            <div className="card">
              <h3>How the model was chosen</h3>
              <p className="muted-copy">
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
              <div className="table-wrap">
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
            </div>
          )}
        </>
      )}
    </div>
  )
}
