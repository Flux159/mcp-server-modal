import json
import logging
from collections.abc import Sequence
import subprocess
from typing import Any

import httpx
import asyncio
from dotenv import load_dotenv
from mcp.server import Server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)
import mcp.types as types
from mcp.server import Server
from pydantic import AnyUrl

import mcp.server.stdio

from pydantic import AnyUrl

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("modal-server")

notes: dict[str, str] = {}

app = Server("modal-server")


@app.list_resources()
async def list_resources() -> list[Resource]:
    """List available resources."""
    return []


@app.read_resource()
async def handle_read_resource(uri: AnyUrl) -> str:
    try:
        return json.dumps({"result": "example"}, indent=2)
    except httpx.HTTPError as e:
        raise RuntimeError(f"API error: {str(e)}")


@app.list_prompts()
async def handle_list_prompts() -> list[types.Prompt]:
    """
    List available prompts.
    Each prompt can have optional arguments to customize its behavior.
    """
    return [
        types.Prompt(
            name="summarize-notes",
            description="Creates a summary of all notes",
            arguments=[
                types.PromptArgument(
                    name="style",
                    description="Style of the summary (brief/detailed)",
                    required=False,
                )
            ],
        )
    ]


@app.get_prompt()
async def handle_get_prompt(
    name: str, arguments: dict[str, str] | None
) -> types.GetPromptResult:
    """
    Generate a prompt by combining arguments with server state.
    The prompt includes all current notes and can be customized via arguments.
    """
    if name != "summarize-notes":
        raise ValueError(f"Unknown prompt: {name}")

    style = (arguments or {}).get("style", "brief")
    detail_prompt = " Give extensive details." if style == "detailed" else ""

    return types.GetPromptResult(
        description="Summarize the current notes",
        messages=[
            types.PromptMessage(
                role="user",
                content=types.TextContent(
                    type="text",
                    text=f"Here are the current notes to summarize:{detail_prompt}\n\n"
                    + "\n".join(
                        f"- {name}: {content}" for name, content in notes.items()
                    ),
                ),
            )
        ],
    )


@app.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List available tools.
    Each tool specifies its arguments using JSON Schema validation.
    """
    return [
        Tool(
            name="deploy",
            description="some description",
            inputSchema={
                "type": "object",
                "properties": {
                    "modal_path": {"type": "string"},
                },
                "required": ["message"],
            },
        )
    ]


@app.call_tool()
async def call_tool(
    name: str, arguments: Any
) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
    """Handle tool calls for weather forecasts."""
    if name != "deploy":
        raise ValueError(f"Unknown tool: {name}")
    if not isinstance(arguments, dict) or "modal_path" not in arguments:
        raise ValueError("Invalid forecast arguments")
    modal_path = arguments["modal_path"]

    try:
        res = deploy(modal_path)
        return [
            TextContent(type="text", text=json.dumps(f"Deploy result: {res}", indent=2))
        ]
    except httpx.HTTPError as e:
        raise RuntimeError(f"Ran in error: {str(e)}")


def deploy(modal_path: str = "model_app.py") -> str:
    """
    Deploy a model using Modal CLI command.

    Args:
        modal_path: Path to the modal file to deploy

    Returns:
        str: deployment result
    """
    try:
        # Run modal deploy command
        process = subprocess.run(["modal", "deploy", modal_path], capture_output=True, text=True)
        
        # Check if the command was successful
        if process.returncode == 0:
            return f"Deploy success: {process.stdout}"
        else:
            raise RuntimeError(f"Deploy failed: {process.stderr}")
        # if process.returncode == 0:
        #     message = f"Deployment successful: {stdout.decode()}"
        # else:
        #     message = f"Deployment failed: {stderr.decode()}"
        # return message
    except Exception as e:
        return f"Deployment error: {str(e)}"


async def main():
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())
