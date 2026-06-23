from pages.parts import html_head, HTML_END, err_body

PREFS_BODY = """<h1>Preferences</h1>
<p style="font-size:18px;"><a href=/set_pw>Change your password</a></p>"""

async def prefs_page(user, post):
    return (await html_head("gensou : preferences", user) + PREFS_BODY + HTML_END, 200, None, None)
