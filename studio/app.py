"""Local single-user Tidal Atlas application and official MCP HTTP endpoint."""

from __future__ import annotations

import argparse
import json
import sys
from html import escape
from contextlib import asynccontextmanager
from pathlib import Path
from urllib.parse import urlparse

import uvicorn
from fastapi import FastAPI, Query, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.trustedhost import TrustedHostMiddleware

from . import __version__
from .service import SceneError, SceneService

STATIC = Path(__file__).parent / "static"


class RequestSizeLimitMiddleware:
    """Bound actual streamed bytes, including chunked MCP/HTTP requests."""

    def __init__(self, app, max_bytes=512_000):
        self.app = app
        self.max_bytes = max_bytes

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or scope["method"] not in {"POST", "PUT", "PATCH"}:
            return await self.app(scope, receive, send)
        chunks, size = [], 0
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            chunk = message.get("body", b"")
            size += len(chunk)
            if size > self.max_bytes:
                response = JSONResponse(
                    {
                        "ok": False,
                        "error": {
                            "code": "request_too_large",
                            "message": "Request exceeds 512 KB",
                        },
                    },
                    status_code=413,
                )
                return await response(scope, receive, send)
            chunks.append(chunk)
            if not message.get("more_body", False):
                break
        delivered = False

        async def bounded_receive():
            nonlocal delivered
            if not delivered:
                delivered = True
                return {
                    "type": "http.request",
                    "body": b"".join(chunks),
                    "more_body": False,
                }
            return await receive()

        await self.app(scope, bounded_receive, send)


