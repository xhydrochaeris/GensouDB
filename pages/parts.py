from db.user import pwd_is_dummy, get_privilege
from db.db import get_conn
from html import escape

async def html_head(t, user):
    dummy = ''
    lin = '<a href="/login">Log in</a><a href="/register">Register</a>'
    if user is not None: # None if not logged in, id if logged in
        lin = f'<a href="/user/{user}">Profile</a><a href="/prefs">Preferences</a><a href="/logout">Log out</a>'
        if pwd_is_dummy(user):
            dummy = '<h1 style="color:red">Your current password is outdated. Please <a href="/set_pw"">set a new one</a>.</h1>'
        if get_privilege(user) == 99:
            lin += f'<a href="/admin">Admin</a>'
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
    {dummy}
"""

HTML_END = """<footer class="center_footer rainbow-border">
    <h2>website developed by</h2>
    <a href="/user/0">CIPHER 【零】</a>
</footer>
</body>
"""

async def err_body(n):
    return f'<div class="center_img"><img src=https://http.cat/images/{n}.jpg></div>'

async def home_body(user):
    t = "You are not logged in."
    if user is not None:
        with get_conn() as conn:
            r = conn.execute("SELECT dname, uname FROM USER WHERE ID = ?", (user,)).fetchone()
            t = f'You are signed in as <a href="/user/{user}">{escape(r[0])}</a> <span style="font-size:20px;font-weight:normal;font-style:italic;">({escape(r[1])})</span>'

    return f"""<h1 class="rainbow rainbow_text_animated">Welcome to GensouDB!</h1>
<h2>{t}</h2>
<p>abcde <a href="vkrecs/w2.html">bogus</a></p>
<ul>
<li>abcde <a href="vkrecs/w2.html">bogus</a></li>
</ul>
"""

async def redirect(page):
    return f"""<!DOCTYPE html>
<html>
<head>
<link rel="stylesheet" href="/static_web/style.css">
<title>gensou : Redirect</title>
<meta http-equiv="refresh" content="0; url={page}" />
</head>
<body>
<h1>You are being redirected. <a href={page}>Click here</a></h1>
"""
