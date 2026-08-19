from pages.parts import html_head, HTML_END, err_body, redirect
from db.db import get_conn
from db.user import hash_password, get_privilege
from html import escape

async def admin_head(user, include=''):
    with get_conn() as conn:
        r = conn.execute("SELECT dname, uname FROM USER WHERE ID = ?", (user,)).fetchone()
    return f"""<!DOCTYPE html>
<html>
<head>
<link rel="stylesheet" href="/static_web/style.css">
<title>gensou admin page</title>
{include}
</head>
<body>
    <div class="TopBar">
        <a href="/home"><img src="/static_web/gensou-logo.png" style="max-height:50px; height:auto; width:auto;"></a>
        <header>
            <a href="/home">Home</a>
            <a href="/search">Search</a>
            <a href="/wiki">Wiki</a>
            <div class="dropdown">User: {escape(r[0])} <span style="font-style:italic;">({escape(r[1])})</span>
  <div class="dropdown-content"><a href="/user/{user}">Profile</a><a href="/prefs">Preferences</a><a href="/logout">Log out</a>
            <a href="/admin">Admin</a></div></div>
        </header>
    </div>
    <br>
    <div class="TopBar">
        <span class="rainbow rainbow_text_animated" style=\"font-size: 28px;font-weight: bold;font-style: italic;\">Admin Control Panel:</span>
        <header style="background-color:rgba(100, 0, 122, 0.6);">
            <a href="/admin?table=user">User</a>
            <a href="/admin?table=artists">Artists</a>
            <a href="/admin?table=rls_groups">Rls_Groups</a>
            <a href="/admin?table=variations">Variations</a>
            <a href="/admin?table=releases">Releases</a>
            <a href="/admin?table=items">Items</a>
            <a href="/admin?table=song">Song</a>
            <a href="/admin?table=file">File</a>
        </header>
    </div>
"""

JS_DELETE_CONFIRM = """<style>
  #confirm-overlay {
    display: none;
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,0.4);
    z-index: 999;
    justify-content: center;
    align-items: center;
  }
  #confirm-overlay.active {
    display: flex;
  }
  #confirm-box {
    background: #10101A;
    padding: 24px 32px;
    border: 1px solid #888;
    text-align: center;
    min-width: 300px;
  }
  #confirm-box p {
    margin: 0 0 16px 0;
  }
  #confirm-box button {
    margin: 0 8px;
    padding: 6px 20px;
    cursor: pointer;
    background: #202030;
    color: rgb(0, 255, 170);
  }
</style>

<div id="confirm-overlay">
  <div id="confirm-box">
    <p id="confirm-msg"></p>
    <button id="confirm-yes">Yes</button>
    <button id="confirm-no">No</button>
  </div>
</div>

<script>
  const overlay = document.getElementById("confirm-overlay");
  const msg     = document.getElementById("confirm-msg");
  const btnYes  = document.getElementById("confirm-yes");
  const btnNo   = document.getElementById("confirm-no");

  function confirmDelete(event, tableName, id) {
    event.preventDefault();
    if (event.shiftKey) {
      window.location.href = `admin?table=${tableName}&action=delete&id=${id}`;
      return;
    }

    msg.textContent = `Are you sure you want to delete entry ${id} of table ${tableName}?`;
    overlay.classList.add("active");

    btnYes.onclick = () => {
      overlay.classList.remove("active");
      window.location.href = `admin?table=${tableName}&action=delete&id=${id}`;
    };

    btnNo.onclick = () => {
      overlay.classList.remove("active");
    };
  }
</script>"""

JS_NOW_BTN = """<script>
  function setNow(fieldId) {
    const now = new Date();
    document.getElementById(fieldId).value = now.toISOString();
  }
</script>"""

