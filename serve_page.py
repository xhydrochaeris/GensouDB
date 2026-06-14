async def html_head(t, user):
    lin = '<a href="/login">Log in</a><a href="/register">Register</a>'
    if user: # None if not logged in, id if logged in
        lin = f'<a href="/user/{user}">Profile</a><a href="/logout">Log out</a>'
    return f"""<!DOCTYPE html>
<html>
<head>
<link rel="stylesheet" href="/static_web/style.css">
<title>{t}</title>
</head>
<body>
    <div class="TopBar">
        <a href="/home"><img src="/static_web/gensou-logo.png" style="max-height:50px; height:auto; width:auto;"></a>
        <header>
            <a href="/home">Home</a>
            <a href="/search">Search</a>
            <a href="/wiki">Wiki</a>
            {lin}
        </header>
    </div>
"""

HOME_BODY = """<h1>Welcome to GensouDB!</h1>
<p>abcde <a href="vkrecs/w2.html">bogus</a></p>
<h2 class="rainbow rainbow_text_animated">rAINbow</h2>
<ul>
<li>abcde <a href="vkrecs/w2.html">bogus</a></li>
</ul>
"""

HTML_END = """<footer class="center_footer rainbow-border">
    <h2>website developed by</h2>
    <a href="/user/0">CIPHER 【零】</a>
</footer>
</body>
"""

async def err_body(n):
    return f'<div class="center_img"><img src=https://http.cat/images/{n}.jpg></div>'

async def serve_page(s, context):
    user = context['user_id']
    if s:
        if s == "home":
            return (await html_head("gensou", user) + HOME_BODY + HTML_END, 200)
        elif s == "search":
            return (await html_head("gensou : error not implemented", user) + await err_body(501) + HTML_END, 501)
        elif s == "wiki":
            return (await html_head("gensou : error not implemented", user) + await err_body(501) + HTML_END, 501)
        elif s == "login":
            return (await html_head("gensou : error not implemented", user) + await err_body(501) + HTML_END, 501)
        elif s == "register":
            return (await html_head("gensou : register", user) + await err_body(501) + HTML_END, 501)
        else:
            return (await html_head("gensou : error not found", user) + await err_body(404) + HTML_END, 404)
    else:
        return (await html_head("gensou : error bad request", user) + await err_body(400) + HTML_END, 400)