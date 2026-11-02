export function looksLikeDateValue(value) {
  if (value === null || value === undefined || value === '') return false
  if (typeof value === 'number') return false
  if (value instanceof Date) return !Number.isNaN(value.getTime())
  const asString = String(value).trim()
  if (!asString || /^-?\d+(\.\d+)?$/.test(asString)) return false
  const hasDateMarker = /[-/]|[A-Za-z]/.test(asString)
  if (!hasDateMarker) return false
  const parsed = new Date(asString)
  return !Number.isNaN(parsed.getTime())
}

export function dateLikeColumns(headers, rows) {
  return headers.filter(header => {
    const values = rows
      .map(row => row[header])
      .filter(value => value !== null && value !== undefined && String(value).trim() !== '')
    if (values.length === 0) return false
    const matching = values.filter(value => looksLikeDateValue(value)).length
    return matching / values.length >= 0.5
  })
}

export function getDefaultForecastColumns(headers, rows) {
  const numericHeaders = headers.filter(header => {
    const first = rows[0]?.[header]
    if (first == null || first === '' || typeof first === 'boolean') return false
    const numeric = Number(first)
    return !Number.isNaN(numeric)
  })
  const validDateColumns = dateLikeColumns(headers, rows)
  const dateColumn = validDateColumns[0] || headers.find(header => /date|time|timestamp/i.test(header)) || headers[0] || ''
  const valueColumn = numericHeaders.find(header => header !== dateColumn) || numericHeaders[0] || ''
  return { dateColumn, valueColumn, numericHeaders, validDateColumns }
}
