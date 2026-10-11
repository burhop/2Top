"""Official MCP adapters for the one authoritative, running Tidal Atlas scene.

HTTP is mounted by :mod:`studio.app` against its SceneService.  The stdio entry
point is deliberately a proxy: it never constructs a second SceneService.
"""

from __future__ import annotations

from . import __version__

import argparse
import asyncio
import inspect
import json
import logging
import os
from collections.abc import Awaitable, Callable
from contextlib import asynccontextmanager
from typing import Any, Protocol
from urllib.parse import urlsplit

import httpx
import jsonschema
from mcp import types
from mcp.server.lowlevel import Server
from mcp.server.stdio import stdio_server

LOGGER = logging.getLogger(__name__)
TOOL_NAMES = frozenset(
    {
        "get_scene",
        "get_selection",
        "create_geometry",
        "update_geometry",
        "delete_geometry",
        "set_style",
        "set_view",
        "select",
        "batch",
        "undo",
        "redo",
        "load_recipe",
        "set_keyframe",
        "delete_keyframe",
        "edit_keyframe",
    }
)


class StudioBackend(Protocol):
    """The shared service contract; a remote proxy may implement it async."""

    def tool_definitions(
        self,
    ) -> list[dict[str, Any]] | Awaitable[list[dict[str, Any]]]: ...

    def invoke(
        self, tool: str, args: dict[str, Any], actor: str = "mcp"
    ) -> dict[str, Any] | Awaitable[dict[str, Any]]: ...


async def _resolve(value: Any) -> Any:
    return await value if inspect.isawaitable(value) else value


def _error(code: str, message: str, **details: Any) -> dict[str, Any]:
    return {"ok": False, "error": {"code": code, "message": message, **details}}


def _tool_result(result: dict[str, Any]) -> types.CallToolResult:
    """Keep domain failures distinguishable from successful scene mutations."""
    return types.CallToolResult(
        content=[
            types.TextContent(type="text", text=json.dumps(result, allow_nan=False))
        ],
        structuredContent=result,
        isError=result.get("ok") is False or bool(result.get("error")),
    )


def create_mcp_server(backend: StudioBackend) -> Server:
    """Build a real SDK server using the service's own tool schemas and commands."""

    async def definitions() -> list[dict[str, Any]]:
        return [
            entry
            for entry in await _resolve(backend.tool_definitions())
            if entry["name"] in TOOL_NAMES
        ]

    async def list_tools(_context: Any, _params: Any) -> types.ListToolsResult:
        return types.ListToolsResult(
            tools=[types.Tool(**entry) for entry in await definitions()]
        )

    async def call_tool(
        _context: Any, params: types.CallToolRequestParams
    ) -> types.CallToolResult:
        try:
            catalog = {entry["name"]: entry for entry in await definitions()}
            if params.name not in catalog:
                return _tool_result(
                    _error("unknown_tool", "This studio tool is not available.")
                )
            arguments = params.arguments or {}
            # Do not depend on host/browser-side schema validation. This is also
            # applied by SceneService for every entry point, including manual UI.
            jsonschema.Draft202012Validator(
                catalog[params.name]["inputSchema"]
            ).validate(arguments)
            result = await _resolve(backend.invoke(params.name, arguments, actor="mcp"))
            return _tool_result(result)
        except jsonschema.ValidationError as exc:
            path = ".".join(str(part) for part in exc.absolute_path)
            return _tool_result(_error("invalid_arguments", exc.message, path=path))
        except (httpx.HTTPError, ConnectionError, TimeoutError):
            return _tool_result(
                _error(
                    "studio_unavailable",
                    "Cannot reach the running studio. No success was confirmed; "
                    "read the scene before retrying, and reuse request_id for a mutation retry.",
                )
            )
        except Exception as exc:
            # Shared command errors expose a public result; programming errors
            # stay in stderr rather than leaking stack traces through a tool.
            if hasattr(exc, "as_dict"):
                return _tool_result({"ok": False, "error": exc.as_dict()})
            if hasattr(exc, "to_dict"):
                value = exc.to_dict()
                return _tool_result(
                    value if "ok" in value else {"ok": False, "error": value}
                )
            LOGGER.exception("Studio tool failed: %s", params.name)
            return _tool_result(
                _error("command_failed", "The studio could not complete this command.")
            )

    return Server(
        "tidal-atlas",
        version=__version__,
        instructions=(
            "Edit the same scene displayed in Tidal Atlas. First read get_scene. "
            "For every mutation supply its expected_revision; use a unique request_id "
            "and reuse it only for an identical retry. On a revision conflict read the "
            "scene again before deciding what to change. Batch is atomic. No arbitrary "
            "code or expression execution is available."
        ),
        on_list_tools=list_tools,
        on_call_tool=call_tool,
    )


