import asyncio
import mimetypes
from pathlib import Path
from aiohttp import web

from pages.serve_page import serve_page
from db.user import get_uid, is_session_valid, hash_password

STATIC_DIR = Path("static_web")
HOST = "0.0.0.0"
PORT = 8080

def make_session_cookie(response: web.Response, uid: str, sess_id: str, days: int = 30) -> None:
    response.set_cookie(
        "uid",
        uid,
        max_age=days * 86400,  # seconds until expiry
        httponly=True,          # JS cannot read it
        samesite="Strict",      # not sent on cross-site requests
        secure=False            # set True when you have HTTPS
    )
    response.set_cookie(
        "sess_id",
        sess_id,
        max_age=days * 86400,  # seconds until expiry
        httponly=True,          # JS cannot read it
        samesite="Strict",      # not sent on cross-site requests
        secure=False            # set True when you have HTTPS
    )

def clear_session_cookie(response: web.Response) -> None:
    response.del_cookie("sess_id")
    response.del_cookie("uid")

async def handle(request: web.Request) -> web.Response:
    context = request.query.copy()
    context["user_id"] = None
    try:
        uid = int(request.cookies.get("uid"))
    except:
        uid = None
    sess_id = request.cookies.get("sess_id")

    if (sess_id == None):
        uid = None
    else:
        if is_session_valid(uid, sess_id):
            context["user_id"] = uid

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

    html, status, extra, extra2 = await serve_page(relative, context)
    resp = web.Response(
        text=html,
        status=status,
        content_type="text/html",
        charset="utf-8"
    )
    if extra:
        for i in extra:
            if i == "redirect":
                resp = web.HTTPFound(html)
            if i == "make_cookie":
                make_session_cookie(resp, extra2[0], extra2[1], 30)
            if i == "clear_cookie":
                clear_session_cookie(resp)
    return resp

app = web.Application()
app.router.add_get("/{path_info:.*}", handle)

if __name__ == "__main__":
    web.run_app(app, host=HOST, port=PORT)
