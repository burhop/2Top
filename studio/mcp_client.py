"""Explicit real MCP calls for protocol walkthroughs, not a model/inference host."""

import argparse
import asyncio
import json
from pathlib import Path

import httpx2
from mcp import Client
from mcp.client.streamable_http import streamable_http_client

from .mcp_server import RemoteStudioBackend


async def call(url, tool="get_scene", arguments=None, *, catalog=False):
    # Reuse the adapter's loopback-origin contract without forwarding HTTP tools.
    RemoteStudioBackend(url)
    async with httpx2.AsyncClient(trust_env=False, timeout=15) as http:
        transport = streamable_http_client(url.rstrip("/") + "/mcp/", http_client=http)
        async with Client(transport) as client:
            if catalog:
                result = await client.list_tools()
                return {
                    "transport": "MCP Streamable HTTP",
                    "model_inference": False,
                    "tools": [
                        {
                            "name": tool.name,
                            "description": tool.description,
                            "inputSchema": tool.input_schema,
                        }
                        for tool in result.tools
                    ],
                }
            result = await client.call_tool(tool, arguments or {})
            return result.structured_content or {
                "ok": False,
                "error": {
                    "code": "missing_result",
                    "message": "MCP returned no structured result",
                },
            }


def main():
    parser = argparse.ArgumentParser(
        description="Explicit official MCP protocol client. No model inference; no automatic writes or retries."
    )
    parser.add_argument("--studio-url", default="http://127.0.0.1:8000")
    parser.add_argument("--tool", default="get_scene")
    parser.add_argument(
        "--arguments",
        type=Path,
        help="JSON arguments file; mutations require an explicit expected_revision",
    )
    parser.add_argument(
        "--catalog", action="store_true", help="Read-only tool discovery"
    )
    args = parser.parse_args()
    try:
        arguments = (
            json.loads(args.arguments.read_text(encoding="utf-8"))
            if args.arguments
            else {}
        )
        if not isinstance(arguments, dict):
            raise ValueError("Arguments must be a JSON object")
        result = asyncio.run(
            call(args.studio_url, args.tool, arguments, catalog=args.catalog)
        )
        print(json.dumps(result, ensure_ascii=True, allow_nan=False))
        return 1 if result.get("ok") is False or result.get("error") else 0
    except Exception as exc:
        print(
            json.dumps(
                {"ok": False, "error": {"code": "client_error", "message": str(exc)}}
            )
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
