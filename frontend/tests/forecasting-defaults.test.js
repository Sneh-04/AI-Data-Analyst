import test from 'node:test'
import assert from 'node:assert/strict'
import { dateLikeColumns, getDefaultForecastColumns, looksLikeDateValue } from '../src/utils/forecastDefaults.js'

test('prefers the actual date column when building forecast defaults', () => {
  const headers = ['x1', 'x2', 'x3', 'category', 'date']
  const rows = [
    { x1: -0.0425, x2: 1.25, x3: 0.8045, category: 'beta', date: '2024-01-01' },
    { x1: 0.9517, x2: 5.0698, x3: 2.1305, category: 'delta', date: '2024-01-02' },
    { x1: 1.8446, x2: 2.5, x3: 1.4933, category: 'delta', date: '2024-01-03' },
  ]

  assert.equal(looksLikeDateValue('2024-01-01'), true)
  assert.deepEqual(dateLikeColumns(headers, rows), ['date'])
  assert.deepEqual(getDefaultForecastColumns(headers, rows), {
    dateColumn: 'date',
    valueColumn: 'x1',
    numericHeaders: ['x1', 'x2', 'x3'],
    validDateColumns: ['date'],
  })
})

test('falls back safely when a dataset has no date-like column', () => {
  const headers = ['a', 'b', 'c']
  const rows = [
    { a: 1, b: 2, c: 3 },
    { a: 2, b: 3, c: 4 },
  ]

  const defaults = getDefaultForecastColumns(headers, rows)
  assert.equal(defaults.dateColumn, 'a')
  assert.equal(defaults.valueColumn, 'b')
})
