import React, { useEffect, useState } from 'react'
import { useDataset } from '../api/DatasetContext.jsx'
import api from '../api/client.js'

export default function Reports() {
  const { records, datasetId, fileName } = useDataset()
  const [format, setFormat] = useState('PDF')
  const [download, setDownload] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => () => {
    if (download?.url) URL.revokeObjectURL(download.url)
  }, [download])

  const generateReport = async () => {
    if (!datasetId) return
    setLoading(true)
    setError(null)
    if (download?.url) URL.revokeObjectURL(download.url)
    try {
      const response = await api.post(`/datasets/${datasetId}/reports`, { format }, { responseType: 'blob' })
      const extension = format === 'PDF' ? 'pdf' : 'xlsx'
      setDownload({
        url: URL.createObjectURL(response.data),
        name: `${fileName?.replace(/\.csv$/i, '') || `dataset-${datasetId}`}-report.${extension}`,
      })
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setLoading(false)
    }
  }

  if (records.length === 0) return <p>Upload a dataset first.</p>

  return (
    <div>
      <h2>Reports</h2>
      <div className="card">
        <label>Format: </label>
        <select value={format} onChange={e => setFormat(e.target.value)} style={{ marginRight: 16 }}>
          <option value="PDF">PDF</option>
          <option value="XLSX">Excel</option>
        </select>
        <button onClick={generateReport} disabled={loading || !datasetId}>
          {loading ? 'Generating...' : 'Generate report'}
        </button>
        {!datasetId && <p>Persist this dataset first to generate a report.</p>}
        {error && <p style={{ color: '#e06c75' }}>{error}</p>}
      </div>
      {download && (
        <div className="card">
          <a href={download.url} download={download.name}>Download {format} report</a>
        </div>
      )}
    </div>
  )
}
