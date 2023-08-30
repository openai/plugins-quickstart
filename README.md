# ChatGPT plugins quickstart

Get a todo list ChatGPT plugin up and running in under 5 minutes using Python. This plugin is designed to work in conjunction with the [ChatGPT plugins documentation](https://platform.openai.com/docs/plugins). If you do not already have plugin developer access, please [join the waitlist](https://openai.com/waitlist/plugins).

## Setup locally

To install the required packages for this plugin, run the following command:

```bash
pip install -r requirements.txt
```

To run the plugin, enter the following command:

```bash
python main.py
```

Once the local server is running:

1. Navigate to https://chat.openai.com. 
2. In the Model drop down, select "Plugins" (note, if you don't see it there, you don't have access yet).
3. Select "Plugin store"
4. Select "Develop your own plugin"
5. Enter in `localhost:5003` since this is the URL the server is running on locally, then select "Find manifest file".

The plugin should now be installed and enabled! You can start with a question like "What is on my todo list" and then try adding something to it as well! 

## Setup remotely

### GitPod
[![Open in Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/github.com/openai/plugins-quickstart)

When using Gitpod, it will run `pip install -r requirements.txt` and `python main.py` for you so you do not need to complete those steps. 

Instead, you will need to update `/.well-known/ai-plugin.json` and `openapi.yaml` to replace `http://localhost:5003/` with the URL for your workspace. This can be found by clicking on `Ports` in the bottom panel and copying the value shown in the `Address` column. Once you have made those 3 replacements (2 in `ai-plugin.json` and 1 in `openapi.yaml`) the above instructions can be used to install the development plugin (using the GitPod address instead of `localhost:5003`)

### Cloudflare workers

### Code Sandbox

### Replit

## Getting help

If you run into issues or have questions building a plugin, please join our [Developer community forum](https://community.openai.com/c/chat-plugins/20).
