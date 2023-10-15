const express = require("express");
const app = express();
const port = 3000;

const fs = require("fs").promises;
const path = require("path");

app.get("/", (req, res) => {
  res.send("Hello, World!");
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
