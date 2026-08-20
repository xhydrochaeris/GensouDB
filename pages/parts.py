# `parts.py` - This file contains some parts which are commonly included in other pages,
# such as headers and footers. These are glued together by the other page functions to produce
# HTML pages that are served to the user.

from db.user import pwd_is_dummy, get_privilege, get_style
from db.db import get_conn
from html import escape

DEFAULT_STYLE = 'muon'

# Website header: placed at the beginning of the HTML. contains a header which changes based on
# the user, and a custom page title that can be set by the caller
async def html_head(title, user):
    style = get_style(user)
    if style == 'default':
        style = DEFAULT_STYLE
    dummy = ''
    lin = '<a href="/login">Log in</a><a href="/register">Register</a>'
    if user is not None: # None if not logged in, id if logged in
        with get_conn() as conn:
            r = conn.execute("SELECT dname, uname FROM USER WHERE ID = ?", (user,)).fetchone()
        lin = f'''<div class="dropdown">User: {escape(r[0])} <span style="font-style:italic;">({escape(r[1])})</span>
  <div class="dropdown-content"><a href="/user?id={user}">Profile</a><a href="/prefs">Preferences</a><a href="/logout">Log out</a>'''
        if pwd_is_dummy(user):
            dummy = '<h1 style="color:red">Your current password is outdated. Please <a href="/set_pw"">set a new one</a>.</h1>'
        if get_privilege(user) >= 50:
            lin += '<a href="/admin">Admin</a></div></div>'
        else:
            lin += '</div></div>'
    return f"""<!DOCTYPE html>
<html>
<head>
<link rel="stylesheet" href="/static_web/style/base.css">
<link rel="stylesheet" href="/static_web/style/{style}.css">
<title>{title}</title>
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

# HTML end: this is a static footer at the end of the HTML, and also closes the open tags
HTML_END = """<footer class="center_footer rainbow-border">
    <h2>website developed by</h2>
    <a href="/user?id=0">CIPHER 【零】</a>
</footer>
</body>
</html>
"""

# Error body: This returns a comical error page with a corresponding picture from http.cat
async def err_body(n):
    return f'<div class="center_img"><img src=https://http.cat/images/{n}.jpg></div>'

# Homepage body: This is a home page body that changes based on the user.
async def home_body(user):
    t = "You are not logged in."
    if user is not None:
        with get_conn() as conn:
            r = conn.execute("SELECT dname, uname FROM USER WHERE ID = ?", (user,)).fetchone()
            t = f'You are signed in as <a href="/user?id={user}">{escape(r[0])}</a> <span style="font-size:20px;font-weight:normal;font-style:italic;">({escape(r[1])})</span>'

    return f"""<h1 class="rainbow rainbow_text_animated">Welcome to GensouDB!</h1>
<h2>{t}</h2>
<p>abcde <a href="vkrecs/w2.html">bogus</a></p>
<ul>
<li>abcde <a href="vkrecs/w2.html">bogus</a></li>
</ul>
"""

# legacy redirect (unused)
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
