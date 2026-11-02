const COLUMNS = [
  'record_type',
  'method',
  'target_column',
  'estimand',
  'predictor_column',
  'selected_method',
  'm',
  'seed',
  'delta',
  'estimate',
  'ci_lower',
  'ci_upper',
  'standard_error',
  'degrees_of_freedom',
  'within_variance',
  'between_variance',
  'total_variance',
  'lambda',
  'missing_fraction',
  'rows_used',
  'subsampled',
  'method_note',
  'warning',
]

const USER_CONTROLLED_TEXT_COLUMNS = new Set(['target_column', 'predictor_column'])

function csvCell(value, column) {
  let text = String(value ?? '')
  if (USER_CONTROLLED_TEXT_COLUMNS.has(column) && /^[\t\r\n ]*[=+\-@]/.test(text)) {
    text = `'${text}`
  }
  return `"${text.replaceAll('"', '""')}"`
}

export function serializeInferenceResult(result) {
  const rows = []
  const append = (recordType, method, values, delta = '') => {
    rows.push({
      record_type: recordType,
      target_column: result.settings.target_column,
      estimand: result.settings.estimand,
      predictor_column: result.settings.predictor_column,
      selected_method: result.settings.selected_method,
      m: result.settings.m,
      seed: result.settings.seed,
      delta,
      estimate: values?.estimate,
      ci_lower: values?.ci_lower,
      ci_upper: values?.ci_upper,
      standard_error: values?.standard_error,
      degrees_of_freedom: values?.degrees_of_freedom,
      within_variance: values?.within_variance,
      between_variance: values?.between_variance,
      total_variance: values?.total_variance,
      lambda: values?.lambda,
      missing_fraction: result.missingFraction,
      rows_used: result.rowsUsed,
      subsampled: result.subsampled,
      method_note: result.methodNote,
      warning: '',
      method,
    })
  }

  append('summary', 'naive', result.naive, 0)
  append('summary', 'improper', result.improper, 0)
  append('summary', 'proper', result.proper, 0)
  result.sensitivity.forEach(item => append('sensitivity', 'proper', item, item.delta))
  result.warnings.forEach(warning => {
    rows.push({
      record_type: 'warning',
      target_column: result.settings.target_column,
      estimand: result.settings.estimand,
      predictor_column: result.settings.predictor_column,
      selected_method: result.settings.selected_method,
      m: result.settings.m,
      seed: result.settings.seed,
      warning,
    })
  })

  return [
    COLUMNS.join(','),
    ...rows.map(row => COLUMNS.map(column => csvCell(row[column], column)).join(',')),
  ].join('\r\n') + '\r\n'
}
