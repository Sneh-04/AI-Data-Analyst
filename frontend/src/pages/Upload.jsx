import React from 'react'
import { useNavigate } from 'react-router-dom'
import { useDataset } from '../api/DatasetContext.jsx'
import api from '../api/client.js'
import PageHeading from '../components/PageHeading.jsx'
import MyDatasets from '../components/MyDatasets.jsx'

export default function Upload() {
  const { fileName, headers, records, loadFile, datasetId, setDatasetId, setHeaders, setRecords } = useDataset()
  const [selectedFile, setSelectedFile] = React.useState(null)
  const [uploading, setUploading] = React.useState(false)
  const [uploadError, setUploadError] = React.useState('')
  const [datasetsRefreshKey, setDatasetsRefreshKey] = React.useState(0)
  const navigate = useNavigate()

  const handleFileChange = async (event) => {
    const file = event.target.files[0]
    if (!file) return
    setDatasetId(null)
    localStorage.removeItem('selectedDatasetId')
    setSelectedFile(file)
    setUploadError('')
    try {
      await loadFile(file)
    } catch (error) {
      setSelectedFile(null)
      setUploadError(error.message)
    }
  }

  const uploadFile = async () => {
    if (!selectedFile) return
    setUploading(true)
    setUploadError('')
    const formData = new FormData()
    formData.append('file', selectedFile)
    try {
      const response = await api.post('/datasets/upload', formData)
      const uploadedDatasetId = response.data.datasetId
      setDatasetId(uploadedDatasetId)
      localStorage.setItem('selectedDatasetId', String(uploadedDatasetId))
      const recordsResponse = await api.get(`/datasets/${uploadedDatasetId}/records`)
      const persistedRecords = recordsResponse.data
      setRecords(persistedRecords)
      setHeaders(persistedRecords.length > 0 ? Object.keys(persistedRecords[0]) : [])
      setDatasetsRefreshKey(key => key + 1)
    } catch (error) {
      setUploadError(error.response?.data?.message || 'Unable to upload the dataset.')
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="upload-page">
      <PageHeading eyebrow="GET STARTED" title="Upload dataset"
        description="Bring in a CSV and start exploring its quality, patterns, and forecasts." />
      <MyDatasets refreshKey={datasetsRefreshKey} />
      <div className="card upload-card">
        <div className="upload-dropzone">
          <span className="upload-drop-icon" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 16V4m0 0L7 9m5-5 5 5" /><path d="M5 14v5h14v-5" />
            </svg>
          </span>
          <div className="upload-file-content">
            <label className="upload-file-label" htmlFor="dataset-file">Choose a CSV file to begin</label>
            <p>Your data is previewed before you upload it to your workspace.</p>
            <input id="dataset-file" type="file" accept=".csv" onChange={handleFileChange} />
          </div>
        </div>
        {fileName && (
          <p className="upload-meta" style={{ marginTop: 16 }}>
            Loaded <strong>{fileName}</strong> — {records.length} rows, {headers.length} columns.
          </p>
        )}
        {selectedFile && (
          <button style={{ marginTop: 16 }} onClick={uploadFile} disabled={uploading} data-loading={uploading}>
            {uploading ? 'Uploading...' : datasetId ? 'Upload again' : 'Upload to platform'}
          </button>
        )}
        {datasetId && <p className="upload-persisted">✓ Persisted dataset #{datasetId}</p>}
        {uploadError && <p className="alert alert-error" role="alert">{uploadError}</p>}
        {records.length > 0 && (
          <button style={{ marginTop: 12 }} onClick={() => navigate('/overview')} disabled={!datasetId}>
            Continue to Overview →
          </button>
        )}
        {records.length > 0 && !datasetId && <p className="alert alert-info" style={{ marginTop: 12 }}>
          Upload this dataset to the platform before starting analysis.
        </p>}
      </div>
      <div className="card upload-note">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
          <circle cx="12" cy="12" r="9" /><path d="M12 11v5m0-8h.01" />
        </svg>
        <p>
          CSV data is previewed locally, then persisted through the authenticated Spring Boot API.
          Analysis pages are enabled after the upload has been stored.
        </p>
      </div>
    </div>
  )
}
