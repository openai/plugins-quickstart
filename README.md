# ChatGPT plugins quickstart

Get a Todo list ChatGPT plugin up and running in under 5 minutes using Python. If you do not already have plugin developer access, please [join the waitlist](https://openai.com/waitlist/plugins).

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/openai/plugins-quickstart?devcontainer_path=/.devcontainer/basics/devcontainer.json)

## Local Setup

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

## GitHub Codespaces Setup
_A codespace is a development environment that's hosted in the cloud. You can build and run this plugin via a GitHub Codespace by following the directions below:_ 

1. Open this environment in a GitHub Codespace by choosing "Use this template" > "Open in Codespace" as pictured below.
<img width="191" alt="Green button titled use this template with dropdown options of create new repository and open in codespace" src="https://user-images.githubusercontent.com/22990146/235506864-7be45716-4b61-4986-97b1-e69e3f3a4df4.png">

2. Allow the Codespace a few minutes to finish installing all necessary dependencies. It may take awhile, but keep in mind that GitHub Codespaces is running all the install commands, so you don't have to.

3. Once everything is installed, you should see that a forwarded port is now running the plugin. **Set the port visibility to public.** 
<img width="1412" alt="Choosing public port visibility for forwarded port" src="https://user-images.githubusercontent.com/22990146/235510002-1a9ef89b-e12c-4145-8119-45daed452028.png">

4. Copy the forwarded port's local address. It should follow this naming convention 

`https://<GITHUB_USER_HANDLE>-<RANDOMLY_GENERATED_PHRASE>-<RANDOMLY_GENERATED_ALPHANUMERIC_STRING>-5003.preview.app.github.dev`

5. Navigate to https://chat.openai.com. 

6. In the Model drop down, select "Plugins" (note, if you don't see it there, you don't have access yet).

7. Select "Plugin store"

8. Select "Develop your own plugin"

9. Enter in the local address to your forwarded port (the one you copied in Step 3), then select "Find manifest file".


The plugin should now be installed and enabled! You can start with a question like "What is on my todo list" and then try adding something to it as well! 

## Getting help

If you run into issues or have questions building a plugin, please join our [Developer community forum](https://community.openai.com/c/chat-plugins/20).
