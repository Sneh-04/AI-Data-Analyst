import React, { useState } from 'react'
import { useDataset } from '../api/DatasetContext.jsx'
import { datasetApi } from '../api/client.js'
import EmptyState from '../components/EmptyState.jsx'
import PageHeading from '../components/PageHeading.jsx'

export default function Chat() {
  const { records, datasetId } = useDataset()
  const [question, setQuestion] = useState('')
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)
  const chatEnabled = import.meta.env.VITE_CHAT_ENABLED === 'true'

  if (!chatEnabled) {
    return (
      <EmptyState
        title="Chat is disabled"
        description="The AI chat feature is disabled for this demo because no valid OpenAI or Ollama provider is configured. Enable CHAT_ENABLED and provide a working provider key in .env to re-enable it."
      />
    )
  }

  if (records.length === 0) return <EmptyState title="Ask your data a question" description="Upload a dataset to explore it through a natural-language conversation." />
  if (!datasetId) return <EmptyState title="Save your dataset to continue" description="Upload this dataset to the platform before chatting with it." />

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
      <PageHeading eyebrow="ASK A QUESTION" title="Chat with your data"
        description="Ask questions in plain language and explore answers grounded in your dataset." />
      <div className="card chat-history">
        {messages.map((m, i) => (
          <div key={i} className={`chat-message ${m.role}`}>{m.content}</div>
        ))}
        {messages.length === 0 && (
          <p className="chat-empty-prompt">
            Try: "what is the average sales", "top 5 revenue", "how many rows"
          </p>
        )}
      </div>
      <div className="card chat-composer">
        <input
          style={{ flex: 1 }}
          value={question}
          onChange={e => setQuestion(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && send()}
          placeholder="Ask a question about your data..."
        />
        <button onClick={send} disabled={loading} data-loading={loading}>{loading ? 'Sending...' : 'Send'}</button>
      </div>
    </div>
  )
}
