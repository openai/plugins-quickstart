import json
import yaml
import quart
import quart_cors
from quart import request

app = quart_cors.cors(quart.Quart(__name__), allow_origin="https://chat.openai.com")

# The file to store the todos
TODO_FILE = "todos.yaml"

# Load the todos from the file
try:
    with open(TODO_FILE, "r" , encoding="utf-8") as f:
        _TODOS = yaml.safe_load(f)
except FileNotFoundError:
    _TODOS = {}

@app.post("/todos/<string:username>")
async def add_todo(username):
    request_data = await request.get_json(force=True)
    if username not in _TODOS:
        _TODOS[username] = []
    _TODOS[username].append(request_data["todo"])
    with open(TODO_FILE, "w" , encoding="utf-8") as f:
        yaml.safe_dump(_TODOS, f, allow_unicode=True)
    print(f"Received POST request: {request_data}")
    return quart.Response(response='OK', status=200)

@app.get("/todos/<string:username>")
async def get_todos(username):
    return quart.Response(response=json.dumps(_TODOS.get(username, [])), status=200)

@app.delete("/todos/<string:username>")
async def delete_todo(username):
    request_data = await request.get_json(force=True)
    todo_idx = request_data["todo_idx"]
    if 0 <= todo_idx < len(_TODOS[username]):
        _TODOS[username].pop(todo_idx)
        with open(TODO_FILE, "w" , encoding="utf-8") as f:
            yaml.safe_dump(_TODOS, f)
    return quart.Response(response='OK', status=200)

@app.get("/logo.png")
async def plugin_logo():
    filename = 'logo.png'
    return await quart.send_file(filename, mimetype='image/png')

@app.get("/.well-known/ai-plugin.json")
async def plugin_manifest():
    host = request.headers['Host']
    with open("./.well-known/ai-plugin.json") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/json")

@app.get("/openapi.yaml")
async def openapi_spec():
    host = request.headers['Host']
    with open("openapi.yaml") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/yaml")

def main():
    app.run(debug=True, host="0.0.0.0", port=5003)

if __name__ == "__main__":
    main()
