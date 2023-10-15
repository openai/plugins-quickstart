const express = require("express");
const app = express();
const port = 3000;
const axios = require("axios");
const fs = require("fs").promises;
const path = require("path");

app.get("/", (req, res) => {
  res.send("Hello, World!");
});

// Passthrough route for creating a post on the authenticated user's profile
app.post("/users/:authorId/posts", async (req, res) => {
  const { authorId } = req.params;
  const payload = req.body;

  try {
    const response = await axios.post(
      `https://api.medium.com/v1/users/${authorId}/posts`,
      payload
    );
    res.status(201).json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json(error.response?.data || {});
  }
});

// Passthrough route for creating a post under a publication
app.post("/publications/:publicationId/posts", async (req, res) => {
  const { publicationId } = req.params;
  const payload = req.body;

  try {
    const response = await axios.post(
      `https://api.medium.com/v1/publications/${publicationId}/posts`,
      payload
    );
    res.status(201).json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json(error.response?.data || {});
  }
});

app.get("/logo.png", async (req, res) => {
  const filename = path.join(__dirname, "logo.png");
  res.sendFile(filename, { headers: { "Content-Type": "image/png" } });
});

app.get("/.well-known/ai-plugin.json", async (req, res) => {
  const host = req.headers.host;
  const filePath = path.join(__dirname, ".well-known", "ai-plugin.json");
  const text = await fs.readFile(filePath, "utf8");
  res.set("Content-Type", "application/json").send(text);
});

app.get("/openapi.yaml", async (req, res) => {
  const host = req.headers.host;
  const filePath = path.join(__dirname, "openapi.yaml");
  const text = await fs.readFile(filePath, "utf8");
  res.set("Content-Type", "text/yaml").send(text);
});

app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}/`);
});
