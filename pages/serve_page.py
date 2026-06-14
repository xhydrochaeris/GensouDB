from pages.parts import html_head, HOME_BODY, HTML_END, err_body
from pages.login import login_page, register_page

async def serve_page(s, context):
    user = context['user_id']
    if s:
        if s == "home":
            return (await html_head("gensou", user) + HOME_BODY + HTML_END, 200)
        elif s == "search":
            return (await html_head("gensou : error not implemented", user) + await err_body(501) + HTML_END, 501)
        elif s == "wiki":
            return (await html_head("gensou : error not implemented", user) + await err_body(501) + HTML_END, 501)
        elif s[:5] == "login":
            return await login_page(s, context)
        elif s[:8] == "register":
            return await register_page(s, context)
        else:
            return (await html_head("gensou : error not found", user) + await err_body(404) + HTML_END, 404)
    else:
        return (await html_head("gensou : error bad request", user) + await err_body(400) + HTML_END, 400)
