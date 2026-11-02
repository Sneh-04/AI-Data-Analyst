import React, { useEffect, useMemo, useState } from 'react'
import {
  CartesianGrid,
  ComposedChart,
  ErrorBar,
  Line,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import api from '../api/client.js'
import PageHeading from '../components/PageHeading.jsx'

const METHOD_LABELS = {
  median: 'Median',
  knn: 'KNN',
  mice_improper: 'MICE improper',
  mice_proper: 'MICE proper',
}
const METHOD_COLORS = {
  median: '#9aa5b8',
  knn: '#20a98b',
  mice_improper: '#8a63d2',
  mice_proper: '#4361ee',
}
const MECHANISM_LABELS = {
  MCAR: 'MCAR',
  MAR: 'MAR',
  MNAR: 'MNAR',
}
const ESTIMAND_LABELS = {
  mean: 'Mean',
  ols_slope: 'OLS slope',
}

function percentage(value) {
  return `${(value * 100).toFixed(1)}%`
}

function dimensionLabel(value) {
  return Number.isInteger(value) ? String(value) : String(value)
}

function keyedChartData(rows, xKey, methods) {
  const grouped = new Map()
  rows.forEach(row => {
    const key = row[xKey]
    if (!grouped.has(key)) grouped.set(key, { [xKey]: key })
    const point = grouped.get(key)
    point[`coverage_${row.method}`] = row.coverage
    point[`mc_se_${row.method}`] = row.mc_se
  })
  return [...grouped.values()].sort((left, right) => left[xKey] - right[xKey])
    .map(point => {
      methods.forEach(method => {
        if (point[`mc_se_${method}`] == null) point[`mc_se_${method}`] = 0
      })
      return point
    })
}

function MethodLines({ methods }) {
  return methods.map(method => (
    <Line
      key={method}
      type="monotone"
      dataKey={`coverage_${method}`}
      name={METHOD_LABELS[method] || method}
      stroke={METHOD_COLORS[method] || '#4361ee'}
      strokeWidth={2}
      connectNulls
      dot={{ r: 3 }}
      activeDot={{ r: 5 }}
      isAnimationActive={false}
    >
      <ErrorBar dataKey={`mc_se_${method}`} direction="y" width={5} strokeWidth={1.3} />
    </Line>
  ))
}

function CoverageChart({ title, rows, xKey, methods, nominalCoverage, coverageDomain, xLabel }) {
  const chartData = keyedChartData(rows, xKey, methods)
  return (
    <section className="card research-chart-card">
      <h3>{title}</h3>
      {chartData.length === 0 ? (
        <p className="muted-copy">No coverage results for this selection.</p>
      ) : (
        <div className="research-chart">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={chartData} margin={{ top: 10, right: 12, bottom: 20, left: 0 }}>
              <CartesianGrid stroke="#e9edf5" strokeDasharray="4 4" />
              <XAxis
                type="number"
                dataKey={xKey}
                domain={['dataMin', 'dataMax']}
                tickFormatter={xKey === 'mask_rate' ? percentage : dimensionLabel}
                label={{ value: xLabel, position: 'insideBottom', offset: -9 }}
                stroke="#8995aa"
                tickLine={false}
                axisLine={false}
              />
              <YAxis
                type="number"
                domain={coverageDomain}
                tickFormatter={percentage}
                stroke="#8995aa"
                tickLine={false}
                axisLine={false}
                width={48}
              />
              <Tooltip
                formatter={(value, name) => [
                  percentage(value),
                  name.startsWith('mc_se_') ? `MC SE (${METHOD_LABELS[name.slice(6)] || name.slice(6)})` : name,
                ]}
                labelFormatter={value => `${xLabel}: ${xKey === 'mask_rate' ? percentage(value) : dimensionLabel(value)}`}
                contentStyle={{ background: '#fff', border: '1px solid #e8ecf5', borderRadius: 10 }}
              />
              <ReferenceLine
                y={nominalCoverage}
                stroke="#d15d5d"
                strokeDasharray="5 4"
                label={{ value: `Nominal ${percentage(nominalCoverage)}`, fill: '#ad5353', fontSize: 10 }}
              />
              <MethodLines methods={methods} />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      )}
      <p className="research-chart-note">Bars show Monte Carlo standard errors.</p>
    </section>
  )
}

export default function Research() {
  const [summary, setSummary] = useState(null)
  const [error, setError] = useState('')
  const [imputationCount, setImputationCount] = useState('')
  const [delta, setDelta] = useState('')
  const [mnarEstimand, setMnarEstimand] = useState('')
  const [mnarRate, setMnarRate] = useState('')
  const [mnarImputationCount, setMnarImputationCount] = useState('')

  useEffect(() => {
    let active = true
    api.get('/research/v4/summary')
      .then(({ data }) => {
        if (!active) return
        setSummary(data)
        setImputationCount(String(data.study.design.imputation_counts.at(-1) ?? ''))
        setDelta(String(data.coverage.find(row => row.delta_sd === 0)?.delta_sd ?? '0'))
        setMnarEstimand(data.coverage.find(row => row.mechanism === 'MNAR')?.estimand || '')
        setMnarRate(String(data.coverage.find(row => row.mechanism === 'MNAR')?.mask_rate ?? ''))
        setMnarImputationCount(String(data.study.design.imputation_counts.at(-1) ?? ''))
      })
      .catch(loadError => {
        if (!active) return
        const status = loadError.response?.status
        const message = status === 401
          ? 'Your session expired. Please sign in again.'
          : status === 403
            ? 'You do not have access to the research summary.'
            : loadError.response?.data?.message || loadError.message || 'Unable to load research summary.'
        setError(message)
      })
    return () => { active = false }
  }, [])

  const availableEstimands = useMemo(
    () => [...new Set((summary?.coverage || []).map(row => row.estimand))],
    [summary],
  )
  const availableImputationCounts = summary?.study.design.imputation_counts || []
  const availableDeltas = useMemo(
    () => [...new Set((summary?.coverage || []).filter(row => row.mechanism === 'MNAR').map(row => row.delta_sd))].sort((a, b) => a - b),
    [summary],
  )
  const availableMnarRates = useMemo(
    () => [...new Set((summary?.coverage || []).filter(row => row.mechanism === 'MNAR').map(row => row.mask_rate))].sort((a, b) => a - b),
    [summary],
  )
  const methods = summary?.study.design.methods || []
  const primaryRows = summary?.coverage || []
  const mnarRows = primaryRows.filter(row =>
    row.mechanism === 'MNAR' &&
    row.estimand === mnarEstimand &&
    row.mask_rate === Number(mnarRate) &&
    row.m === Number(mnarImputationCount))
  const mnarMethods = [...new Set(mnarRows.map(row => row.method))]
  const exploratory = summary?.exploratory || []

  if (error) {
    return <p className="alert alert-error" role="alert">{error}</p>
  }
  if (!summary) {
    return <p className="loading-inline" role="status">Loading research summary…</p>
  }

  const design = summary.study.design
  const designItems = [
    ['Datasets', design.dataset_count],
    ['Samples per population', design.sample_size],
    ['Seeds per cell', design.seeds_per_cell],
    ['Masked columns', design.masked_columns],
    ['Sanity gate', `${design.sanity_gate.passed}/${design.sanity_gate.total} passed`],
  ]

  return (
    <div className="research-page">
      <PageHeading eyebrow="SIMULATION RESULTS" title="Research"
        description="Rubin-rule interval coverage across missingness mechanisms, estimands, methods, and prespecified sensitivity shifts." />

      <section className="card">
        <h3>Study design</h3>
        <div className="research-design-grid">
          {designItems.map(([label, value]) => (
            <div className="research-design-item" key={label}>
              <span>{label}</span><strong>{value}</strong>
            </div>
          ))}
          <div className="research-design-item research-design-wide">
            <span>Mechanisms</span>
            <strong>{design.mechanisms.join(' · ')}</strong>
          </div>
          <div className="research-design-item research-design-wide">
            <span>Missing rates</span>
            <strong>{design.missing_rates.map(percentage).join(' · ')}</strong>
          </div>
          <div className="research-design-item research-design-wide">
            <span>Methods</span>
            <strong>{design.methods.map(method => METHOD_LABELS[method] || method).join(' · ')}</strong>
          </div>
          <div className="research-tags" aria-label="Study tags">
            {summary.tags.map(tag => <span className="research-tag" key={tag}>{tag}</span>)}
          </div>
        </div>
      </section>

      <section className="card research-controls" aria-label="Coverage chart controls">
        <label>
          Imputations (m)
          <select value={imputationCount} onChange={event => setImputationCount(event.target.value)}>
            {availableImputationCounts.map(value => <option key={value} value={value}>{value}</option>)}
          </select>
        </label>
        <label>
          MNAR delta (SD units)
          <select value={delta} onChange={event => setDelta(event.target.value)}>
            {availableDeltas.map(value => <option key={value} value={value}>{value}</option>)}
          </select>
        </label>
      </section>

      <div className="research-chart-grid">
        {design.mechanisms.flatMap(mechanism => availableEstimands.map(chartEstimand => (
          <CoverageChart
            key={`${mechanism}-${chartEstimand}`}
            title={`${MECHANISM_LABELS[mechanism] || mechanism} · ${ESTIMAND_LABELS[chartEstimand] || chartEstimand}`}
            rows={primaryRows.filter(row =>
              row.mechanism === mechanism &&
              row.estimand === chartEstimand &&
              row.m === Number(imputationCount) &&
              (row.mechanism !== 'MNAR' || row.delta_sd === Number(delta)))}
            xKey="mask_rate"
            methods={methods}
            nominalCoverage={summary.study.nominal_coverage}
            coverageDomain={summary.study.coverage_axis_domain}
            xLabel="Missing rate"
          />
        )))}
      </div>

      <section className="card">
        <div className="research-section-heading">
          <div>
            <h3>MNAR coverage by delta</h3>
            <p className="muted-copy">Coverage and Monte Carlo standard errors across the prespecified delta grid.</p>
          </div>
          <div className="research-controls research-controls-inline">
            <label>
              Estimand
              <select value={mnarEstimand} onChange={event => setMnarEstimand(event.target.value)}>
                {availableEstimands.map(value => <option key={value} value={value}>{ESTIMAND_LABELS[value] || value}</option>)}
              </select>
            </label>
            <label>
              Missing rate
              <select value={mnarRate} onChange={event => setMnarRate(event.target.value)}>
                {availableMnarRates.map(value => <option key={value} value={value}>{percentage(value)}</option>)}
              </select>
            </label>
            <label>
              Imputations (m)
              <select value={mnarImputationCount} onChange={event => setMnarImputationCount(event.target.value)}>
                {availableImputationCounts.map(value => <option key={value} value={value}>{value}</option>)}
              </select>
            </label>
          </div>
        </div>
        <div className="research-chart research-chart-large">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart
              data={keyedChartData(mnarRows, 'delta_sd', mnarMethods)}
              margin={{ top: 12, right: 20, bottom: 20, left: 0 }}>
              <CartesianGrid stroke="#e9edf5" strokeDasharray="4 4" />
              <XAxis type="number" dataKey="delta_sd" domain={['dataMin', 'dataMax']}
                label={{ value: 'Delta (SD units)', position: 'insideBottom', offset: -9 }}
                stroke="#8995aa" tickLine={false} axisLine={false} />
              <YAxis type="number" domain={summary.study.coverage_axis_domain} tickFormatter={percentage}
                stroke="#8995aa" tickLine={false} axisLine={false} width={48} />
              <Tooltip
                formatter={(value, name) => [
                  percentage(value),
                  name.startsWith('mc_se_') ? `MC SE (${METHOD_LABELS[name.slice(6)] || name.slice(6)})` : name,
                ]}
                labelFormatter={value => `Delta: ${value} SD`}
                contentStyle={{ background: '#fff', border: '1px solid #e8ecf5', borderRadius: 10 }} />
              <ReferenceLine y={summary.study.nominal_coverage} stroke="#d15d5d" strokeDasharray="5 4"
                label={{ value: `Nominal ${percentage(summary.study.nominal_coverage)}`, fill: '#ad5353', fontSize: 10 }} />
              <MethodLines methods={mnarMethods} />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
        <p className="research-chart-note">Bars show Monte Carlo standard errors.</p>
      </section>

      <section className="card research-caveats">
        <h3>Caveats</h3>
        <ul>{summary.caveats.map(caveat => <li key={caveat}>{caveat}</li>)}</ul>
      </section>

      <section className="card">
        <h3>Post-hoc exploratory summary</h3>
        <p className="muted-copy">
          Dataset-mean coverage summaries are shown separately from the primary simulation results.
          Monte Carlo standard errors and width ratios are not supplied for these summaries.
        </p>
        <div className="table-wrap">
          <table>
            <thead>
              <tr><th>Label</th><th>Estimand</th><th>Mechanism</th><th>Method</th><th>Missing rate</th><th>Datasets</th><th>Mean dataset coverage</th></tr>
            </thead>
            <tbody>
              {exploratory.map((row, index) => (
                <tr key={`${row.estimand}-${row.mechanism}-${row.method}-${row.mask_rate}-${index}`}>
                  <td>{row.exploratory_label}</td>
                  <td>{ESTIMAND_LABELS[row.estimand] || row.estimand}</td>
                  <td>{row.mechanism}</td>
                  <td>{METHOD_LABELS[row.method] || row.method}</td>
                  <td>{percentage(row.mask_rate)}</td>
                  <td>{row.dataset_count}</td>
                  <td>{percentage(row.coverage)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <p className="muted-copy research-width-note">
        Width ratio: {summary.width_ratio_available ? 'available in the exported primary results.' : 'not available in the source CSVs.'}
      </p>
    </div>
  )
}
