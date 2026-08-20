# `serve_page.py` - This file determines the page URLs that can be requested by the user
# This file doesn't necessarily contain any logic for the pages themselves, other than
# the privilege check for admin pages. It just calls functions that represent the target pages,
# or returns an error if something is wrong with the request.

from pages.parts import html_head, home_body, HTML_END, err_body
from pages.login import login_page, register_page, LOGGED_IN, set_pw, logout, set_uname
from pages.admin import admin_page, admin_insert, admin_edit, admin_search
from pages.user import user_profile, prefs_page
from db.user import get_privilege

# `serve_page()` takes four inputs and produces a 4-tuple as its output
# - `s` is the relative URL requested
# - `user` is the user ID of the requester (session was already verified by server)
# - `post` is a Multidict containing the contents of POST, if they exist
# - `query` is a Multidict containing the contents of the URL query
# The returned tuple is explained in the server's `handle()`
async def serve_page(s, user, post, query):
    if s:
        if s == "home":
            return (await html_head("gensou", user) + await home_body(user) + HTML_END, 200, None, None)
        elif s == "search":
            return (await html_head("gensou : error not implemented", user) + await err_body(501) + HTML_END, 501, None, None)
        elif s == "wiki":
            return (await html_head("gensou : error not implemented", user) + await err_body(501) + HTML_END, 501, None, None)
        elif s == "login":
            return await login_page(user, post)
        elif s == "set_pw":
            return await set_pw(user, post)
        elif s == "set_uname":
            return await set_uname(user, post)
        elif s == "register":
            return await register_page(user, post)
        elif s == "user":
            return await user_profile(user, query)
        elif s == "prefs":
            if user != None:
                return await prefs_page(user, post)
            else:
                return (await html_head("gensou : error unauthorized", user) + await err_body(401) + HTML_END, 401, None, None)
        elif s == "logout":
            return await logout(user)
        elif s == "admin":
            if get_privilege(user) >= 50:
                return await admin_page(user, post, query)
            else:
                return (await html_head("gensou : error not found", user) + await err_body(404) + HTML_END, 404, None, None)
        elif s == "admin/insert":
            if get_privilege(user) >= 50:
                return await admin_insert(user, post)
            else:
                return (await html_head("gensou : error not found", user) + await err_body(404) + HTML_END, 404, None, None)
        elif s == "admin/edit":
            if get_privilege(user) >= 50:
                return await admin_edit(user, post)
            else:
                return (await html_head("gensou : error not found", user) + await err_body(404) + HTML_END, 404, None, None)
        else:
            return (await html_head("gensou : error not found", user) + await err_body(404) + HTML_END, 404, None, None)
    else:
        return (await html_head("gensou : error bad request", user) + await err_body(400) + HTML_END, 400, None, None)
