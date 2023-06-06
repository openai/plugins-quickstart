const express = require('express');
const cors = require('cors');
const fs = require('fs');

const app = express();
app.use(express.json());
app.use(cors({ origin: 'https://chat.openai.com' }));

// Keep track of todo's. Does not persist if the Node.js process is restarted.
const TODOS = {};

app.post('/todos/:username', (req, res) => {
  const username = req.params.username;
  if (!TODOS[username]) {
    TODOS[username] = [];
  }
  TODOS[username].push(req.body.todo);
  res.status(200).send('OK');
});

app.get('/todos/:username', (req, res) => {
  const username = req.params.username;
  res.status(200).json(TODOS[username] || []);
});

app.delete('/todos/:username', (req, res) => {
  const username = req.params.username;
  const todoIdx = req.body.todo_idx;
  // fail silently, it's a simple plugin
  if (0 <= todoIdx && todoIdx < TODOS[username].length) {
    TODOS[username].splice(todoIdx, 1);
  }
  res.status(200).send('OK');
});

app.get('/logo.png', (req, res) => {
  res.sendFile('logo.png', { root: __dirname }, (err) => {
    if (err) {
      res.status(500).send(err);
    }
  });
});

app.get('/.well-known/ai-plugin.json', (req, res) => {
  fs.readFile('./.well-known/ai-plugin.json', 'utf8', (err, data) => {
    if (err) {
      res.status(500).send(err);
    } else {
      res.set('Content-Type', 'text/json');
      res.status(200).send(data);
    }
  });
});

app.get('/openapi.yaml', (req, res) => {
  fs.readFile('openapi.yaml', 'utf8', (err, data) => {
    if (err) {
      res.status(500).send(err);
    } else {
      res.set('Content-Type', 'text/yaml');
      res.status(200).send(data);
    }
  });
});

app.listen(5003, '0.0.0.0', () => {
  console.log('App is running on port 5003');
});
