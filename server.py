import asyncio
import mimetypes
from pathlib import Path
from aiohttp import web

from pages.serve_page import serve_page

STATIC_DIR = Path("static_web")
HOST = "0.0.0.0"
PORT = 8080

async def handle(request: web.Request) -> web.Response:
    context = request.query.copy()
    context.add("user_id" , None)
    path = request.path

    relative  = path.lstrip("/") or "home"
    candidate = (Path("") / relative).resolve()

    try:
        candidate.relative_to(STATIC_DIR.resolve())
        is_safe = True
    except ValueError:
        is_safe = False

    if is_safe and candidate.is_file():
        mime, _ = mimetypes.guess_type(str(candidate))
        return web.FileResponse(
            candidate,
            headers={"Content-Type": mime or "application/octet-stream"}
        )

    html, status = await serve_page(relative, context)
    return web.Response(
        text=html,
        status=status,
        content_type="text/html",
        charset="utf-8"
    )

app = web.Application()
app.router.add_get("/{path_info:.*}", handle)

if __name__ == "__main__":
    web.run_app(app, host=HOST, port=PORT)
