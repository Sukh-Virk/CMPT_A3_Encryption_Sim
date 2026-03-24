const WebSocket = require('ws');
const { spawn } = require('child_process');

const wss = new WebSocket.Server({ port: 3001 });
const clients = new Map(); // Map of ws -> { process, username, password, buffer }

wss.on('connection', (ws) => {
  console.log('React client connected');
  
  let username = null;
  let password = null;
  let clientProcess = null;
  let stdoutBuffer = '';
  
  ws.on('message', (msg) => {
    const message = msg.toString().trim();
    console.log('Received from React:', message);
    
    if (!clientProcess) {
      // First message should be username, second should be password
      if (username === null) {
        username = message;
        console.log(`Username set: ${username}`);
        return;
      } 
      
      if (password === null && username !== null) {
        password = message;
        console.log(`Password set for ${username}`);
        
        // Spawn Python client with username and password
        console.log(`Spawning Python client for ${username}`);
        clientProcess = spawn('python', ['client.py', username, password], { 
          cwd: __dirname,
          stdio: ['pipe', 'pipe', 'pipe']
        });
        
        clients.set(ws, { process: clientProcess, username, password });
        
        clientProcess.on('error', (err) => {
          console.error(`client.py spawn error for ${username}:`, err);
          ws.send('Error: Failed to start client');
        });
        
        clientProcess.on('exit', (code, sig) => {
          console.log(`client.py exited for ${username}`, code, sig);
          clients.delete(ws);
          ws.send('Error: Client disconnected');
        });
        
        // Handle stdout from Python client
        clientProcess.stdout.on('data', (chunk) => {
          stdoutBuffer += chunk.toString();
          let lines = stdoutBuffer.split('\n');
          stdoutBuffer = lines.pop();
          
          lines.forEach(line => {
            line = line.trim();
            if (!line) return;
            
            console.log(`From Python client (${username}):`, line);
            
            // Forward all output to React client
            if (ws.readyState === ws.OPEN) {
              ws.send(line);
            }
          });
        });
        
        clientProcess.stderr.on('data', (data) => {
          console.error(`client.py stderr (${username}):`, data.toString());
          if (ws.readyState === ws.OPEN) {
            ws.send(`Error: ${data.toString()}`);
          }
        });
        
        return;
      }
    }
    
    // Forward message to Python client if process exists
    if (clientProcess && !clientProcess.killed) {
      console.log(`Forwarding to Python client (${username}):`, message);
      clientProcess.stdin.write(message + '\n');
    }
  });
  
  ws.on('close', () => {
    console.log(`WebSocket closed for ${username || 'unknown'}`);
    if (clientProcess && !clientProcess.killed) {
      clientProcess.kill();
    }
    clients.delete(ws);
  });
  
  ws.on('error', (err) => {
    console.error('WebSocket error:', err);
  });
});

wss.on('listening', () => {
  console.log('WebSocket server listening on ws://localhost:3001');
});

wss.on('error', (err) => {
  console.error('WebSocket server error:', err);
});