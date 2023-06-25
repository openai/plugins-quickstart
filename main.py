import json
import os
import sys
import subprocess
from urllib.parse import unquote
import quart
from quart import request
from quart_cors import cors
import re

app = quart.Quart(__name__)
app = cors(app, allow_origin="https://chat.openai.com")


def remove_ansi_escape_sequences(text):
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)


@app.post("/initialize")
async def initialize_plugin():
    request_data = await quart.request.get_json(force=True)
    env_name = request_data.get("env_name", "debuggerGPT")
    try:
        # Check if the specified conda environment exists
        envs = subprocess.check_output(['conda', 'env', 'list']).decode('utf-8')
        if env_name not in envs:
            # Create the specified conda environment
            subprocess.run(['conda', 'create', '-n', env_name, 'python=3.10'], check=True)

        instructions = {
            "message": "Initialization successful. The conda environment '" + env_name + "' is ready to use.",
            "instructions": "As a Python Code Debugging Plugin, I can help you debug Python code files,"
                            " manage Python environments, and manipulate files on your computer."
                            " Here are the main capabilities and how to use them: \n\n1) "
                            "Initialization: Before using the plugin, initialize it by running the 'initialize_plugin' function. "
                            "This function sets up a conda environment for running scripts. The default environment is 'debuggerGPT', "
                            "but you can specify a different one during initialization or when running a script. \n\n2) "
                            "Execute Shell Commands: You can ask me to 'execute a command' and provide the command as a string. "
                            "If you want to run the command in a specific environment, include the 'env_name' in your request. "
                            "\n\n3) Run Python Scripts: You can ask me to 'run a Python script in a specific environment' "
                            "and provide the path to the script and the name of the environment. Before running a script for the first time, "
                            "I will check the code for non-native dependencies and ensure they are installed in the chosen environment. \n\n4) "
                            "Modify Files: You can use the 'modify a file' command to update the local file of the code. "
                            "\n\n5) Install Python Packages: You can ask me to 'install Python packages' and provide a list of packages to install in a specific environment. "
                            "\n\n6) Debug Code: To debug a code, run the code, examine the output and error messages, "
                            "decide how to fix the code, and then use the 'modify a file' command to update the code. "
                            "Repeat this process until the code runs without errors."
        }
        return quart.Response(response=json.dumps(instructions), status=200)
    except subprocess.CalledProcessError as e:
        return quart.Response(response=f'Error during initialization: {str(e)}', status=400)


@app.post("/execute")
async def execute_command():
    request_data = await quart.request.get_json(force=True)
    command = request_data.get("command", "")
    env_name = request_data.get("env_name", None)
    if env_name:
        command = f"conda run -n {env_name} {command}"
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
        return quart.Response(response=json.dumps({"output": result.stdout}), status=200)
    except subprocess.CalledProcessError as e:
        return quart.Response(response=json.dumps({"error": str(e), "output": e.output}), status=400)


@app.post("/install_packages")
async def install_packages():
    request_data = await quart.request.get_json(force=True)
    env_name = request_data.get("env_name", "debuggerGPT")  # Default to 'debuggerGPT' if not specified
    packages = request_data.get("packages", [])
    for package in packages:
        command = f"conda install -n {env_name} {package} -y"
        try:
            subprocess.run(command, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            return quart.Response(response=json.dumps({"error": str(e)}), status=400)
    return quart.Response(response='Packages installed successfully', status=200)


@app.post("/run_script")
async def run_script():
    request_data = await quart.request.get_json(force=True)
    env_name = request_data.get("env_name", "debuggerGPT")  # Default to 'debuggerGPT' if not specified
    script_path = request_data.get("script_path", "")
    command = f"conda run -n {env_name} python {script_path}"
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
        processed_output = remove_ansi_escape_sequences(result.stdout)
        # print(result.stderr)
        return quart.Response(response=json.dumps({"output": processed_output, "error": result.stderr}), status=200)
    except subprocess.CalledProcessError as e:
        # print(e.output)
        return quart.Response(response=json.dumps({"error": e.stderr, "output": e.output, "stderr": str(e)}),
                              status=400)


@app.get("/files/<path:filename>")
async def get_file(filename):
    filename = unquote(filename)
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            content = f.read()
        return quart.Response(response=json.dumps({"content": content}), status=200)
    else:
        return quart.Response(response='File not found', status=404)


@app.post("/files/<path:filename>")
async def modify_file(filename):
    request_data = await quart.request.get_json(force=True)
    filename = unquote(filename)
    fixes = request_data.get("fixes", [])

    with open(filename, 'r') as f:
        lines = f.readlines()

    for fix in fixes:
        if len(fix["lines"]) == 2:
            start_line, end_line = fix["lines"]
        elif len(fix["lines"]) == 1:
            start_line, end_line = fix["lines"], fix["lines"]
        new_code = fix["code"]
        indentation = fix["indentation"]
        indented_code = '\n'.join([indentation + line for line in new_code.split('\n')])
        lines[start_line - 1:end_line] = [indented_code + '\n']

    with open(filename, 'w') as f:
        f.writelines(lines)

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
