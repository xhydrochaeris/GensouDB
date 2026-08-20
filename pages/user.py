# `user.py` - This file has functions related to user profiles, including the profile page and preferences page

from pages.parts import html_head, HTML_END, err_body, DEFAULT_STYLE
from db.db import get_conn
from html import escape

async def user_body(r):
    if r[3] is not None:
        r3 = escape(r[3][:10])
    else:
        r3 = "Unknown"
    return f'''<h1>User profile: {escape(r[0])} <span style="font-size:20px;font-weight:normal;font-style:italic;">({escape(r[1])})</span></h1>
    <p style="font-size:18px;">User class: {r[2]}</p>
    <p style="font-size:18px;">Account created on: {r3}</p>
    <p style="font-size:18px;"><a href=/prefs>User preferences</a></p>
    '''

# This page should be the user's profile. It can be seen by any user, but some fields may be hidden to other users
# endpoint: /user?id=
async def user_profile(user, query):
    try:
        with get_conn() as conn:
            row = conn.execute(
                "SELECT dname, uname, class, created FROM USER WHERE ID = ?", (query['id'],)
            ).fetchone()
            if not row:
                return (await html_head("gensou : error not found", user) + await err_body(404) + HTML_END, 404, None, None)
            else:
                return (await html_head(f"gensou : {row[0]}'s profile page", user) + await user_body(row) + HTML_END, 200, None, None)
    except:
        return (await html_head("gensou : error bad request", user) + await err_body(400) + HTML_END, 400, None, None)

async def prefs_body(user, message=None):
    themes = {"default": f'Default ({DEFAULT_STYLE})',
                  'muon': 'muon by CIPHER 【零】'}
    with get_conn() as conn:
        theme = conn.execute(
                "SELECT theme FROM USER WHERE ID = ?", (user,)
            ).fetchone()[0]
    options = ''
    for t in themes:
        options += f'<option value="{t}" {'selected' if t == theme else ''}>{themes[t]}</option>'
    if message is not None:
        m = f'<p style=\"color: lime; font-weight: bold\">{message}</p>'
    else:
        m = ''
    return f"""{m}
    <h1>Preferences</h1>
<p style="font-size:18px;"><a href=/set_pw>Change your password</a></p>
<p style="font-size:18px;"><a href=/set_uname>Change your username or display name</a></p>
<form action="/prefs" method="post">
  <label for="theme">Choose a theme:</label>
  <select id="theme" name="theme">
    {options}
  </select>
  <input type="submit">
</form>"""

# This page is the user's preferences menu. Each user can use it to change their own settings for the site
async def prefs_page(user, post):
    message = None
    try:
        if post['theme'] != '':
            with get_conn() as conn:
                conn.execute("UPDATE USER SET theme = ? WHERE ID = ?", (post['theme'], user))
                message = "Theme updated!"
    finally:
        return (await html_head("gensou : preferences", user) + await prefs_body(user, message) + HTML_END, 200, None, None)
