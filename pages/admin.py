# `admin.py` - This file contains the admin pages, which allow users with sufficient privileges to edit tables by a web interface
# This should only be visible to admins (99) and moderators (50).
# Moderators can use this to gain direct & intuitive control over certain SQL tables

from pages.parts import html_head, HTML_END, err_body, redirect, DEFAULT_STYLE
from db.db import get_conn
from db.user import hash_password, get_privilege, get_style
from html import escape

# Admin header. Much like the html_head() function, but it doesn't check privileges, adds
# a second bar to navigate tables, and can include JS
async def admin_head(user, include=''):
    style = get_style(user)
    if style == 'default':
        style = DEFAULT_STYLE
    with get_conn() as conn:
        r = conn.execute("SELECT dname, uname FROM USER WHERE ID = ?", (user,)).fetchone()
    return f"""<!DOCTYPE html>
<html>
<head>
<link rel="stylesheet" href="/static_web/style/base.css">
<link rel="stylesheet" href="/static_web/style/{style}.css">
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
  <div class="dropdown-content"><a href="/user?id={user}">Profile</a><a href="/prefs">Preferences</a><a href="/logout">Log out</a>
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

# This JS snippet allows the delete confirmation to be displayed on the table view page
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

# This JS snippet allows a "Now" button to be displayed on forms where date fields are present
# the button sets the corresponding field to the current date and time
JS_NOW_BTN = """<script>
  function setNow(fieldId) {
    const now = new Date();
    document.getElementById(fieldId).value = now.toISOString();
  }
</script>"""

# This function displays items within a range of IDs in the specified table
async def admin_view(name, frm=0, to=100):
    with get_conn() as conn:
        t = f"""<p style=\"font-size: 18px;\">Showing IDs {frm}-{to}.<form action="admin">
        <input type="hidden" id="table", name="table", value="{name}">
        <label for="from">Show IDs from: </label><input type="text" id="from" name="from" value={frm}> <label for="to">to: </label>
        <input type="text" id="to" name="to" value={to}><input class=login_submit type="submit" value="Submit">
        </form></p>
        """
        t += f"""<p><a href=admin?table={name}&action=search style=\"font-size: 18px;\">Search table for entries</a>"""
        t += f'<p><a href=admin?table={name}&action=insert style=\"font-size: 18px;\">Insert new entry into table</a>'
        tbl = []
        hrs = []
        cnt = 0
        if name.lower() == "user":
            tbl = conn.execute("SELECT * FROM USER WHERE ID >= ? AND ID <= ?", (frm, to)).fetchall()
            hrs = ["ID", "dname", "uname", "class", "pw_hash", "created", "pw_date", "SESS_ID", "SESS_Expiry", "dummy_pw", 'theme']
        elif name.lower() == "artists":
            tbl = conn.execute("SELECT * FROM ARTISTS WHERE ID >= ? AND ID <= ?", (frm, to)).fetchall()
            hrs = ["ID", "Name", "Orig_Name", "ON_Lang", "Alt_Names", "AN_Lang", "Description", "Country"]
        t += await html_table(name, tbl, hrs)
        t += "<br>"
        return t

async def admin_search(name, post):
    with get_conn() as conn:
        x_tup = ()
        if name.lower() == "user":
            x_string = "SELECT * FROM USER"
            hrs = ["ID", "dname", "uname", "class", "created", "pw_date", "SESS_ID", "SESS_Expiry", "dummy_pw", 'theme']
            hrs_d = ["ID", "dname", "uname", "class", "created", "pw_hash", "pw_date", "SESS_ID", "SESS_Expiry", "dummy_pw", 'theme']
        elif name.lower() == "artists":
            x_string = "SELECT * FROM ARTISTS"
            hrs = hrs_d = ["ID", "Name", "Orig_Name", "ON_Lang", "Alt_Names", "AN_Lang", "Description", "Country"]
        else:
            return []
        for f in hrs:
            if post[f] != '':
                if x_tup == ():
                    x_string += " WHERE "
                else:
                    x_string += " AND "
                x_string += f"{f} = ?"
                x_tup = x_tup + (post[f],)

        tbl = conn.execute(x_string, x_tup).fetchall()
        t = f"""<p style=\"font-size: 18px;\">Showing search results.<form action="admin">
        <input type="hidden" id="table", name="table", value="{name}">
        <label for="from">Show IDs from: </label><input type="text" id="from" name="from" value=0> <label for="to">to: </label>
        <input type="text" id="to" name="to" value=100><input class=login_submit type="submit" value="Submit">
        </form></p>
        """
        t += f"""<p><a href=admin?table={name}&action=search style=\"font-size: 18px;\">Search table for entries</a>"""
        t += f'<p><a href=admin?table={name}&action=insert style=\"font-size: 18px;\">Insert new entry into table</a>'
        t += await html_table(name, tbl, hrs_d)
        t += "<br>"
        return t


