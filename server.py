#!/usr/bin/env python3

# `server.py` - This file is the main executable that runs the server
# The dispatch process for the server is roughly as follows:
# 1. collect POST and query from the request
# 2. validate the user's session
# 3. if the request is a valid file in the `static_web` directory
#    --> serve that file
# 4. otherwise `serve_page()` in `serve_page.py` dispatches the request to other functions based on the URL
# 5. if the returned tuple from `serve_page()` includes additional commands, execute them before returning the request

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
    # `post` is a multidict which contains the POST contents if the request was a POST
    # and is empty if there were no POST contents
    # The server doesn't distinguish between GET and POST other than polling whether POST contents exist.
    try:
        post = await request.post()
    except:
        post = multidict.MultiDict()
    # `query` is a multidict which contains the data submitted in the URL query
    query = request.query.copy()
    # `uid` is the user's ID, `sess_id` is the user's session ID. Both are in the cookies
    # The server can only trust the `uid` is valid if the `sess_id` is valid and corresponds to the user
    uid = None
    try:
        uid = int(request.cookies.get("uid"))
    except:
        uid = None
    sess_id = request.cookies.get("sess_id")

    if (sess_id == None):
        uid = None
    else:
        if not is_session_valid(uid, sess_id):
            uid = None

    # `path` is the request's path
    # We first check if it is a valid file in the `static_web` folder, and serve that file if it is
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

    # If the request is not a file that exists in `static_web`, `serve_page()` handles it
    # The values returned in `serve_page()`'s 4-tuple are as follows:
    # - `html`: the html content of the page, or a URL if `extra` includes the "redirect" command
    # - `status`: the HTTP status code of the response
    # - `extra`: a list of commands for the server to complete before serving the page
    # - `extra2`: a list of [uid, sess_id] used to create a cookie if the "make_cookie" command is included in `extra`
    html, status, extra, extra2 = await serve_page(relative, uid, post, query)
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
app.router.add_post("/{path_info:.*}", handle)

if __name__ == "__main__":
    web.run_app(app, host=HOST, port=PORT)
