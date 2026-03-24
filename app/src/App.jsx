import { useState, useEffect, useRef } from 'react'

function App() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [message, setMessage] = useState('')
  const [messages, setMessages] = useState([])
  const [users, setUsers] = useState([])
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [connectionStatus, setConnectionStatus] = useState('Disconnected')
  const [selectedRecipient, setSelectedRecipient] = useState('')
  const ws = useRef(null)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

 

  const connect = () => {
    if (!username || !password) {
      alert('Please enter username and password')
      return
    }

    setConnectionStatus('Connecting...')
    ws.current = new WebSocket('ws://localhost:3001')
    
    ws.current.onopen = () => {
      setConnectionStatus('Connected')
      ws.current.send(username)
      ws.current.send(password)
    }
    
    ws.current.onmessage = (event) => {
      const data = event.data
      
      // Check for registration confirmation
      if (data === 'Registered') {
        setIsLoggedIn(true)
        setConnectionStatus('Logged in')
        // Request user list immediately after login
        setTimeout(() => {
          if (ws.current && ws.current.readyState === WebSocket.OPEN) {
            ws.current.send('/users')
          }
        }, 500)
        return
      }
      
      // Check for errors
      if (data.startsWith('Error:')) {
        alert(data)
        if (data.includes('Username taken')) {
          setIsLoggedIn(false)
          setConnectionStatus('Disconnected')
        }
        return
      }
      
      // Check for user list
      if (data.startsWith('Users: ')) {
        const userList = data.replace('Users: ', '').split(', ')
        const otherUsers = userList.filter(u => u !== username)
        setUsers(otherUsers)
        if (!selectedRecipient && otherUsers.length > 0) {
          setSelectedRecipient(otherUsers[0])
        }
        return
      }
      
      // Check for messages (format: "username: message")
      const colonIndex = data.indexOf(': ')
      if (colonIndex > 0) {
        const from = data.substring(0, colonIndex)
        const payload = data.substring(colonIndex + 2)
        setMessages(prev => [...prev, { from, payload, timestamp: new Date() }])
        return
      }
  
    }
    
    ws.current.onclose = () => {
   
      setConnectionStatus('Disconnected')
      setIsLoggedIn(false)
    }
    
    ws.current.onerror = (error) => {
      setConnectionStatus('Error')
      alert('Connection error. Make sure the WebSocket server is running on port 3001')
    }
  }

  const sendMessage = () => {
    if (!selectedRecipient) {
      alert('Please select a recipient first')
      return
    }
    
    if (!message.trim()) {
      alert('Please enter a message')
      return
    }
    
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      const fullMessage = `/msg ${selectedRecipient} ${message}`
      ws.current.send(fullMessage)
      
      // Add to local messages
      setMessages(prev => [...prev, { 
        from: `${username} → ${selectedRecipient}`, 
        payload: message,
        timestamp: new Date(),
        isOwn: true
      }])
      
      setMessage('')
    } else {
      alert('Not connected to server')
    }
  }

  const listUsers = () => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send('/users')
    }
  }

  return (
    <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto', fontFamily: 'Arial' }}>
      {!isLoggedIn ? (
        <div style={{ maxWidth: '400px', margin: '50px auto' }}>
          <h2>💬 Chat Login</h2>
          <div style={{ marginBottom: '10px' }}>
            <input 
              value={username} 
              onChange={(e) => setUsername(e.target.value)} 
              placeholder="Username" 
              style={{ padding: '8px', width: '100%', marginBottom: '10px' }}
            />
            <input 
              type="password" 
              value={password} 
              onChange={(e) => setPassword(e.target.value)} 
              placeholder="Shared Password" 
              style={{ padding: '8px', width: '100%' }}
            />
          </div>
          <button onClick={connect} style={{ padding: '10px', width: '100%', marginTop: '10px' }}>
            Connect
          </button>
          <p style={{ marginTop: '10px', fontSize: '12px', color: '#666' }}>
            Status: {connectionStatus}
          </p>
        </div>
      ) : (
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '20px' }}>
            <h2>💬 Chat Room</h2>
            <div>
              <span>Logged in as: <strong>{username}</strong></span>
              <button onClick={listUsers} style={{ marginLeft: '10px', padding: '5px 10px' }}>
                Refresh Users
              </button>
            </div>
          </div>
          
          <div style={{ display: 'flex', gap: '20px' }}>
            {/* Users Panel */}
            <div style={{ width: '200px' }}>
              <h3>👥 Online Users</h3>
              <div style={{ border: '1px solid #ddd', borderRadius: '4px', padding: '10px' }}>
                {users.length === 0 ? (
                  <p style={{ color: '#999' }}>No other users online</p>
                ) : (
                  users.map(user => (
                    <div
                      key={user}
                      onClick={() => setSelectedRecipient(user)}
                      style={{
                        padding: '8px',
                        margin: '5px 0',
                        backgroundColor: selectedRecipient === user ? '#4CAF50' : '#f0f0f0',
                        color: selectedRecipient === user ? 'white' : 'black',
                        borderRadius: '4px',
                        cursor: 'pointer'
                      }}
                    >
                      {user} {selectedRecipient === user && '✓'}
                    </div>
                  ))
                )}
              </div>
            </div>
            
            {/* Messages Panel */}
            <div style={{ flex: 1 }}>
              <h3>📨 Messages</h3>
              <div style={{ 
                height: '400px', 
                overflowY: 'scroll', 
                border: '1px solid #ddd', 
                padding: '10px',
                backgroundColor: '#fafafa',
                borderRadius: '4px',
                width: '600px'
              }}>
                {messages.length === 0 ? (
                  <p style={{ textAlign: 'center', color: '#999', marginTop: '180px' }}>
                    No messages yet. Select a user and start chatting!
                  </p>
                ) : (
                  messages.map((msg, i) => (
                    <div key={i} style={{ 
                      margin: '10px 0',
                      padding: '8px',
                      backgroundColor: msg.from === username ? '#e3f2fd' : '#fff',
                      borderRadius: '4px',
                      borderLeft: `3px solid ${msg.from === username ? '#2196f3' : '#4caf50'}`
                    }}>
                      <div style={{ fontSize: '12px', color: '#666', marginBottom: '5px' }}>
                        {msg.from} • {msg.timestamp.toLocaleTimeString()}
                      </div>
                      <div>{msg.payload}</div>
                    </div>
                  ))
                )}
                <div ref={messagesEndRef} />
              </div>
              
              <div style={{ marginTop: '10px' }}>
                <div style={{ marginBottom: '5px' }}>
                  <strong>Sending to: {selectedRecipient || 'None selected'}</strong>
                </div>
                <div style={{ display: 'flex', gap: '10px' }}>
                  <input 
                    value={message} 
                    onChange={(e) => setMessage(e.target.value)} 
                    placeholder={selectedRecipient ? `Message to ${selectedRecipient}...` : "Select a user first"} 
                    style={{ flex: 1, padding: '8px' }} 
                    onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                    disabled={!selectedRecipient}
                  />
                  <button 
                    onClick={sendMessage} 
                    disabled={!selectedRecipient || !message}
                    style={{ padding: '8px 20px' }}
                  >
                    Send
                  </button>
                </div>
              </div>
            </div>
            
            
          </div>
        </div>
      )}
    </div>
  )
}

export default App