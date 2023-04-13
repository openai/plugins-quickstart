export default `
openapi: 3.0.1
info:
  title: GitHub Repositories Search API
  description: A plugin that allows the user to search for GitHub repositories using ChatGPT.
  version: 'v0.0.1'
servers:
  - url: https://repoai.examples.workers.dev
paths:
  /search:
    get:
      operationId: searchRepos
      summary: Search repositories by a query parameter
      parameters:
        - name: q
          in: query
          description: The query to search for
          required: true
          schema:
            type: string
      responses:
        "200":
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/getSearchResponse'
components:
  schemas:
    getSearchResponse:
      type: object
      properties:
        repos:
          type: array
          items:
            type: object
            properties:
              name:
                type: string
              description:
                type: string
              stars:
                type: number
              url:
                type: string
`