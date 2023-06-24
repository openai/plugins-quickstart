import json
import os
import subprocess

from urllib.parse import unquote
import quart
from quart import request
from quart_cors import cors

app = quart.Quart(__name__)
app = cors(app, allow_origin="https://chat.openai.com")


@app.post("/execute")
async def execute_command():
    request_data = await quart.request.get_json(force=True)
    command = request_data.get("command", "")
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
        return quart.Response(response=json.dumps({"output": result.stdout}), status=200)
    except subprocess.CalledProcessError as e:
        return quart.Response(response=json.dumps({"error": str(e), "output": e.output}), status=400)


@app.post("/create_env")
async def create_env():
    request_data = await quart.request.get_json(force=True)
    env_name = request_data.get("env_name", "")
    command = f"conda create -n {env_name} python=3.10 -y"
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
        return quart.Response(response=json.dumps({"output": result.stdout}), status=200)
    except subprocess.CalledProcessError as e:
        return quart.Response(response=json.dumps({"error": str(e), "output": e.output}), status=400)


@app.post("/run_script")
async def run_script():
    request_data = await quart.request.get_json(force=True)
    env_name = request_data.get("env_name", "")
    script_path = request_data.get("script_path", "")
    command = f"conda run -n {env_name} python {script_path}"
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
        return quart.Response(response=json.dumps({"output": result.stdout}), status=200)
    except subprocess.CalledProcessError as e:
        return quart.Response(response=json.dumps({"error": str(e), "output": e.output}), status=400)


@app.get("/files/<path:filename>")
async def get_file(filename):
    filename = unquote(filename)  # URL-decode the filename
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            content = f.read()
        return quart.Response(response=json.dumps({"content": content}), status=200)
    else:
        return quart.Response(response='File not found', status=404)


@app.post("/files/<path:filename>")
async def modify_file(filename):
    request_data = await quart.request.get_json(force=True)
    filename = unquote(filename)  # URL-decode the filename
    content = request_data.get("content", "")
    with open(filename, 'w') as f:
        f.write(content)
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


@app.after_request
async def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = 'https://chat.openai.com'
    response.headers['Access-Control-Allow-Headers'] = '*'
    response.headers['Access-Control-Allow-Methods'] = '*'
    return response


@app.route("/files/<path:filename>", methods=['OPTIONS'])
async def options_files(filename):
    response = quart.Response(response='', status=200)
    response.headers['Access-Control-Allow-Origin'] = "https://chat.openai.com"
    response.headers['Access-Control-Allow-Headers'] = 'content-type,openai-conversation-id,openai-ephemeral-user-id'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST'
    return response


def main():
    app.run(debug=True, host="0.0.0.0", port=5003)


if __name__ == "__main__":
    main()
