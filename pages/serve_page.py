from pages.parts import html_head, HOME_BODY, HTML_END, err_body
from pages.login import login_page, register_page, LOGGED_IN, set_pw, logout
from pages.admin import admin_page, admin_insert, admin_edit
from pages.preferences import prefs_page
from db.user import get_privilege

async def serve_page(s, user, post, query):
    if s:
        if s == "home":
            return (await html_head("gensou", user) + HOME_BODY + HTML_END, 200, None, None)
        elif s == "search":
            return (await html_head("gensou : error not implemented", user) + await err_body(501) + HTML_END, 501, None, None)
        elif s == "wiki":
            return (await html_head("gensou : error not implemented", user) + await err_body(501) + HTML_END, 501, None, None)
        elif s == "login":
            return await login_page(user, post)
        elif s == "set_pw":
            return await set_pw(user, post)
        elif s == "register":
            return await register_page(user, post)
        elif s == "prefs":
            return await prefs_page(user, post)
        elif s == "logout":
            return await logout(user)
        elif s == "admin":
            if get_privilege(user) == 99:
                return await admin_page(user, post, query)
            else:
                return (await html_head("gensou : error not found", user) + await err_body(404) + HTML_END, 404, None, None)
        elif s == "admin/insert":
            if get_privilege(user) == 99:
                return await admin_insert(user, post)
            else:
                return (await html_head("gensou : error not found", user) + await err_body(404) + HTML_END, 404, None, None)
        elif s == "admin/edit":
            if get_privilege(user) == 99:
                return await admin_edit(user, post)
            else:
                return (await html_head("gensou : error not found", user) + await err_body(404) + HTML_END, 404, None, None)
        else:
            return (await html_head("gensou : error not found", user) + await err_body(404) + HTML_END, 404, None, None)
    else:
        return (await html_head("gensou : error bad request", user) + await err_body(400) + HTML_END, 400, None, None)