def create_mcp_http_app(backend: StudioBackend) -> tuple[Any, Callable[..., Any]]:
    """Return (ASGI app, lifespan factory) for mounting at ``/mcp``.

    Parent lifespan must enter ``async with mcp_lifespan():``; mounted Starlette
    applications do not automatically receive ASGI lifespan events.
    """
    server = create_mcp_server(backend)
    app = server.streamable_http_app(
        streamable_http_path="/",
        json_response=True,
        stateless_http=True,
        max_request_body_size=256 * 1024,
        host="127.0.0.1",
    )

    @asynccontextmanager
    async def lifespan():
        async with server.session_manager.run():
            yield

    return app, lifespan


class RemoteStudioBackend:
    """Forward stdio tools to the running app; no fallback or private scene."""

    def __init__(self, url: str, client: httpx.AsyncClient | None = None):
        parsed = urlsplit(url)
        if (
            parsed.scheme != "http"
            or parsed.hostname not in {"localhost", "127.0.0.1", "::1"}
            or parsed.username
            or parsed.password
            or parsed.query
            or parsed.fragment
            or parsed.path not in {"", "/"}
        ):
            raise ValueError(
                "Studio URL must be a loopback HTTP origin, such as http://127.0.0.1:8000"
            )
        self.url = url.rstrip("/")
        self.client = client

    async def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        if self.client is not None:
            response = await self.client.request(method, self.url + path, **kwargs)
        else:
            async with httpx.AsyncClient(
                timeout=30, follow_redirects=False, trust_env=False
            ) as client:
                response = await client.request(method, self.url + path, **kwargs)
        # Preserve domain conflicts/validation failures rather than reporting a
        # generic networking failure. Never silently retry a mutation.
        try:
            result = response.json()
        except ValueError:
            response.raise_for_status()
            raise ValueError("The running studio returned non-JSON data") from None
        if not response.is_success:
            if isinstance(result, dict) and result.get("ok") is False:
                return result
            response.raise_for_status()
        return result

    async def tool_definitions(self) -> list[dict[str, Any]]:
        result = await self._request("GET", "/api/tools")
        return result["tools"] if isinstance(result, dict) else result

    async def invoke(
        self, tool: str, args: dict[str, Any], actor: str = "mcp"
    ) -> dict[str, Any]:
        if tool not in TOOL_NAMES:
            return _error("unknown_tool", "This studio tool is not available.")
        return await self._request(
            "POST",
            f"/api/tools/{tool}",
            json=args,
            headers={"X-Studio-Actor": "mcp"},
        )


async def run_stdio(url: str) -> None:
    """Use the official SDK transport and a proxy to the shared HTTP service."""
    async with httpx.AsyncClient(
        timeout=30, follow_redirects=False, trust_env=False
    ) as client:
        server = create_mcp_server(RemoteStudioBackend(url, client))
        async with stdio_server() as (read, write):
            await server.run(read, write, server.create_initialization_options())


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Tidal Atlas MCP stdio proxy (start the web app first)"
    )
    parser.add_argument(
        "--studio-url", default=os.getenv("TIDAL_STUDIO_URL", "http://127.0.0.1:8000")
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    args = parser.parse_args()
    logging.basicConfig(level=logging.WARNING)
    asyncio.run(run_stdio(args.studio_url))


if __name__ == "__main__":
    main()
