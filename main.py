import json
from typing import Dict, List

import quart
import quart_cors
from quart import Quart, Response, jsonify, request

app = quart_cors.cors(Quart(__name__), allow_origin="https://chat.openai.com")

# Keep track of todo's. Does not persist if Python session is restarted.
_TODOS: Dict[str, List[str]] = {}

@app.post("/todos/<string:username>")
async def add_todo(username: str) -> Response:
    data = await request.get_json(force=True)
    if username not in _TODOS:
        _TODOS[username] = []
    _TODOS[username].append(data["todo"])
    return Response(response='OK', status=200)

@app.get("/todos/<string:username>")
async def get_todos(username: str) -> Response:
    return jsonify(_TODOS.get(username) or [])

@app.delete("/todos/<string:username>")
async def delete_todo(username: str) -> Response:
    data = await request.get_json(force=True)
    todo_idx = data["todo_idx"]
    # fail silently, it's a simple plugin
    if 0 <= todo_idx < len(_TODOS.get(username, [])):
        _TODOS[username].pop(todo_idx)
    return Response(response='OK', status=200)

@app.get("/logo.png")
async def plugin_logo() -> Response:
    filename = 'logo.png'
    return await quart.send_file(filename, mimetype='image/png')

@app.get("/.well-known/ai-plugin.json")
async def plugin_manifest() -> Response:
    with open("./.well-known/ai-plugin.json") as f:
        text = f.read()
    return Response(text, mimetype="text/json")

@app.get("/openapi.yaml")
async def openapi_spec() -> Response:
    with open("openapi.yaml") as f:
        text = f.read()
    return Response(text, mimetype="text/yaml")

def main() -> None:
    app.run(debug=True, host="0.0.0.0", port=5003)

if __name__ == "__main__":
    main()
