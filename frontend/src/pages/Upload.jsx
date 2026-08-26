import React from 'react'
import { useNavigate } from 'react-router-dom'
import { useDataset } from '../api/DatasetContext.jsx'
import api from '../api/client.js'

export default function Upload() {
  const { fileName, headers, records, loadFile, datasetId, setDatasetId, setHeaders, setRecords } = useDataset()
  const [selectedFile, setSelectedFile] = React.useState(null)
  const [uploading, setUploading] = React.useState(false)
  const [uploadError, setUploadError] = React.useState('')
  const navigate = useNavigate()

  const handleFileChange = (event) => {
    const file = event.target.files[0]
    if (!file) return
    setSelectedFile(file)
    setUploadError('')
    loadFile(file)
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
      const recordsResponse = await api.get(`/datasets/${uploadedDatasetId}/records`)
      const persistedRecords = recordsResponse.data
      setRecords(persistedRecords)
      setHeaders(persistedRecords.length > 0 ? Object.keys(persistedRecords[0]) : [])
    } catch (error) {
      setUploadError(error.response?.data?.message || 'Unable to upload the dataset.')
    } finally {
      setUploading(false)
    }
  }

  return (
    <div>
      <h2>Upload dataset</h2>
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
          <button style={{ marginTop: 8 }} onClick={() => navigate('/overview')}>
            Continue to Overview →
          </button>
        )}
      </div>
      <div className="card">
        <p style={{ color: '#a9adba', fontSize: 13 }}>
          In production this uploads to Spring Boot, which streams the file to object storage,
          inserts a row into <code>datasets</code>, and returns a <code>dataset_id</code>. This scaffold
          parses the CSV client-side so every page below has real data to call the ML service with.
        </p>
      </div>
    </div>
  )
}
