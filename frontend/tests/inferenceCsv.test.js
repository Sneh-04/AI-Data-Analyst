import assert from 'node:assert/strict'
import test from 'node:test'
import { serializeInferenceResult } from '../src/utils/inferenceCsv.js'

test('exports summaries, sensitivity rows, settings, and warnings as CSV', () => {
  const csv = serializeInferenceResult({
    settings: {
      target_column: '=SUM(1,1)',
      estimand: 'ols_slope',
      predictor_column: 'predictor',
      selected_method: 'proper',
      m: 20,
      seed: 42,
    },
    proper: { estimate: 1.5, ci_lower: 1, ci_upper: 2, lambda: 0.2 },
    improper: { estimate: 1.4, ci_lower: 0.8, ci_upper: 2.1 },
    naive: { estimate: 1.3, ci_lower: 0.9, ci_upper: 1.7 },
    sensitivity: [{ delta: 0.5, estimate: 1.7, ci_lower: 1.1, ci_upper: 2.3 }],
    missingFraction: 0.25,
    rowsUsed: 100,
    subsampled: false,
    methodNote: 'Intervals depend on assumptions.',
    warnings: ['Do not interpret as calibrated.'],
  })

  const rows = csv.trimEnd().split('\r\n')
  assert.equal(rows.length, 6)
  assert.match(rows[1], /^"summary","naive","'=SUM\(1,1\)","ols_slope"/)
  assert.match(rows[4], /^"sensitivity","proper"/)
  assert.match(rows[5], /^"warning",""/)
  assert.ok(csv.includes('"Do not interpret as calibrated."'))
  assert.ok(csv.includes('"20","42"'))
})

test('escapes quotes and newlines in exported values', () => {
  const csv = serializeInferenceResult({
    settings: {
      target_column: 'target',
      estimand: 'mean',
      predictor_column: '',
      selected_method: 'proper',
      m: 2,
      seed: 1,
    },
    proper: { estimate: 1 },
    improper: { estimate: 1 },
    naive: { estimate: 1 },
    sensitivity: [],
    missingFraction: 0,
    rowsUsed: 2,
    subsampled: false,
    methodNote: 'line one\nline "two"',
    warnings: [],
  })

  assert.ok(csv.includes('"line one\nline ""two"""'))
})
