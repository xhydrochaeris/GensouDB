from pages.parts import html_head, HTML_END, err_body, redirect

async def admin_page(s, user, post, query):
    return (await html_head("gensou : error not implemented", user) + await err_body(501) + HTML_END, 501, None, None)
