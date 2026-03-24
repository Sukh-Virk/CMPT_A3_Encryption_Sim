import { useState, useEffect, useRef } from 'react'
import './App.css'

function App() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [message, setMessage] = useState('')
  const [messages, setMessages] = useState([])
  const [users, setUsers] = useState([])
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const ws = useRef(null)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    ws.current = new WebSocket('ws://localhost:3001')
    
    ws.current.onopen = () => {
      console.log('Connected to backend')
    }
    
    ws.current.onmessage = (event) => {
      const output = event.data;
      console.log('Received from backend:', output);
      
      // Parse output from client.py
      const lines = output.split('\n');
      lines.forEach(line => {
        line = line.trim();
        if (line.startsWith('Users: ')) {
          const userList = line.replace('Users: ', '').split(', ');
          setUsers(userList);
        } else if (line.includes(': ') && !line.startsWith('Error:')) {
          const [from, ...msgParts] = line.split(': ');
          const payload = msgParts.join(': ');
          setMessages(prev => [...prev, { from, payload }]);
        } else if (line.startsWith('Error:')) {
          alert(line);
        }
      });
    }
    
    ws.current.onclose = () => {
      console.log('Disconnected from backend');
      setIsLoggedIn(false);
    }
    
    return () => ws.current?.close()
  }, [])  // No dependency on username/password

  const connect = () => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN && username && password) {
      ws.current.send(username);
      ws.current.send(password);
      setIsLoggedIn(true);
    } else {
      alert('Please enter username and password, and ensure connection is open.');
    }
  }

  const sendMessage = () => {
    if (ws.current && message) {
      ws.current.send(`/msg targetUser ${message}`);
      setMessage('');
    }
  }

  const listUsers = () => {
    if (ws.current) {
      ws.current.send('/users');
    }
  }

  return (
    <div>
      {!isLoggedIn ? (
        <div>
          <input value={username} onChange={(e) => setUsername(e.target.value)} placeholder="Username" />
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Shared Password" />
          <button onClick={connect}>Connect</button>
        </div>
      ) : (
        <div>
          <h2>Users: {users.join(', ')}</h2>
          <button onClick={listUsers}>Refresh Users</button>
          
          <div>
            <h3>Incoming Messages</h3>
            <div style={{ height: '300px', overflowY: 'scroll', border: '1px solid #ccc', padding: '10px' }}>
              {messages.length === 0 ? (
                <p>No messages yet.</p>
              ) : (
                messages.map((msg, i) => (
                  <p key={i} style={{ margin: '5px 0' }}>
                    <strong>{msg.from}:</strong> {msg.payload}
                  </p>
                ))
              )}
              <div ref={messagesEndRef} />
            </div>
          </div>
          
          <div style={{ marginTop: '20px' }}>
            <input 
              value={message} 
              onChange={(e) => setMessage(e.target.value)} 
              placeholder="Type your message" 
              style={{ width: '70%', padding: '5px' }} 
            />
            <button onClick={sendMessage} style={{ padding: '5px 10px', marginLeft: '10px' }}>
              Send
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default App