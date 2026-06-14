from pages.parts import html_head, HOME_BODY, HTML_END, err_body
from pages.login import login_page, register_page, LOGGED_IN, set_pw, logout

async def serve_page(s, context):
    user = context['user_id']
    if s:
        if s == "home":
            return (await html_head("gensou", user) + HOME_BODY + HTML_END, 200, None, None)
        elif s == "search":
            return (await html_head("gensou : error not implemented", user) + await err_body(501) + HTML_END, 501, None, None)
        elif s == "wiki":
            return (await html_head("gensou : error not implemented", user) + await err_body(501) + HTML_END, 501, None, None)
        elif s == "login":
            return await login_page(s, context)
        elif s == "logged_in":
            return (await html_head("gensou : logged in", user) + LOGGED_IN + HTML_END, 200, None, None)
        elif s == "set_pw":
            return await set_pw(s, context)
        elif s == "register":
            return await register_page(s, context)
        elif s == "logout":
            return await logout(s, context)
        else:
            return (await html_head("gensou : error not found", user) + await err_body(404) + HTML_END, 404, None, None)
    else:
        return (await html_head("gensou : error bad request", user) + await err_body(400) + HTML_END, 400, None, None)
