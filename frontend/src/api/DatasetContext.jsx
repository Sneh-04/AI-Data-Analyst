import React, { createContext, useContext, useState } from 'react'

const DatasetContext = createContext(null)

function parseCsv(text) {
  const lines = text.trim().split(/\r?\n/)
  const headers = lines[0].split(',').map(h => h.trim())
  const records = lines.slice(1).filter(Boolean).map(line => {
    const values = line.split(',')
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

  const loadFile = (file) => {
    const reader = new FileReader()
    reader.onload = (e) => {
      const { headers, records } = parseCsv(e.target.result)
      setFileName(file.name)
      setHeaders(headers)
      setRecords(records)
    }
    reader.readAsText(file)
  }

  return (
    <DatasetContext.Provider value={{ fileName, headers, records, setRecords, setHeaders, loadFile, datasetId, setDatasetId }}>
      {children}
    </DatasetContext.Provider>
  )
}

export const useDataset = () => useContext(DatasetContext)
