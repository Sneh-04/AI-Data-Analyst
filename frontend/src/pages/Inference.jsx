import React, { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  CartesianGrid,
  ErrorBar,
  Line,
  LineChart,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { useDataset } from '../api/DatasetContext.jsx'
import { datasetApi } from '../api/client.js'
import EmptyState from '../components/EmptyState.jsx'
import PageHeading from '../components/PageHeading.jsx'
import { serializeInferenceResult } from '../utils/inferenceCsv.js'

const SEED = 42
const SENSITIVITY_DELTAS = [-1, -0.5, 0, 0.5, 1]
const METHOD_INFO = {
  proper: 'Proper: bootstrap-resamples rows to include model-estimation uncertainty.',
  improper: 'Improper: skips row resampling and can understate imputation uncertainty.',
}
const METHOD_COLORS = {
  naive: '#9aa5b8',
  improper: '#8a63d2',
  proper: '#4361ee',
}

function isMissing(value) {
  return value == null || (typeof value === 'string' && value.trim() === '')
}

function numericValue(value) {
  if (isMissing(value) || typeof value === 'boolean') return null
  const parsed = Number(value)
  return Number.isFinite(parsed) ? parsed : null
}

function formatNumber(value, digits = 3) {
  return typeof value === 'number' && Number.isFinite(value)
    ? value.toLocaleString(undefined, { maximumFractionDigits: digits })
    : '—'
}

function confidenceInterval(row) {
  if (
    typeof row?.ci_lower !== 'number' ||
    !Number.isFinite(row.ci_lower) ||
    typeof row?.ci_upper !== 'number' ||
    !Number.isFinite(row.ci_upper)
  ) return 'Unavailable'
  return `[${formatNumber(row.ci_lower)}, ${formatNumber(row.ci_upper)}]`
}

function resultAtDelta(response, delta) {
  const result = response?.results?.find(item => item.delta === delta)
  if (!result) {
    throw new Error(`The inference response did not include a result for delta ${delta}.`)
  }
  return result
}

function errorMessage(error) {
  return error.response?.data?.detail || error.response?.data?.message || error.message
}

export default function Inference() {
  const { records, headers, datasetId } = useDataset()
  const numericHeaders = useMemo(() => headers.filter(header => {
    const values = records.map(record => record[header]).filter(value => !isMissing(value))
    return values.length > 0 && values.every(value => numericValue(value) !== null)
  }), [headers, records])
  const [target, setTarget] = useState('')
  const [estimand, setEstimand] = useState('mean')
  const [predictor, setPredictor] = useState('')
  const [method, setMethod] = useState('proper')
  const [m, setM] = useState(20)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!numericHeaders.includes(target)) setTarget(numericHeaders[0] || '')
    if (!numericHeaders.includes(predictor) || predictor === target) {
      setPredictor(numericHeaders.find(header => header !== target) || '')
    }
  }, [numericHeaders, predictor, target])

  const targetMissingFraction = target && records.length > 0
    ? records.filter(record => isMissing(record[target])).length / records.length
    : 0
  const availablePredictors = numericHeaders.filter(header => header !== target)

  if (records.length === 0) {
    return <EmptyState
      title="Load a dataset for inference"
      description="Upload a dataset to estimate means or regression slopes with imputation-aware intervals."
    />
  }

  if (!datasetId) {
    return (
      <section className="empty-state">
        <p className="eyebrow">YOUR WORKSPACE</p>
        <h2>Upload this dataset to continue</h2>
        <p>Save the loaded dataset to the platform before running inference.</p>
        <Link className="button-link" to="/">Upload a dataset <span aria-hidden="true">→</span></Link>
      </section>
    )
  }

  const run = async () => {
    setLoading(true)
    setError('')
    setResult(null)
    const payload = {
      target_column: target,
      estimand,
      ...(estimand === 'ols_slope' ? { predictor_column: predictor } : {}),
      m,
      seed: SEED,
    }

    try {
      const [properResponse, improperResponse] = await Promise.all([
        datasetApi.inference(datasetId, {
          ...payload,
          method: 'proper',
          deltas: SENSITIVITY_DELTAS,
        }),
        datasetApi.inference(datasetId, {
          ...payload,
          method: 'improper',
          deltas: [0],
        }),
      ])
      const proper = resultAtDelta(properResponse, 0)
      const improper = resultAtDelta(improperResponse, 0)
      if (!properResponse.naive_single_imputation) {
        throw new Error('The inference response did not include the naive single-imputation result.')
      }
      const sensitivity = SENSITIVITY_DELTAS.map(delta => resultAtDelta(properResponse, delta))
      const warnings = [...new Set([
        ...(properResponse.warnings || []),
        ...(improperResponse.warnings || []),
      ])]
      setResult({
        proper,
        improper,
        naive: properResponse.naive_single_imputation,
        sensitivity,
        missingFraction: properResponse.missing_fraction,
        rowsUsed: properResponse.n_rows_used,
        subsampled: properResponse.subsampled,
        methodNote: properResponse.method_note,
        settings: {
          target_column: target,
          estimand,
          predictor_column: estimand === 'ols_slope' ? predictor : '',
          selected_method: method,
          m,
          seed: SEED,
        },
        warnings,
      })
    } catch (requestError) {
      setError(errorMessage(requestError))
    } finally {
      setLoading(false)
    }
  }

  if (numericHeaders.length === 0) {
    return (
      <div>
        <PageHeading eyebrow="INFERENCE" title="Inference"
          description="Estimate means or regression slopes with imputation-aware uncertainty." />
        <p className="alert alert-info" role="status">
          This dataset has no columns with numeric values available for inference.
        </p>
      </div>
    )
  }

  const inferenceRows = result ? [
    { key: 'naive', label: 'Naive single imputation', detail: 'not valid for inference', values: result.naive },
    { key: 'improper', label: 'Improper', detail: '', values: result.improper },
    { key: 'proper', label: 'Proper', detail: '', values: result.proper },
  ] : []
  const forestRows = inferenceRows
    .filter(row => typeof row.values?.estimate === 'number' && Number.isFinite(row.values.estimate))
    .map(row => ({
      ...row,
      estimate: row.values.estimate,
      interval: [
        typeof row.values.ci_lower === 'number' ? Math.max(0, row.values.estimate - row.values.ci_lower) : 0,
        typeof row.values.ci_upper === 'number' ? Math.max(0, row.values.ci_upper - row.values.estimate) : 0,
      ],
    }))
  const sensitivityRows = result?.sensitivity.map(item => ({
    ...item,
    interval: [
      typeof item.ci_lower === 'number' ? Math.max(0, item.estimate - item.ci_lower) : 0,
      typeof item.ci_upper === 'number' ? Math.max(0, item.ci_upper - item.estimate) : 0,
    ],
  })) || []
  const canRun = Boolean(target) && (estimand !== 'ols_slope' || Boolean(predictor))

  const downloadResults = () => {
    const csv = serializeInferenceResult(result)
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `inference-${datasetId}-${new Date().toISOString().slice(0, 10)}.csv`
    link.click()
    window.setTimeout(() => URL.revokeObjectURL(url), 0)
  }

  return (
    <div className="inference-page">
      <PageHeading eyebrow="IMPUTATION-AWARE ANALYSIS" title="Inference"
        description="Compare naive, improper, and proper uncertainty estimates for a numeric estimand." />

      <section className="card inference-controls" aria-label="Inference controls">
        <label>
          Target numeric column
          <select value={target} onChange={event => setTarget(event.target.value)}>
            {numericHeaders.map(header => <option key={header} value={header}>{header}</option>)}
          </select>
          <span className="control-hint">{(targetMissingFraction * 100).toFixed(1)}% missing</span>
        </label>

        <label>
          Estimand
          <select value={estimand} onChange={event => setEstimand(event.target.value)}>
            <option value="mean">Mean</option>
            <option value="ols_slope">OLS slope</option>
          </select>
        </label>

        {estimand === 'ols_slope' && (
          <label>
            Predictor
            <select value={predictor} onChange={event => setPredictor(event.target.value)}
              disabled={availablePredictors.length === 0}>
              {availablePredictors.map(header => <option key={header} value={header}>{header}</option>)}
            </select>
            {availablePredictors.length === 0 && <span className="control-hint">Add another numeric column for an OLS slope.</span>}
          </label>
        )}

        <fieldset className="method-selector">
          <legend>Imputation method</legend>
          <div className="method-toggle" role="group" aria-label="Highlight an imputation method">
            {['proper', 'improper'].map(option => (
              <button key={option} type="button" className={method === option ? 'is-selected' : ''}
                aria-pressed={method === option} onClick={() => setMethod(option)}>
                {option === 'proper' ? 'Proper' : 'Improper'}
              </button>
            ))}
          </div>
          <div className="method-explanations">
            <p className={method === 'proper' ? 'is-selected' : ''}>{METHOD_INFO.proper}</p>
            <p className={method === 'improper' ? 'is-selected' : ''}>{METHOD_INFO.improper}</p>
          </div>
          <p className="control-hint">Both methods run for comparison; the selection highlights a row in the results.</p>
        </fieldset>

        <label className="imputation-count">
          Number of imputations (m): <strong>{m}</strong>
          <input type="range" min="2" max="50" value={m}
            onChange={event => setM(Number(event.target.value))}
            aria-label="Number of imputations" />
          <span className="range-limits"><span>2</span><span>50</span></span>
        </label>

        <div className="inference-run">
          <button onClick={run} disabled={loading || !canRun} data-loading={loading}>
            {loading ? 'Running inference...' : 'Run inference'}
          </button>
          {loading && <span className="loading-inline" role="status">Running proper and improper analyses with the same seed…</span>}
        </div>
        {error && <p className="alert alert-error" role="alert">{error}</p>}
      </section>

      <p className="alert alert-info inference-caveat">
        Intervals assume the imputation model is appropriate. Validity is not guaranteed.
      </p>
      <p className="alert alert-info">
        Inference results are temporary and are not saved to your account. Download the results CSV
        before leaving this page if you need to keep a copy.
      </p>

      {result && (
        <>
          <section className="card">
            <h3>Keep a copy</h3>
            <p className="muted-copy">
              These results exist only in this page session. Download them locally to retain a copy.
            </p>
            <button type="button" onClick={downloadResults}>Download results CSV</button>
          </section>

          {result.warnings.length > 0 && (
            <section className="alert alert-warning inference-warnings" role="status" aria-live="polite">
              <strong>Warnings</strong>
              <ul>{result.warnings.map(warning => <li key={warning}>{warning}</li>)}</ul>
            </section>
          )}

          <section className="card">
            <h3>Estimate intervals</h3>
            <div className="inference-chart">
              <ResponsiveContainer width="100%" height="100%">
                <ScatterChart margin={{ top: 12, right: 24, bottom: 8, left: 18 }}>
                  <CartesianGrid stroke="#e9edf5" strokeDasharray="4 4" horizontal={false} />
                  <XAxis type="number" dataKey="estimate" name="Estimate" stroke="#8995aa"
                    tickLine={false} axisLine={false} />
                  <YAxis type="category" dataKey="label" width={190} stroke="#8995aa"
                    tickLine={false} axisLine={false} />
                  <Tooltip formatter={(value, name) => [formatNumber(value), name]}
                    contentStyle={{ background: '#fff', border: '1px solid #e8ecf5', borderRadius: 10 }} />
                  {forestRows.map(row => (
                    <Scatter key={row.key} name={row.label} data={[row]}
                      fill={METHOD_COLORS[row.key]} shape="circle">
                      <ErrorBar dataKey="interval" direction="x" width={8} strokeWidth={2} />
                    </Scatter>
                  ))}
                </ScatterChart>
              </ResponsiveContainer>
            </div>
          </section>

          <section className="card">
            <h3>Inference summary</h3>
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Method</th><th>Estimate</th><th>95% CI</th><th>SE</th>
                    <th>df</th><th>Lambda</th><th>Missing fraction</th>
                    <th>Rows used</th><th>Subsampled</th>
                  </tr>
                </thead>
                <tbody>
                  {inferenceRows.map(row => (
                    <tr key={row.key} className={method === row.key ? 'is-highlighted' : ''}>
                      <td>{row.label}{row.detail && <span className="not-inferential"> ({row.detail})</span>}</td>
                      <td>{formatNumber(row.values.estimate)}</td>
                      <td>{confidenceInterval(row.values)}</td>
                      <td>{formatNumber(row.values.standard_error)}</td>
                      <td>{formatNumber(row.values.degrees_of_freedom)}</td>
                      <td>{formatNumber(row.values.lambda)}</td>
                      <td>{typeof result.missingFraction === 'number' ? `${(result.missingFraction * 100).toFixed(1)}%` : '—'}</td>
                      <td>{formatNumber(result.rowsUsed, 0)}</td>
                      <td>{result.subsampled ? 'Yes' : 'No'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

          <section className="card">
            <h3>MNAR sensitivity analysis</h3>
            <p className="muted-copy">
              Delta shifts imputed target values by this many observed standard deviations.
              This does not identify the mechanism or remove MNAR bias.
            </p>
            <div className="inference-chart sensitivity-chart">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={sensitivityRows} margin={{ top: 12, right: 22, bottom: 8, left: 10 }}>
                  <CartesianGrid stroke="#e9edf5" strokeDasharray="4 4" />
                  <XAxis type="number" dataKey="delta" ticks={SENSITIVITY_DELTAS}
                    label={{ value: 'Delta (SD units)', position: 'insideBottom', offset: -3 }}
                    stroke="#8995aa" tickLine={false} axisLine={false} />
                  <YAxis type="number" dataKey="estimate" stroke="#8995aa"
                    tickLine={false} axisLine={false} />
                  <Tooltip formatter={(value, name) => [formatNumber(value), name]}
                    labelFormatter={value => `Delta: ${value} SD`}
                    contentStyle={{ background: '#fff', border: '1px solid #e8ecf5', borderRadius: 10 }} />
                  <Line type="monotone" dataKey="estimate" name="Proper estimate"
                    stroke={METHOD_COLORS.proper} strokeWidth={2.5}
                    activeDot={{ r: 5 }} dot={{ r: 4 }}>
                    <ErrorBar dataKey="interval" direction="y" width={7} strokeWidth={1.5} />
                  </Line>
                </LineChart>
              </ResponsiveContainer>
            </div>
          </section>
        </>
      )}
    </div>
  )
}
