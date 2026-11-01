import React from 'react'
import { useNavigate } from 'react-router-dom'
import { useDataset } from '../api/DatasetContext.jsx'
import api from '../api/client.js'
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
    <div>
      <h2>Upload dataset</h2>
      <MyDatasets refreshKey={datasetsRefreshKey} />
      <div className="card">
        <input
          type="file"
          accept=".csv"
          onChange={handleFileChange}
        />
        {fileName && (
          <p style={{ marginTop: 16 }}>
            Loaded <strong>{fileName}</strong> — {records.length} rows, {headers.length} columns.
          </p>
        )}
        {selectedFile && (
          <button style={{ marginTop: 8, marginLeft: 8 }} onClick={uploadFile} disabled={uploading}>
            {uploading ? 'Uploading...' : datasetId ? 'Upload again' : 'Upload to platform'}
          </button>
        )}
        {datasetId && <p style={{ color: '#8bd5a7', fontSize: 13 }}>Persisted dataset #{datasetId}</p>}
        {uploadError && <p style={{ color: '#e27b7b', fontSize: 13 }}>{uploadError}</p>}
        {records.length > 0 && (
          <button style={{ marginTop: 8 }} onClick={() => navigate('/overview')} disabled={!datasetId}>
            Continue to Overview →
          </button>
        )}
        {records.length > 0 && !datasetId && <p style={{ color: '#d4a04f', fontSize: 13 }}>
          Upload this dataset to the platform before starting analysis.
        </p>}
      </div>
      <div className="card">
        <p style={{ color: '#a9adba', fontSize: 13 }}>
          CSV data is previewed locally, then persisted through the authenticated Spring Boot API.
          Analysis pages are enabled after the upload has been stored.
        </p>
      </div>
    </div>
  )
}
