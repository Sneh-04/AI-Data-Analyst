import React, { useEffect, useState } from 'react'
import { useDataset } from '../api/DatasetContext.jsx'
import api from '../api/client.js'
import EmptyState from '../components/EmptyState.jsx'
import PageHeading from '../components/PageHeading.jsx'

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

  if (records.length === 0) return <EmptyState title="Create a report from your data" description="Upload a dataset to generate a downloadable PDF or Excel report." />

  return (
    <div>
      <PageHeading eyebrow="SHARE YOUR WORK" title="Reports"
        description="Package your dataset analysis in a format that is easy to share." />
      <div className="card control-panel report-controls">
        <label htmlFor="report-format">Format</label>
        <select id="report-format" value={format} onChange={e => setFormat(e.target.value)}>
          <option value="PDF">PDF</option>
          <option value="XLSX">Excel</option>
        </select>
        <button onClick={generateReport} disabled={loading || !datasetId} data-loading={loading}>
          {loading ? 'Generating...' : 'Generate report'}
        </button>
        {!datasetId && <p>Persist this dataset first to generate a report.</p>}
        {error && <p className="alert alert-error" role="alert">{error}</p>}
      </div>
      {download && (
        <div className="card report-download">
          <span className="report-file-icon" aria-hidden="true">↓</span>
          <div><strong>Your report is ready</strong><small>{download.name}</small></div>
          <a className="button-link" href={download.url} download={download.name}>Download {format} report</a>
        </div>
      )}
    </div>
  )
}
