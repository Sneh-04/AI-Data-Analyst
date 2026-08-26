import React, { useState } from 'react'
import { useDataset } from '../api/DatasetContext.jsx'
import { datasetApi } from '../api/client.js'

export default function Chat() {
  const { records, datasetId } = useDataset()
  const [question, setQuestion] = useState('')
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)

  if (records.length === 0) return <p>Upload a dataset first.</p>

  const send = async () => {
    if (!question.trim()) return
    const q = question
    setMessages(m => [...m, { role: 'user', content: q }])
    setQuestion('')
    setLoading(true)
    try {
      const res = await datasetApi.chat(datasetId, { dataset_id: datasetId, records, question: q })
      setMessages(m => [...m, { role: 'assistant', content: res.answer }])
    } catch (e) {
      setMessages(m => [...m, { role: 'assistant', content: `Error: ${e.message}` }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h2>Chat with your data</h2>
      <div className="card">
        {messages.map((m, i) => (
          <div key={i} className={`chat-message ${m.role}`}>{m.content}</div>
        ))}
        {messages.length === 0 && (
          <p style={{ color: '#a9adba', fontSize: 13 }}>
            Try: "what is the average sales", "top 5 revenue", "how many rows"
          </p>
        )}
      </div>
      <div className="card" style={{ display: 'flex', gap: 8 }}>
        <input
          style={{ flex: 1 }}
          value={question}
          onChange={e => setQuestion(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && send()}
          placeholder="Ask a question about your data..."
        />
        <button onClick={send} disabled={loading}>{loading ? '...' : 'Send'}</button>
      </div>
    </div>
  )
}
