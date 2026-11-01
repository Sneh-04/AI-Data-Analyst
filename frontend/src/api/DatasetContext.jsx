import React, { createContext, useContext, useState } from 'react'

const DatasetContext = createContext(null)

function parseCsv(text) {
  const rows = []
  let row = []
  let value = ''
  let quoted = false

  for (let index = 0; index < text.length; index += 1) {
    const character = text[index]
    if (quoted) {
      if (character === '"' && text[index + 1] === '"') {
        value += '"'
        index += 1
      } else if (character === '"') {
        quoted = false
      } else {
        value += character
      }
    } else if (character === '"' && value.length === 0) {
      quoted = true
    } else if (character === ',') {
      row.push(value)
      value = ''
    } else if (character === '\r' || character === '\n') {
      row.push(value)
      if (!(row.length === 1 && row[0].trim() === '')) rows.push(row)
      row = []
      value = ''
      if (character === '\r' && text[index + 1] === '\n') index += 1
    } else {
      value += character
    }
  }

  if (quoted) throw new Error('CSV contains an unterminated quoted field.')
  if (row.length > 0 || value.length > 0) {
    row.push(value)
    if (!(row.length === 1 && row[0].trim() === '')) rows.push(row)
  }
  if (rows.length === 0) throw new Error('CSV must contain a header row.')

  const headers = rows[0].map((header, index) =>
    (index === 0 ? header.replace(/^\uFEFF/, '') : header).trim())
  if (headers.length === 0 || headers.some(header => header === '')) {
    throw new Error('CSV headers must not be empty.')
  }
  const records = rows.slice(1).map(values => {
    const row = {}
    headers.forEach((h, i) => {
      const raw = (values[i] ?? '').trim()
      const num = Number(raw)
      row[h] = raw !== '' && !Number.isNaN(num) ? num : raw
    })
    return row
  })
  return { headers, records }
}

export function DatasetProvider({ children }) {
  const [fileName, setFileName] = useState(null)
  const [headers, setHeaders] = useState([])
  const [records, setRecords] = useState([])
  const [datasetId, setDatasetId] = useState(null)

  const loadFile = (file) => new Promise((resolve, reject) => {
    setFileName(null)
    setHeaders([])
    setRecords([])
    const reader = new FileReader()
    reader.onload = (e) => {
      try {
        const parsed = parseCsv(String(e.target.result ?? ''))
        setFileName(file.name)
        setHeaders(parsed.headers)
        setRecords(parsed.records)
        resolve(parsed)
      } catch (error) {
        reject(error)
      }
    }
    reader.onerror = () => reject(new Error('Unable to read the selected CSV file.'))
    reader.readAsText(file)
  })

  return (
    <DatasetContext.Provider value={{ fileName, headers, records, setRecords, setHeaders, loadFile, datasetId, setDatasetId, setFileName }}>
      {children}
    </DatasetContext.Provider>
  )
}

export const useDataset = () => useContext(DatasetContext)
