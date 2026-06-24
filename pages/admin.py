from pages.parts import html_head, HTML_END, err_body, redirect
from db.db import get_conn
from db.user import hash_password
from html import escape

async def admin_head(include=''):
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
            <a href="/admin">Admin</a>
            <a href="/prefs">Preferences</a><a href="/logout">Log out</a>
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
        cnt = 0
        if name.lower() == "user":
            tbl = conn.execute("SELECT * FROM USER WHERE ID >= ? AND ID <= ?", (frm, to)).fetchall()
            cnt = len(tbl)
            hrs = ["ID", "dname", "uname", "class", "pw_hash", "pw_date", "Prefs", "SESS_ID", "SESS_Expiry", "dummy_pw"]
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
                    t += f"<td>{escape(str(row[i]))}</td>"
            t += f"<td><a href=admin?table={name}&action=edit&id={row[0]} style=\"color:blue;\">Edit</a></td>"
            t += f"<td><a href=\"#\" onclick=\"confirmDelete(event, '{name}', {row[0]})\" style=\"color:blue;\">Delete</a></td>"
            t += "</tr>"
        t += "</table><br>"
        return t

async def edit_form(name, i=None):
    with get_conn() as conn:
        hrs = []
        r = None
        if name.lower() == "user":
            if (i is not None):
                r = conn.execute("SELECT * FROM USER WHERE ID = ?", (i,)).fetchone()
            hrs = ["ID", "dname", "uname", "class", "pw_hash", "pw_date", "Prefs", "SESS_ID", "SESS_Expiry", "dummy_pw"]
        if i is not None:
            t = f'<form action=\"/admin/edit\" method=post><input type="hidden" id="table", name="table", value="{name}">'
            for j in range(len(hrs)):
                if hrs[j] == 'pw_hash':
                    t += '''<label for="PW">PW (will be hashed): </label><input type="text" id="PW" name="PW">
                            <input type="checkbox" id="pw_clear" name="pw_clear" value="yes">
                            <label for="pw_clear"> Clear this user's pasword</label><br><br>'''
                else:
                    if r[j] is None:
                        t += f'<label for="{hrs[j]}">{hrs[j]}: </label><input type="text" id="{hrs[j]}" name="{hrs[j]}"><br><br>'
                    else:
                        t += f'<label for="{hrs[j]}">{hrs[j]}: </label><input type="text" id="{hrs[j]}" name="{hrs[j]}" value="{escape(str(r[j]))}"><br><br>'
        else:
            t = f'<form action=\"/admin/insert\" method=post><input type="hidden" id="table", name="table", value="{name}">'
            for j in range(len(hrs)):
                if hrs[j] == 'pw_hash':
                    t += f'<label for="PW">PW (will be hashed): </label><input type="text" id="PW" name="PW"><br><br>'
                else:
                    t += f'<label for="{hrs[j]}">{hrs[j]}: </label><input type="text" id="{hrs[j]}" name="{hrs[j]}"><br><br>'
        t += '<input class=login_submit type="submit" value="Submit"></form><br>'
    return t

async def admin_insert(user, post):
    try:
        q = post["table"]
        if q.lower() == 'user':
            with get_conn() as conn:
                if post['ID'] == '':
                    cursor = conn.execute("INSERT INTO USER (dname, uname) VALUES (?, ?)", (post['dname'], post['uname']))
                else:
                    cursor = conn.execute("INSERT INTO USER (ID, dname, uname) VALUES (?, ?, ?)", (post['ID'], post['dname'], post['uname']))
                ins_id = cursor.lastrowid
                if post['PW'] != '':
                    conn.execute("UPDATE USER SET pw_hash = ? WHERE ID = ?", (hash_password(post['PW']), ins_id))
                for f in ["class", "Prefs", "pw_date", "SESS_ID", "SESS_Expiry", "dummy_pw"]:
                    if post[f] != '':
                        conn.execute(f"UPDATE USER SET {f} = ? WHERE ID = ?", (post[f], ins_id))
        return (await admin_head() + f'<h1>Item inserted at ID={ins_id}!</h1><p><a href=/admin?table={q}>Return to admin page</a></p>' + HTML_END, 200, None, None)
    except:
        return (await admin_head() + await err_body(400) + HTML_END, 400, None, None)

async def admin_edit(user, post):
    try:
        q = post["table"]
        i = int(post['ID'])
        if q.lower() == 'user':
            with get_conn() as conn:
                if post['PW'] != '':
                    conn.execute("UPDATE USER SET pw_hash = ? WHERE ID = ?", (hash_password(post['PW']), i))
                try:
                    p = post['pw_clear']
                except:
                    p = "no"
                if p == "yes":
                    conn.execute("UPDATE USER SET pw_hash = NULL WHERE ID = ?", (i,))
                for f in ["dname", "uname","class", "pw_date", "Prefs", "SESS_ID", "SESS_Expiry", "dummy_pw"]:
                    if post[f] != '':
                        conn.execute(f"UPDATE USER SET {f} = ? WHERE ID = ?", (post[f], i))
                    else:
                        conn.execute(f"UPDATE USER SET {f} = NULL WHERE ID = ?", (i,))
        return (await admin_head() + f'<h1>Item at ID={i} updated!</h1><p><a href=/admin?table={q}>Return to admin page</a></p>' + HTML_END, 200, None, None)
    except:
        return (await admin_head() + await err_body(400) + HTML_END, 400, None, None)

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
            return (await admin_head(JS_DELETE_CONFIRM) + await html_table(q, f, t) + HTML_END, 200, None, None)
        except:
            return (await admin_head() + "<h1>Select a table to view from the header above.</h1>" + HTML_END, 200, None, None)
    elif a == "insert":
        try:
            q = query['table']
            return (await admin_head() + await edit_form(q) + HTML_END, 200, None, None)
        except:
            return (await admin_head() + await err_body(400) + HTML_END, 400, None, None)
    elif a == "edit":
        try:
            q = query['table']
            i = int(query['id'])
            return (await admin_head() + await edit_form(q, i) + HTML_END, 200, None, None)
        except:
            return (await admin_head() + await err_body(400) + HTML_END, 400, None, None)
    elif a == "delete":
        try:
            i = int(query["id"])
            q = query['table']
            if q.lower() == 'user':
                if i == 0:
                    return (await admin_head() + f'<h1 style="color:red;">You cannot delete the admin user!!!!!!</h1><p><a href=/admin?table={q}>Return to admin page</a></p>' + HTML_END, 400, None, None)
                with get_conn() as conn:
                    conn.execute("DELETE FROM USER WHERE ID = ?", (i,))
            return (await admin_head() + f'<h1 class="rainbow rainbow_text_animated">Item was deleted!</h1><p><a href=/admin?table={q}>Return to admin page</a></p>' + HTML_END, 200, None, None)
        except:
            return (await admin_head() + await err_body(400) + HTML_END, 400, None, None)
    else:
        return (await admin_head() + await err_body(400) + HTML_END, 400, None, None)