def create_app(
    service: SceneService | None = None, *, enable_mcp: bool = True
) -> FastAPI:
    service = service or SceneService()
    if enable_mcp:
        from .mcp_server import create_mcp_http_app

        mcp_app, mcp_lifespan = create_mcp_http_app(service)

    @asynccontextmanager
    async def lifespan(app):
        if enable_mcp:
            async with mcp_lifespan():
                yield
        else:
            yield

    app = FastAPI(
        title="2Top / Tidal Atlas",
        version=__version__,
        lifespan=lifespan,
        docs_url=None,
        redoc_url=None,
    )
    app.state.scene_service = service
    app.add_middleware(RequestSizeLimitMiddleware)
    app.add_middleware(
        TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1", "[::1]"]
    )

    @app.middleware("http")
    async def local_origin_guard(request: Request, call_next):
        origin = request.headers.get("origin")
        # Prevent arbitrary websites from driving a local, unauthenticated studio.
        if origin and (urlparse(origin).scheme, urlparse(origin).netloc) != (
            request.url.scheme,
            request.url.netloc,
        ):
            return JSONResponse(
                {
                    "ok": False,
                    "error": {
                        "code": "origin_rejected",
                        "message": "Cross-origin requests are not allowed",
                    },
                },
                status_code=403,
            )
        if request.headers.get("sec-fetch-site") == "cross-site":
            return JSONResponse(
                {
                    "ok": False,
                    "error": {
                        "code": "origin_rejected",
                        "message": "Cross-site requests are not allowed",
                    },
                },
                status_code=403,
            )
        try:
            if int(request.headers.get("content-length", "0")) > 512_000:
                return JSONResponse(
                    {
                        "ok": False,
                        "error": {
                            "code": "request_too_large",
                            "message": "Request exceeds 512 KB",
                        },
                    },
                    status_code=413,
                )
        except ValueError:
            return JSONResponse(
                {
                    "ok": False,
                    "error": {
                        "code": "invalid_request",
                        "message": "Invalid content length",
                    },
                },
                status_code=400,
            )
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; connect-src 'self'; font-src 'self'; object-src 'none'; frame-ancestors 'none'"
        )
        return response

    @app.exception_handler(SceneError)
    async def scene_error(request, exc):
        return JSONResponse(
            {
                "ok": False,
                "error": exc.as_dict(),
                "revision": service.snapshot()["revision"],
            },
            status_code=exc.status,
        )

    async def body(request):
        try:
            value = json.loads(
                await request.body(),
                parse_constant=lambda value: (_ for _ in ()).throw(
                    ValueError("Non-finite JSON constant")
                ),
            )
        except (ValueError, UnicodeError, RecursionError) as exc:
            raise SceneError("invalid_json", "Request body must be valid JSON") from exc
        if not isinstance(value, dict):
            raise SceneError("invalid_arguments", "Request body must be a JSON object")
        return value

    @app.get("/")
    async def index():
        return FileResponse(STATIC / "index.html")

    @app.get("/api/docs", response_class=HTMLResponse)
    async def api_docs():
        cards = "".join(
            "<details><summary>"
            + escape(tool["name"])
            + "</summary><p>"
            + escape(tool["description"])
            + "</p><pre>"
            + escape(json.dumps(tool["inputSchema"], indent=2))
            + "</pre></details>"
            for tool in service.tool_definitions()
        )
        return HTMLResponse(
            """<!doctype html><html lang="en"><meta charset="utf-8"><title>Tidal Atlas · Tool reference</title>
        <meta name="viewport" content="width=device-width,initial-scale=1"><style>body{max-width:900px;margin:60px auto;padding:24px;background:#f4f2ec;color:#21312f;font:16px/1.6 system-ui}h1{font-size:40px}a{color:#266b64}code,pre{font:13px/1.5 monospace}pre{overflow:auto;padding:20px;background:#fff;border-radius:8px}details{padding:16px 0;border-bottom:1px solid #d8dcd6}summary{cursor:pointer;font-weight:600}</style>
        <a href="/">← Back to studio</a><h1>One canvas. Three ways to edit.</h1>
        <p>The manual UI, standard MCP server, and browser WebMCP tools call the same revision-checked scene service.</p>
        <p>MCP Streamable HTTP: <code>/mcp/</code>. Stdio: <code>python -m studio.mcp_server --studio-url http://127.0.0.1:8000</code>. Start the studio first.</p>
        <p>Read <code>get_scene</code>, then send a write with <code>expected_revision</code>. Add a unique <code>request_id</code> for a retry-safe request. Conflict means read the new scene and reconsider; never silently overwrite it.</p>
        <p>This is a single-user, local-only service. A registered WebMCP tool is not an AI connection. Browser and model support vary. Recipes contain numeric geometry, never executable expressions.</p>
        <p>Manual HTTP: GET <code>/api/scene</code>, GET <code>/api/recipe</code>, POST <code>/api/command</code> with an <code>op</code>. Named tools: POST <code>/api/tools/{name}</code> with schema arguments below.</p>"""
            + cards
            + "</html>"
        )

    @app.get("/api/scene")
    async def get_scene():
        return service.snapshot()

    @app.get("/api/geometry")
    async def geometry_paths(
        resolution: int = Query(180, ge=24, le=720),
        time: float | None = Query(None, ge=0, le=3600, allow_inf_nan=False),
    ):
        return service.geometry_paths(resolution=resolution, time_value=time)

    @app.get("/api/recipe")
    async def get_recipe():
        return service.recipe()

    @app.get("/api/tools")
    async def get_tools():
        return service.tool_definitions()

    @app.post("/api/command")
    async def command(request: Request):
        return service.execute(
            await body(request), actor="manual", entrypoint="manual_http"
        )

    @app.post("/api/tools/{name}")
    async def tool(name: str, request: Request):
        actor = request.headers.get("x-studio-actor", "webmcp")
        if actor not in {"mcp", "webmcp"}:
            raise SceneError("invalid_actor", "Tool source must be mcp or webmcp")
        return service.invoke(
            name,
            await body(request),
            actor=actor,
            entrypoint="tool_http",
            caller_hint=request.headers.get("x-studio-actor"),
        )

    @app.get("/api/setup")
    async def setup(request: Request):
        origin = str(request.base_url).rstrip("/")
        return {
            "mcp_enabled": enable_mcp,
            "mcp_url": origin + "/mcp/",
            "catalog_url": origin + "/api/tools",
            "model_connection_verified": False,
            "stdio": {
                "command": sys.executable,
                "args": ["-m", "studio.mcp_server", "--studio-url", origin],
                "cwd": str(Path(__file__).resolve().parent.parent),
            },
        }

    @app.get("/api/health")
    async def health():
        return {
            "ok": True,
            "service": "2top-tidal-atlas",
            "version": __version__,
            "mcp": enable_mcp,
            "document_id": service.snapshot()["document_id"],
        }

    app.mount("/static", StaticFiles(directory=STATIC), name="static")
    if enable_mcp:
        app.mount("/mcp", mcp_app)
    return app


def main():
    parser = argparse.ArgumentParser(
        description="Start the local 2Top kinetic-art studio"
    )
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument(
        "--scene",
        type=Path,
        default=Path(".studio/scene.json"),
        help="Local scene persistence file (not accepted via agent tools)",
    )
    parser.add_argument(
        "--ephemeral", action="store_true", help="Do not save a scene on disk"
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    args = parser.parse_args()
    service = SceneService(None if args.ephemeral else args.scene)
    uvicorn.run(create_app(service), host="127.0.0.1", port=args.port)


if __name__ == "__main__":
    main()
