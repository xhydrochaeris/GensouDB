# `user.py` - This file has functions related to user profiles, including the profile page and preferences page

from pages.parts import html_head, HTML_END, err_body
from db.db import get_conn
from html import escape

async def user_body(r):
    return f'''<h1>User profile: {escape(r[0])} <span style="font-size:20px;font-weight:normal;font-style:italic;">({escape(r[1])})</span></h1>
    <p>User class: {r[2]}</p>
    <p>Account created on: {escape(r[3][:10])}</p>'''

# This page should be the user's profile. It can be seen by any user, but some fields may be hidden to other users
# endpoint: /user?id=
async def user_profile(user, query):
    #try:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT dname, uname, class, created FROM USER WHERE ID = ?", (query['id'],)
        ).fetchone()
        if not row:
            return (await html_head("gensou : error not found", user) + await err_body(404) + HTML_END, 404, None, None)
        else:
            return (await html_head(f"gensou : {row[0]}'s profile page", user) + await user_body(row) + HTML_END, 200, None, None)
    #except:
        #return (await html_head("gensou : error bad request", user) + await err_body(400) + HTML_END, 400, None, None)

PREFS_BODY = """<h1>Preferences</h1>
<p style="font-size:18px;"><a href=/set_pw>Change your password</a></p>"""

# This page is the user's preferences menu. Each user can use it to change their own settings for the site
async def prefs_page(user):
    return (await html_head("gensou : preferences", user) + PREFS_BODY + HTML_END, 200, None, None)
