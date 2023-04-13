import { Hono } from 'hono'

import aiPlugin from './ai-plugin'
import openapi from './openapi'

const app = new Hono({ strict: false })

// The OpenAPI specification for the plugin
app.get('/openapi.yaml', async (c) => {
  return c.text(openapi, {
    headers: { 'Content-Type': 'text/yaml' }
  })
})

// Set up the AI plugin configuration endpoint
app.get('/.well-known/ai-plugin.json', async (c) => c.json(aiPlugin))

// The search endpoint, which is used by the ChatGPT client
app.get('/search', async (c) => {
  const query = c.req.query('q') || 'cloudflare workers'
  const url = `https://api.github.com/search/repositories?q=${query}`

  const resp = await fetch(url, {
    headers: {
      'Accept': 'application/vnd.github.v3+json',
      'User-Agent': 'RepoAI - Cloudflare Workers ChatGPT Plugin Example'
    }
  })

  if (!resp.ok) {
    throw new Error(await resp.text())
  }

  const json = await resp.json()
  const repos = json.items.map((item: any) => ({
    name: item.name,
    description: item.description,
    stars: item.stargazers_count,
    url: item.html_url
  }))

  return c.json({ repos })
})

// Handle errors
// This will log the error to the console and return a 500 status code to the browser
// You can view errors in the Cloudflare Workers dashboard or using `wrangler tail`
app.onError((err, c) => {
  console.error(`${err}`)
  return c.text('Something went wrong', 500)
})

// A simple health check endpoint
app.get("/", c => c.text('OK'))

export default app