# This function produces a HTML table with specified headers (hrs) and table contents (tbl)
async def html_table(name, tbl, hrs):
    t = "<div style=\"overflow-x: auto;\"><table><tr>"
    for hr in hrs:
        t += f"<th class=\"mono-table\">{hr}</th>"
    t += f"<th class=\"mono-table\" colspan=2 style=\"color:brown;white-space: pre;\">{len(tbl)} items</th></tr>"
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
    t += "</table></div>"
    return t

# These fields are date fields, which means they get the "Now" button next to them in insert/edit forms
DATE_FIELDS = {'created', 'pw_date', 'SESS_Expiry'}

# This function produces the insert/edit form for an item in a table
async def edit_form(user, name, i=None, search=False):
    with get_conn() as conn:
        hrs = []
        r = None
        if name.lower() == "user":
            if get_privilege(user) != 99 and not search:
                return (await admin_head(user) + await err_body(401) + HTML_END, 401, None, None)
            if (i is not None):
                r = conn.execute("SELECT * FROM USER WHERE ID = ?", (i,)).fetchone()
            hrs = ["ID", "dname", "uname", "class", "pw_hash", "created", "pw_date", "SESS_ID", "SESS_Expiry", "dummy_pw", 'theme']
        elif name.lower() == "artists":
            if (i is not None):
                r = conn.execute("SELECT * FROM ARTISTS WHERE ID = ?", (i,)).fetchone()
            hrs = ["ID", "Name", "Orig_Name", "ON_Lang", "Alt_Names", "AN_Lang", "Description", "Country"]
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
            if search:
                t = f'<form action=\"/admin?table={name}&action=search\" method=post>'
            else:
                t = f'<form action=\"/admin/insert\" method=post><input type="hidden" id="table", name="table", value="{name}">'
            for j in range(len(hrs)):
                if hrs[j] == 'pw_hash':
                    if not search:
                        t += f'<label for="PW">PW (will be hashed): </label><input type="text" id="PW" name="PW"><br><br>'
                else:
                    now_btn = f' <button type="button" onclick="setNow(\'{hrs[j]}\')">Now</button>' if hrs[j] in DATE_FIELDS else ""
                    t += f'<label for="{hrs[j]}">{hrs[j]}: </label><input type="text" id="{hrs[j]}" name="{hrs[j]}">{now_btn}<br><br>'
        t += '<input class=login_submit type="submit" value="Submit"></form><br>'
    return t

# This function inserts an item into a table (endpoint /admin/insert)
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
                for f in ["class", "created", "pw_date", "SESS_ID", "SESS_Expiry", "dummy_pw", 'theme']:
                    if post[f] != '':
                        conn.execute(f"UPDATE USER SET {f} = ? WHERE ID = ?", (post[f], ins_id))
        elif q.lower() == "artists":
            with get_conn() as conn:
                if post['ID'] == '':
                    cursor = conn.execute("INSERT INTO ARTISTS (Name) VALUES (?)", (post['Name'],))
                else:
                    cursor = conn.execute("INSERT INTO ARTISTS (ID, Name) VALUES (?, ?)", (post['ID'], post['Name']))
                ins_id = cursor.lastrowid
                for f in ["Orig_Name", "ON_Lang", "Alt_Names", "AN_Lang", "Description", "Country"]:
                    if post[f] != '':
                        conn.execute(f"UPDATE ARTISTS SET {f} = ? WHERE ID = ?", (post[f], ins_id))
        return (await admin_head(user) + f'<h1>Item inserted at ID={ins_id}!</h1><p><a href=/admin?table={q}>Return to admin page</a></p>' + HTML_END, 200, None, None)
    except:
        return (await admin_head(user) + await err_body(400) + HTML_END, 400, None, None)

