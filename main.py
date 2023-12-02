import json
import os
import quart
import quart_cors
from quart import request

app = quart_cors.cors(quart.Quart(__name__), allow_origin="https://chat.openai.com")

# Get GitHub Codespaces domain if any
def construct_codespaces_url():
    codespace_name = os.environ.get('CODESPACE_NAME')
    if not codespace_name:
        return None  # Return None if there's no codespace name
    port = 5003  # Example port number
    return f"https://{codespace_name}-{port}.app.github.dev"

# Keep track of todo's. Does not persist if Python session is restarted.
_TODOS = {}

@app.post("/todos/<string:username>")
async def add_todo(username):
    request = await quart.request.get_json(force=True)
    if username not in _TODOS:
        _TODOS[username] = []
    _TODOS[username].append(request["todo"])
    return quart.Response(response='OK', status=200)

@app.get("/todos/<string:username>")
async def get_todos(username):
    return quart.Response(response=json.dumps(_TODOS.get(username, [])), status=200)

@app.delete("/todos/<string:username>")
async def delete_todo(username):
    request = await quart.request.get_json(force=True)
    todo_idx = request["todo_idx"]
    # fail silently, it's a simple plugin
    if 0 <= todo_idx < len(_TODOS[username]):
        _TODOS[username].pop(todo_idx)
    return quart.Response(response='OK', status=200)

@app.get("/logo.png")
async def plugin_logo():
    filename = 'logo.png'
    return await quart.send_file(filename, mimetype='image/png')

@app.get("/.well-known/ai-plugin.json")
async def plugin_manifest():
    codespaces_url = construct_codespaces_url()
    with open("./.well-known/ai-plugin.json", "r") as f:
        data = json.load(f)
    
    # Update URL properties only if codespaces_url is not None
    if codespaces_url:
        data["api"]["url"] = data["api"]["url"].replace("localhost:5003", codespaces_url)
        data["logo_url"] = data["logo_url"].replace("localhost:5003", codespaces_url)

    return quart.Response(json.dumps(data), mimetype="application/json")

@app.get("/openapi.yaml")
async def openapi_spec():
    codespaces_url = construct_codespaces_url()
    with open("openapi.yaml", "r") as f:
        text = f.read()
    
    # Replace the URL only if codespaces_url is not None
    if codespaces_url:
        updated_text = text.replace("localhost:5003", codespaces_url)
    else:
        updated_text = text

    return quart.Response(updated_text, mimetype="text/yaml")



def main():
    app.run(debug=True, host="localhost", port=5003)

if __name__ == "__main__":
    main()
