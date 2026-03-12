const express = require('express');
const http = require('http');
const WebSocket = require('ws');
const path = require('path');

const app = express();
const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

const clients = new Map();

app.use(express.static('.'));

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'));
});

wss.on('connection', (ws) => {
  let username = null;

  ws.on('message', (message) => {
    try {
      const data = JSON.parse(message);

      if (data.type === 'join') {
        username = data.user;
        clients.set(ws, username);
        broadcastUsers();
      } else if (data.type === 'message' && username) {
        broadcastMessage(username, data.message);
      }
    } catch (err) {
      console.error('Error:', err);
    }
  });

  ws.on('close', () => {
    if (username) {
      clients.delete(ws);
      broadcastUsers();
    }
  });
});

function broadcastUsers() {
  const users = Array.from(clients.values());
  const msg = JSON.stringify({ type: 'users', users });
  clients.forEach((_, ws) => {
    if (ws.readyState === WebSocket.OPEN) {
      ws.send(msg);
    }
  });
}

function broadcastMessage(user, message) {
  const msg = JSON.stringify({ type: 'message', user, message });
  clients.forEach((_, ws) => {
    if (ws.readyState === WebSocket.OPEN) {
      ws.send(msg);
    }
  });
}

const PORT = process.env.PORT || 8080;
server.listen(PORT, () => {
  console.log(`Chat server running on port ${PORT}`);
});
