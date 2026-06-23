from db.user import pwd_is_dummy, get_privilege

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

HOME_BODY = """<h1>Welcome to GensouDB!</h1>
<p>abcde <a href="vkrecs/w2.html">bogus</a></p>
<h2 class="rainbow rainbow_text_animated">rAINbow</h2>
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

def pt2html(text):
    t = ''
    for c in str(text):
        if c == '<':
            t += '&lt;'
        elif c == '>':
            t += '&gt;'
        elif c == '&':
            t += '&amp;'
        else:
            t += c
    return t