async def html_table(name, frm=0, to=100):
    with get_conn() as conn:
        t = f"""<p style=\"font-size: 18px;\">Showing IDs {frm}-{to}.<form action="admin">
        <input type="hidden" id="table", name="table", value="{name}">
        <label for="from">Show IDs from: </label><input type="text" id="from" name="from" value={frm}> <label for="to">to: </label>
        <input type="text" id="to" name="to" value={to}><input class=login_submit type="submit" value="Submit">
        </form></p>
        """
        if name.lower() == 'user':
            t += f"""<p style=\"font-size: 18px;\"><form action="admin/search">
            <input type="hidden" id="table", name="table", value="{name}">
            <label for="uname">Search by uname: </label><input type="text" id="uname" name="uname"> <label for="dname"> or dname: </label>
            <input type="text" id="dname" name="dname"><input class=login_submit type="submit" value="Submit">
            </form></p>"""
        t += f'<p><a href=admin?table={name}&action=insert style=\"font-size: 18px;\">Insert new entry into table</a></p><div style="overflow-x: auto;"><table>'
        tbl = []
        hrs = []
        cnt = 0
        if name.lower() == "user":
            tbl = conn.execute("SELECT * FROM USER WHERE ID >= ? AND ID <= ?", (frm, to)).fetchall()
            cnt = len(tbl)
            hrs = ["ID", "dname", "uname", "class", "pw_hash", "pw_date", "SESS_ID", "SESS_Expiry", "dummy_pw"]
        t += "<tr>"
        for hr in hrs:
            t += f"<th class=\"mono-table\">{hr}</th>"
        t += f"<th class=\"mono-table\" colspan=2 style=\"color:brown;white-space: pre;\">{cnt} items</th></tr>"
        for row in tbl:
            t += "<tr>"
            for i in range(len(hrs)):
                if hrs[i] in ["pw_hash", "SESS_ID"]:
                    if row[i] is None:
                        t += "<td>None</td>"
                    else:
                        t += "<td style=\"white-space: pre;\">(not shown)</td>"
                else:
                    if row[i] is None:
                        t += "<td>None</td>"
                    else:
                        t += f"<td class=\"mono-table\" style=\"white-space: pre;\">{escape(str(row[i]))}</td>"
            t += f"<td><a href=admin?table={name}&action=edit&id={row[0]} style=\"color:blue;\">Edit</a></td>"
            t += f"<td><a href=\"#\" onclick=\"confirmDelete(event, '{name}', {row[0]})\" style=\"color:blue;\">Delete</a></td>"
            t += "</tr>"
        t += "</table></div><br>"
        return t

DATE_FIELDS = {'pw_date', 'SESS_Expiry'}
async def edit_form(name, i=None):
    with get_conn() as conn:
        hrs = []
        r = None
        if name.lower() == "user":
            if (i is not None):
                r = conn.execute("SELECT * FROM USER WHERE ID = ?", (i,)).fetchone()
            hrs = ["ID", "dname", "uname", "class", "pw_hash", "pw_date", "SESS_ID", "SESS_Expiry", "dummy_pw"]
        if i is not None:
            t = f'<form action=\"/admin/edit\" method=post><input type="hidden" id="table", name="table", value="{name}">'
            for j in range(len(hrs)):
                if hrs[j] == 'pw_hash':
                    t += '''<label for="PW">PW (will be hashed): </label><input type="text" id="PW" name="PW">
                            <input type="checkbox" id="pw_clear" name="pw_clear" value="yes" onchange="document.getElementById('PW').disabled = this.checked">
                            <label for="pw_clear"> Clear this user's pasword</label><br><br>'''
                elif hrs[j] == 'ID':
                    t += f'<label>ID: </label><input type="text" value="{str(r[j])}" disabled=true><input type="hidden" id="ID", name="ID", value="{str(r[j])}"><br><br>'
                else:
                    val_attr = f'value="{escape(str(r[j]))}"' if r[j] is not None else ""
                    now_btn = f' <button type="button" onclick="setNow(\'{hrs[j]}\')">Now</button>' if hrs[j] in DATE_FIELDS else ""
                    t += f'<label for="{hrs[j]}">{hrs[j]}: </label><input type="text" id="{hrs[j]}" name="{hrs[j]}" {val_attr}>{now_btn}<br><br>'
        else:
            t = f'<form action=\"/admin/insert\" method=post><input type="hidden" id="table", name="table", value="{name}">'
            for j in range(len(hrs)):
                if hrs[j] == 'pw_hash':
                    t += f'<label for="PW">PW (will be hashed): </label><input type="text" id="PW" name="PW"><br><br>'
                else:
                    now_btn = f' <button type="button" onclick="setNow(\'{hrs[j]}\')">Now</button>' if hrs[j] in DATE_FIELDS else ""
                    t += f'<label for="{hrs[j]}">{hrs[j]}: </label><input type="text" id="{hrs[j]}" name="{hrs[j]}">{now_btn}<br><br>'
        t += '<input class=login_submit type="submit" value="Submit"></form><br>'
    return t

async def admin_insert(user, post):
    try:
        q = post["table"]
        if q.lower() == 'user':
            if get_privilege(user) != 99:
                return (await admin_head(user) + await err_body(401) + HTML_END, 401, None, None)
            with get_conn() as conn:
                d = post['uname'] if post['dname'] == '' else post['dname']
                if post['ID'] == '':
                    cursor = conn.execute("INSERT INTO USER (dname, uname) VALUES (?, ?)", (d, post['uname']))
                else:
                    cursor = conn.execute("INSERT INTO USER (ID, dname, uname) VALUES (?, ?, ?)", (post['ID'], d, post['uname']))
                ins_id = cursor.lastrowid
                if post['PW'] != '':
                    conn.execute("UPDATE USER SET pw_hash = ? WHERE ID = ?", (hash_password(post['PW']), ins_id))
                for f in ["class", "pw_date", "SESS_ID", "SESS_Expiry", "dummy_pw"]:
                    if post[f] != '':
                        conn.execute(f"UPDATE USER SET {f} = ? WHERE ID = ?", (post[f], ins_id))
        return (await admin_head(user) + f'<h1>Item inserted at ID={ins_id}!</h1><p><a href=/admin?table={q}>Return to admin page</a></p>' + HTML_END, 200, None, None)
    except:
        return (await admin_head(user) + await err_body(400) + HTML_END, 400, None, None)

