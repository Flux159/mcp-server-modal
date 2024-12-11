# mcp-server-modal

https://docs.google.com/document/d/1DcrSKbcsXrzCoyMe0XtAsDcE3IgBV1bLirUG80VxPq8/edit?tab=t.0

An MCP Server that allows users to deploy python scripts to [modal](https://modal.com/).

## Installation

Make sure that modal is setup:
```
pip install modal
python3 -m modal setup
```

Then setup the server in your Claude desktop app:
```
{
    "mcpServers": {
      "modal": {
        "command": "uvx",
        "args": ["mcp-server-modal"]
      }
    }
}
```

## Usage

In claude, give a python script and ask it to create a modal application and deploy it for you. After code generation, you will get a link to the modal application which you can try out and share with others.