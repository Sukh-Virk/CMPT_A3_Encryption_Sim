const WebSocket = require('ws');
const net = require('net');

const wss = new WebSocket.Server({ port: 8080 });

wss.on('connection', (ws) => {
  const client = net.createConnection({ host: 'localhost', port: 5000 });
  
  ws.on('message', (data) => {
    client.write(data.toString() + '\n');
  });
  
  client.on('data', (data) => {
  ws.send(data.toString().trim());  // Trim to remove \n
    });

  
  client.on('close', () => ws.close());
  ws.on('close', () => client.end());
  
  client.on('error', (err) => console.error('TCP error:', err));
  ws.on('error', (err) => console.error('WS error:', err));
});

console.log('Proxy running on ws://localhost:8080');