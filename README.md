# mcp-server-modal

https://docs.google.com/document/d/1DcrSKbcsXrzCoyMe0XtAsDcE3IgBV1bLirUG80VxPq8/edit?tab=t.0

An MCP Server that allows users to deploy python scripts to [modal](https://modal.com/).

## Installation

Make sure that modal is setup:

```
pip install modal
python3 -m modal setup
```

Then setup the server with the filesystem server in your Claude desktop app:

```
{
   "mcpServers": {
        "mcp-server-modal": {
            "command": "uv",
            "args": [
                "--directory",
                "/path/to/mcp-server-modal",
                "run",
                "modal-server"
            ]
        },
        "filesystem": {
			"command": "npx",
			"args": [
				"-y",
				"@modelcontextprotocol/server-filesystem",
				"/Users/user/Desktop/",
                "/path/to/other/dir"
			]
		}
   }
}
```

## Usage

In claude, give a python script and ask it to create a modal application and deploy it for you. After code generation, you will get a link to the modal application which you can try out and share with others.

## Development

```
npx @modelcontextprotocol/inspector uv --directory /path/to/mcp-server-modal run modal-server
```
