from pages.parts import html_head, HTML_END, err_body, redirect
from db.db import get_conn

ADMIN_HEAD = f"""<!DOCTYPE html>
<html>
<head>
<link rel="stylesheet" href="/static_web/style.css">
<title>gensou admin page</title>
</head>
<body>
    <div class="TopBar">
        <a href="/home"><img src="/static_web/gensou-logo.png" style="max-height:50px; height:auto; width:auto;"></a>
        <header>
            <a href="/home">Home</a>
            <a href="/search">Search</a>
            <a href="/wiki">Wiki</a>
            <a href="/admin">Admin</a>
        </header>
    </div>
    <div class="TopBar">
        <header>
            <a href="/admin?table=user">User</a>
            <a href="/admin?table=artists">Artists</a>
        </header>
    </div>
"""

async def html_table(name, frm=0, to=100):
    with get_conn() as conn:
        t = f"""<p style=\"font-size: 18px;\">Showing IDs {frm}-{to}.<form action="admin">
        <input type="hidden" id="table", name="table", value="{name}">
        <label for="from">from: </label><input type="text" id="from" name="from" value={frm}> <label for="to">to: </label>
        <input type="text" id="to" name="to" value={to}><input class=login_submit type="submit" value="Submit">
        </form></p>
        <p><a href=admin?table={name}&action=insert style=\"font-size: 18px;\">Insert new entry into table</a></p><table>"""
        tbl = []
        hrs = []
        if name.lower() == "user":
            tbl = conn.execute("SELECT * FROM USER WHERE ID >= ? AND ID <= ?", (frm, to)).fetchall()
            cnt = len(tbl)
            hrs = ["ID", "dname", "uname", "class", "pw_hash", "Prefs", "SESS_ID", "SESS_Expiry", "dummy_pw"]
        t += "<tr>"
        for hr in hrs:
            t += f"<th>{hr}</th>"
        t += f"<th colspan=2 style=\"color:brown;\">{cnt} items</th></tr>"
        for row in tbl:
            t += "<tr>"
            for i in range(len(hrs)):
                if hrs[i] in ["pw_hash", "SESS_ID"]:
                    if row[i] is None:
                        t += "<td>None</td>"
                    else:
                        t += "<td>(not shown)</td>"
                else:
                    t += f"<td>{row[i]}</td>"
            t += f"<td><a href=admin?table={name}&action=edit&id={row[0]} style=\"color:blue;\">Edit</a></td>"
            t += f"<td><a href=admin?table={name}&action=delete&id={row[0]} style=\"color:blue;\">Delete</a></td>"
            t += "</tr>"
        t += "</table><br>"
        return t

async def admin_page(user, post, query):
    try:
        a = query['action']
    except:
        a = "view"
    if a == "view":
        try:
            f = int(query['from'])
            t = int(query['to'])
            if (f > t):
                temp = t
                t = f
                f = temp
        except:
            f = 0
            t = 100
        try:
            q = query['table']
            return (ADMIN_HEAD + await html_table(q, f, t) + HTML_END, 200, None, None)
        except:
            return (ADMIN_HEAD + HTML_END, 200, None, None)
    elif a == "insert":
        return (ADMIN_HEAD + HTML_END, 200, None, None)
    else:
        return (ADMIN_HEAD + HTML_END, 200, None, None)
