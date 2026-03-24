const WebSocket = require('ws');
const { spawn } = require('child_process');

const wss = new WebSocket.Server({ port: 3001 });

wss.on('connection', (ws) => {
  console.log('React client connected');
  
  const clientProcess = spawn('python', ['client.py'], {
    cwd: __dirname,
    stdio: ['pipe', 'pipe', 'pipe']
  });
  
  ws.on('message', (data) => {
    const msg = data.toString();
    console.log('Sending to client.py:', msg);
    clientProcess.stdin.write(msg + '\n');
  });
  
  clientProcess.stdout.on('data', (data) => {
    const output = data.toString();
    console.log('Received from client.py:', output);
    ws.send(output);  // Forward raw output to React for parsing
  });
  
  clientProcess.stderr.on('data', (data) => {
    console.error('Client stderr:', data.toString());
  });
  
  clientProcess.on('close', (code) => {
    console.log('Client.py exited with code', code);
    ws.close();
  });
  
  ws.on('close', () => {
    clientProcess.kill();
  });
});

console.log('Backend WebSocket server running on ws://localhost:3001');