# This function edits an exsting item into a table (endpoint /admin/edit)
async def admin_edit(user, post):
    try:
        q = post["table"]
        i = int(post['ID'])
        if q.lower() == 'user':
            if get_privilege(user) != 99:
                return (await admin_head(user) + await err_body(401) + HTML_END, 401, None, None)
            with get_conn() as conn:
                try:
                    p = post['pw_clear']
                except:
                    p = "no"
                if p == "yes":
                    conn.execute("UPDATE USER SET pw_hash = NULL WHERE ID = ?", (i,))
                elif post['PW'] != '':
                    conn.execute("UPDATE USER SET pw_hash = ? WHERE ID = ?", (hash_password(post['PW']), i))
                for f in ["dname", "uname","class", "created", "pw_date", "SESS_ID", "SESS_Expiry", "dummy_pw", 'theme']:
                    if post[f] != '':
                        conn.execute(f"UPDATE USER SET {f} = ? WHERE ID = ?", (post[f], i))
                    else:
                        conn.execute(f"UPDATE USER SET {f} = NULL WHERE ID = ?", (i,))
        elif q.lower() == "artists":
                for f in ["Name", "Orig_Name", "ON_Lang", "Alt_Names", "AN_Lang", "Description", "Country"]:
                    if post[f] != '':
                        conn.execute(f"UPDATE ARTISTS SET {f} = ? WHERE ID = ?", (post[f], i))
                    else:
                        conn.execute(f"UPDATE ARTISTS SET {f} = NULL WHERE ID = ?", (i,))
        return (await admin_head(user) + f'<h1>Item at ID={i} updated!</h1><p><a href=/admin?table={q}>Return to admin page</a></p>' + HTML_END, 200, None, None)
    except:
        return (await admin_head(user) + await err_body(400) + HTML_END, 400, None, None)

# This is the main logic to handle most features of the admin page
# /admin or /admin&action=view : Go into table display mode
# /admin?table=user : Display table user (by default display items 0 to 100)
# /admin?table=user&from=0&to=10 : Display items in table user from 0 to 10
# /admin?table=user&action=insert : Insert a new item into table user (only privilege class == 99 is allowed)
# /admin?table=user&action=edit&id=2 : Edit item 2 in table user (only privilege class == 99 is allowed)
# /admin?table=user&action=delete&id=1 : Delete item 1 in table user (only privilege class == 99 is allowed)
# Insert and Edit display a form which submits to /admin/insert and /admin/edit respectively
# Delete directly deletes the entry, which is why there is a JS confirmation on the view page
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
            return (await admin_head(user, JS_DELETE_CONFIRM) + await admin_view(q, f, t) + HTML_END, 200, None, None)
        except:
            return (await admin_head(user) + "<h1>Select a table to view from the header above.</h1>" + HTML_END, 200, None, None)
    elif a == "insert":
        try:
            q = query['table']
            if (q.lower() == "user") and (get_privilege(user) != 99):
                return (await admin_head(user) + await err_body(401) + HTML_END, 401, None, None)
            return (await admin_head(user, JS_NOW_BTN) + await edit_form(user, q) + HTML_END, 200, None, None)
        except:
            return (await admin_head(user) + await err_body(400) + HTML_END, 400, None, None)
    elif a == "edit":
        try:
            q = query['table']
            if (q.lower() == "user") and (get_privilege(user) != 99):
                return (await admin_head(user) + await err_body(401) + HTML_END, 401, None, None)
            i = int(query['id'])
            return (await admin_head(user, JS_NOW_BTN) + await edit_form(user, q, i) + HTML_END, 200, None, None)
        except:
            return (await admin_head(user) + await err_body(400) + HTML_END, 400, None, None)
    elif a == "delete":
        try:
            i = int(query["id"])
            q = query['table']
            if q.lower() == 'user':
                if get_privilege(user) != 99:
                    return (await admin_head(user) + await err_body(401) + HTML_END, 401, None, None)
                if i == 0:
                    return (await admin_head(user) + f'<h1 style="color:red;">You cannot delete the admin user!!!!!!</h1><p><a href=/admin?table={q}>Return to admin page</a></p>' + HTML_END, 400, None, None)
                with get_conn() as conn:
                    conn.execute("DELETE FROM USER WHERE ID = ?", (i,))
            if q.lower() == 'artists':
                with get_conn() as conn:
                    conn.execute("DELETE FROM ARTISTS WHERE ID = ?", (i,))
            return (await admin_head(user) + f'<h1 class="rainbow rainbow_text_animated">Item was deleted!</h1><p><a href=/admin?table={q}>Return to admin page</a></p>' + HTML_END, 200, None, None)
        except:
            return (await admin_head(user) + await err_body(400) + HTML_END, 400, None, None)
    elif a == "search":
        try:
            q = query['table']
            if len(post) > 0:
                return (await admin_head(user, JS_DELETE_CONFIRM) + await admin_search(q, post) + HTML_END, 200, None, None)
            else:
                return (await admin_head(user, JS_NOW_BTN) + await edit_form(user, q, search=True) + HTML_END, 200, None, None)
        except:
            return (await admin_head(user) + await err_body(400) + HTML_END, 400, None, None)
    else:
        return (await admin_head(user) + await err_body(400) + HTML_END, 400, None, None)
