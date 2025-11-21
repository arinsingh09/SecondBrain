import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import rehypeRaw from 'rehype-raw'
import './App.css'

const API_URL = 'http://localhost:8000'

function App() {
  const [activeTab, setActiveTab] = useState('ask')
  const [question, setQuestion] = useState('')
  const [answer, setAnswer] = useState('')
  const [loading, setLoading] = useState(false)
  const [history, setHistory] = useState([])
  const [flashcards, setFlashcards] = useState([])
  const [flashcardsLoading, setFlashcardsLoading] = useState(false)
  const [error, setError] = useState('')

  const handleAsk = async () => {
    if (!question.trim()) {
      setError('Please enter a question.')
      return
    }

    setLoading(true)
    setError('')
    
    console.log('Sending question:', question)
    
    try {
      // Add timeout to fetch request
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 90000) // 90 second timeout
      
      console.log('Making fetch request to:', `${API_URL}/ask`)
      const response = await fetch(`${API_URL}/ask`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question }),
        signal: controller.signal
      })

      clearTimeout(timeoutId)
      console.log('Response received:', response.status, response.statusText)
      
      // Check if response is ok before parsing
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: `HTTP ${response.status}: ${response.statusText}` }))
        setError(errorData.detail || errorData.error || `Server error: ${response.status}`)
        setLoading(false)
        return
      }
      
      const data = await response.json()
      console.log('Response data:', data)
      
      if (data.answer) {
        setAnswer(data.answer)
        setHistory(prev => [...prev, { user: question, bot: data.answer }])
        setQuestion('')
      } else {
        setError('No answer received from server')
      }
    } catch (err) {
      if (err.name === 'AbortError') {
        setError('Request timed out. The server may be processing or Ollama may not be running.')
      } else if (err instanceof TypeError && err.message.includes('fetch')) {
        setError('Failed to connect to server. Make sure the backend is running on http://localhost:8000')
      } else {
        setError(`Error: ${err.message}`)
      }
      console.error('Error details:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleGenerateFlashcards = async () => {
    setFlashcardsLoading(true)
    setError('')
    
    try {
      const response = await fetch(`${API_URL}/flashcards`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      })

      const data = await response.json()
      
      if (response.ok) {
        setFlashcards(data.cards || [])
      } else {
        setError(data.error || 'Failed to generate flashcards')
      }
    } catch (err) {
      setError('Failed to connect to the server. Make sure the backend is running.')
    } finally {
      setFlashcardsLoading(false)
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>🧠 Your Second Brain</h1>
      </header>

      <div className="tabs">
        <button
          className={activeTab === 'ask' ? 'tab active' : 'tab'}
          onClick={() => setActiveTab('ask')}
        >
          💬 Ask
        </button>
        <button
          className={activeTab === 'history' ? 'tab active' : 'tab'}
          onClick={() => setActiveTab('history')}
        >
          📜 History
        </button>
        <button
          className={activeTab === 'flashcards' ? 'tab active' : 'tab'}
          onClick={() => setActiveTab('flashcards')}
        >
          ⚡ Flash Cards
        </button>
      </div>

      <main className="content">
        {error && <div className="error">{error}</div>}

        {activeTab === 'ask' && (
          <div className="ask-section">
            <div className="input-group">
              <input
                type="text"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="❓ Ask me anything from your S3 data..."
                onKeyPress={(e) => e.key === 'Enter' && handleAsk()}
                disabled={loading}
              />
              <button onClick={handleAsk} disabled={loading || !question.trim()}>
                {loading ? 'Thinking...' : 'Ask'}
              </button>
            </div>
            {answer && (
              <div className="answer-section">
                <h3>Answer:</h3>
                <div className="answer-content">
                  <ReactMarkdown remarkPlugins={[remarkGfm]} rehypePlugins={[rehypeRaw]}>
                    {answer}
                  </ReactMarkdown>
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'history' && (
          <div className="history-section">
            <h2>Conversation History</h2>
            {history.length === 0 ? (
              <p className="empty-state">No questions asked yet.</p>
            ) : (
              <div className="history-list">
                {[...history].reverse().map((msg, idx) => (
                  <div key={idx} className="history-item">
                    <div className="history-user">
                      <strong>🧑 You:</strong> {msg.user}
                    </div>
                    <div className="history-bot">
                      <strong>🤖 Bot:</strong>
                      <div className="history-answer">
                        <ReactMarkdown remarkPlugins={[remarkGfm]} rehypePlugins={[rehypeRaw]}>
                          {msg.bot}
                        </ReactMarkdown>
                      </div>
                    </div>
                    <hr />
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'flashcards' && (
          <div className="flashcards-section">
            <h2>Generate Flashcards from your AWS data</h2>
            <button
              onClick={handleGenerateFlashcards}
              disabled={flashcardsLoading}
              className="generate-btn"
            >
              {flashcardsLoading ? 'Generating flashcards...' : 'Generate Flashcards'}
            </button>
            {flashcards.length > 0 && (
              <div className="flashcards-grid">
                {flashcards.map((card, idx) => (
                  <div key={idx} className="flashcard">
                    <div className="flashcard-question">
                      <strong>Card {idx + 1}:</strong> {card.question || '❓'}
                    </div>
                    <div className="flashcard-answer">
                      {card.answer || '❓'}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  )
}

export default App