async def admin_edit(user, post):
    try:
        q = post["table"]
        if (q == "user") and (get_privilege(user) != 99):
            return (await admin_head(user) + await err_body(401) + HTML_END, 401, None, None)
        i = int(post['ID'])
        if q.lower() == 'user':
            with get_conn() as conn:
                try:
                    p = post['pw_clear']
                except:
                    p = "no"
                if p == "yes":
                    conn.execute("UPDATE USER SET pw_hash = NULL WHERE ID = ?", (i,))
                elif post['PW'] != '':
                    conn.execute("UPDATE USER SET pw_hash = ? WHERE ID = ?", (hash_password(post['PW']), i))
                for f in ["dname", "uname","class", "pw_date", "SESS_ID", "SESS_Expiry", "dummy_pw"]:
                    if post[f] != '':
                        conn.execute(f"UPDATE USER SET {f} = ? WHERE ID = ?", (post[f], i))
                    else:
                        conn.execute(f"UPDATE USER SET {f} = NULL WHERE ID = ?", (i,))
        return (await admin_head(user) + f'<h1>Item at ID={i} updated!</h1><p><a href=/admin?table={q}>Return to admin page</a></p>' + HTML_END, 200, None, None)
    except:
        return (await admin_head(user) + await err_body(400) + HTML_END, 400, None, None)

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
            return (await admin_head(user, JS_DELETE_CONFIRM) + await html_table(q, f, t) + HTML_END, 200, None, None)
        except:
            return (await admin_head(user) + "<h1>Select a table to view from the header above.</h1>" + HTML_END, 200, None, None)
    elif a == "insert":
        try:
            q = query['table']
            if (q == "user") and (get_privilege(user) != 99):
                return (await admin_head(user) + await err_body(401) + HTML_END, 401, None, None)
            return (await admin_head(user, JS_NOW_BTN) + await edit_form(q) + HTML_END, 200, None, None)
        except:
            return (await admin_head(user) + await err_body(400) + HTML_END, 400, None, None)
    elif a == "edit":
        try:
            q = query['table']
            if (q == "user") and (get_privilege(user) != 99):
                return (await admin_head(user) + await err_body(401) + HTML_END, 401, None, None)
            i = int(query['id'])
            return (await admin_head(user, JS_NOW_BTN) + await edit_form(q, i) + HTML_END, 200, None, None)
        except:
            return (await admin_head(user) + await err_body(400) + HTML_END, 400, None, None)
    elif a == "delete":
        try:
            i = int(query["id"])
            q = query['table']
            if (q == "user") and (get_privilege(user) != 99):
                return (await admin_head(user) + await err_body(401) + HTML_END, 401, None, None)
            if q.lower() == 'user':
                if i == 0:
                    return (await admin_head(user) + f'<h1 style="color:red;">You cannot delete the admin user!!!!!!</h1><p><a href=/admin?table={q}>Return to admin page</a></p>' + HTML_END, 400, None, None)
                with get_conn() as conn:
                    conn.execute("DELETE FROM USER WHERE ID = ?", (i,))
            return (await admin_head(user) + f'<h1 class="rainbow rainbow_text_animated">Item was deleted!</h1><p><a href=/admin?table={q}>Return to admin page</a></p>' + HTML_END, 200, None, None)
        except:
            return (await admin_head(user) + await err_body(400) + HTML_END, 400, None, None)
    else:
        return (await admin_head(user) + await err_body(400) + HTML_END, 400, None, None)

async def admin_search(user, query):
    try:
        q = query['table']
        if q == 'user':
            if query['uname'] != '':
                with get_conn() as conn:
                    row = conn.execute(
                        "SELECT ID FROM USER WHERE uname = ?", (query['uname'],)
                    ).fetchone()
                    if not row:
                        return (await admin_head(user) + await err_body(404) + HTML_END, 404, None, None)
                    else:
                        return (f"/admin?table={q}&from={dict(row)['ID']}&to={dict(row)['ID']}", 200, ["redirect"], None)
            elif query['dname'] != '':
                with get_conn() as conn:
                    row = conn.execute(
                        "SELECT ID FROM USER WHERE dname = ?", (query['dname'],)
                    ).fetchone()
                    if not row:
                        return (await admin_head(user) + await err_body(404) + HTML_END, 404, None, None)
                    else:
                        return (f"/admin?table={q}&from={dict(row)['ID']}&to={dict(row)['ID']}", 200, ["redirect"], None)
            else:
                return (f"/admin?table={q}", 200, ["redirect"], None)
        else:
            return (await admin_head(user) + await err_body(501) + HTML_END, 501, None, None)
    except:
        return (await admin_head(user) + await err_body(400) + HTML_END, 400, None, None)
