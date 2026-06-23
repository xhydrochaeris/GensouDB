from pages.parts import html_head, HTML_END, err_body, redirect
from db.user import store_hash_password, verify_password, get_uid, new_session, pwd_is_dummy, destroy_session, create_user, dname_collision
import string

REGISTRATION_CLOSED = False

LOGGED_IN = '<h1 class="rainbow rainbow_text_animated">You have successfully logged in.</h1><p><a href=/home>Return to home page</a></p>'
LOGGED_OUT = '<h1 class="rainbow rainbow_text_animated">You have successfully logged out.</h1><p><a href=/home>Return to home page</a></p>'
PW_UPDATED = '<h1 class="rainbow rainbow_text_animated">You have successfully updated your password.</h1><p><a href=/home>Return to home page</a></p>'
REGISTER_SUCCESS = '<h1 class="rainbow rainbow_text_animated">Your account was successfully created!</h1><p><a href=/home>Return to home page</a></p>'

async def login_form(error=False):
    e = ''
    if error:
        e = "<div class=login_center><p style=\"color: red; font-weight: bold\">Username or password may be incorrect!</p></div>"
    return f"""<div class=login_center><h2>Login:</h2></div>
<div class=login_center><form action="/login" method=post>
  <label for="uname">Username:</label><br>
  <input type="text" id="uname" name="uname"><br><br>
  <label for="pwd">Password:</label><br>
  <input type="password" id="pwd" name="pwd"><br><br>
  <input class=login_submit type="submit" value="Submit">
</form></div>
{e}
<div class=login_center><p>Don't have an account yet? <a href=/register>Register</a> now.</p></div>
"""

async def register_form(error='0'):
    e = ''
    if error == '1':
        e = "<div class=login_center><p style=\"color: red; font-weight: bold\">Invalid username</p></div>"
    elif error == '2':
        e = "<div class=login_center><p style=\"color: red; font-weight: bold\">Invalid password</p></div>"
    elif error == '3':
        e = "<div class=login_center><p style=\"color: red; font-weight: bold\">Passwords do not match</p></div>"
    elif error == '4':
        e = "<div class=login_center><p style=\"color: red; font-weight: bold\">Display name too long</p></div>"
    elif error == '5':
        e = "<div class=login_center><p style=\"color: red; font-weight: bold\">Username too long</p></div>"
    elif error == '6':
        e = "<div class=login_center><p style=\"color: red; font-weight: bold\">Username already taken</p></div>"
    elif error == '7':
        e = "<div class=login_center><p style=\"color: red; font-weight: bold\">Display name already taken</p></div>"

    return f"""<div class=login_center><h2>Register:</h2></div>
<div class=login_center><form action="/register" method=post>
  <label for="dname">Display Name:</label><br>
  <input type="text" id="dname" name="dname"><br><br>
  <label for="uname">Username:</label><br>
  <input type="text" id="uname" name="uname"><br>
  <label>(only use alphanumeric, '-', '_')</label><br><br>
  <label for="pwd1">Password:</label><br>
  <input type="password" id="pwd1" name="pwd1"><br>
  <label>(at least 8 characters)</label><br><br>
  <label for="pwd2">Confirm Password:</label><br>
  <input type="password" id="pwd2" name="pwd2"><br><br>
  <input class=login_submit type="submit" value="Submit">
</form></div>
{e}
<div class=login_center><p>All fields above can be changed later.</p></div>
<div class=login_center><p>Already have an account? <a href=/login>Log in</a>.</p></div>
"""

async def dummy_form(error='0', dummy=True):
    e = ''
    if error == '2':
        e = "<div class=login_center><p style=\"color: red; font-weight: bold\">Invalid password</p></div>"
    elif error == '3':
        e = "<div class=login_center><p style=\"color: red; font-weight: bold\">Passwords do not match</p></div>"
    elif error == '1':
        e = "<div class=login_center><p style=\"color: red; font-weight: bold\">Incorrect old password</p></div>"
    elif error == '4':
        e = "<div class=login_center><p style=\"color: red; font-weight: bold\">New password should not be the same as old password</p></div>"

    d = ''
    if not dummy:
        d = """<label for="opwd">Old password:</label><br>
  <input type="password" id="opwd" name="opwd"><br><br>"""
    return f"""<div class=login_center><h2>Set your password:</h2></div>
    <div class=login_center><p>Your current password is outdated. Please set a new one.</p></div>
<div class=login_center><form action="/set_pw" method=post>
{d}
  <label for="pwd1">Password:</label><br>
  <input type="password" id="pwd1" name="pwd1"><br>
  <label>(at least 8 characters)</label><br><br>
  <label for="pwd2">Confirm Password:</label><br>
  <input type="password" id="pwd2" name="pwd2"><br><br>
  <input class=login_submit type="submit" value="Submit">
</form></div>
{e}
<div class=login_center><p>Password can be changed later.</p></div>
"""

CLOSED_FORM = """<div class=login_center><h2>Register:</h2></div>
<div class=login_center><p>Registration is currently closed.</p></div>
<div class=login_center><p>Already have an account? <a href=/login>Log in</a>.</p></div>
"""

async def login_page(user, context):
    if user is not None:
        return (await html_head("gensou : logged in", user) + LOGGED_IN + HTML_END, 200, None, None)
    try:
        uname = context['uname']
        pwd = context['pwd']
        uid = get_uid(uname)
        check = verify_password(uid, pwd)
        if check == 0:
            return (await html_head("gensou : login", user) + await login_form(True) + HTML_END, 200, None, None)
        elif check == 1:
            sess_id, sess_expiry = new_session(uid, days=30)
            return (await html_head("gensou : logged in", uid) + LOGGED_IN + HTML_END, 200, ["make_cookie"], [f"{uid}", sess_id])
        else:
            sess_id, sess_expiry = new_session(uid, days=30)
            return ("/set_pw", 200, ["redirect", "make_cookie"], [f"{uid}", sess_id])
    except:
        return (await html_head("gensou : login", user) + await login_form() + HTML_END, 200, None, None)

async def register_page(user, context):
    if REGISTRATION_CLOSED:
        return (await html_head("gensou : registration closed", user) + CLOSED_FORM + HTML_END, 200, None, None)
    if user is not None:
        return (await html_head("gensou : logged in", user) + LOGGED_IN + HTML_END, 200, None, None)
    try:
        dname = context['dname']
        # display name length limit
        if len(dname) > 40:
            return (await html_head("gensou : register", user) + await register_form('4') + HTML_END, 200, None, None)
        uname = context['uname']
        # username accepted char set
        if not(set(uname) <= set(string.ascii_letters + string.digits + '-' + '_')):
            return (await html_head("gensou : register", user) + await register_form('1') + HTML_END, 200, None, None)
        # empty username disallowed
        if len(uname) == 0:
            return (await html_head("gensou : register", user) + await register_form('1') + HTML_END, 200, None, None)
        # empty display name is set to username
        if len(dname) == 0:
            dname = uname
        # username length limit
        if len(uname) > 20:
            return (await html_head("gensou : register", user) + await register_form('5') + HTML_END, 200, None, None)
        # username collision
        if get_uid(uname) >= 0:
            return (await html_head("gensou : register", user) + await register_form('6') + HTML_END, 200, None, None)
        if dname_collision(dname):
            return (await html_head("gensou : register", user) + await register_form('7') + HTML_END, 200, None, None)
        pwd1 = context['pwd1']
        pwd2 = context['pwd2']
        if pwd1 != pwd2:
            return (await html_head("gensou : register", user) + await register_form('3') + HTML_END, 200, None, None)
        elif len(pwd1) < 8:
            return (await html_head("gensou : register", user) + await register_form('2') + HTML_END, 200, None, None)
        else:
            uid = create_user(dname, uname, pwd1)
            sess_id, sess_expiry = new_session(uid, days=30)
            return (await html_head("gensou : registration success", uid) + REGISTER_SUCCESS + HTML_END, 200, ["make_cookie"], [f"{uid}", sess_id])
    except:
        return (await html_head("gensou : register", user) + await register_form() + HTML_END, 200, None, None)

async def set_pw(user, context):
    if user is None:
        d = 2
    else:
        d = pwd_is_dummy(user)
    if d == 0:
        try:
            opwd = context['opwd']
            check = verify_password(user, opwd)
            if check == 0:
                return (await html_head("gensou : register", user) + await dummy_form('1', False) + HTML_END, 200, None, None)
            pwd1 = context['pwd1']
            pwd2 = context['pwd2']
            if pwd1 != pwd2:
                return (await html_head("gensou : register", user) + await dummy_form('3', False) + HTML_END, 200, None, None)
            elif len(pwd1) < 8:
                return (await html_head("gensou : register", user) + await dummy_form('2', False) + HTML_END, 200, None, None)
            elif verify_password(user, pwd1) == 1:
                return (await html_head("gensou : register", user) + await dummy_form('4', False) + HTML_END, 200, None, None)
            else:
                store_hash_password(user, pwd1)
                return (await html_head("gensou : password updated", user) + PW_UPDATED + HTML_END, 200, None, None)
        except:
            return (await html_head("gensou : register", user) + await dummy_form(dummy=False) + HTML_END, 200, None, None)
    elif d == 1:
        try:
            pwd1 = context['pwd1']
            pwd2 = context['pwd2']
            chk2 = verify_password(user, pwd1)
            if pwd1 != pwd2:
                return (await html_head("gensou : register", user) + await dummy_form('3') + HTML_END, 200, None, None)
            elif len(pwd1) < 8:
                return (await html_head("gensou : register", user) + await dummy_form('2') + HTML_END, 200, None, None)
            elif chk2 == 2:
                return (await html_head("gensou : register", user) + await dummy_form('4') + HTML_END, 200, None, None)
            else:
                store_hash_password(user, pwd1)
                return (await html_head("gensou : password updated", user) + PW_UPDATED + HTML_END, 200, None, None)
        except:
            return (await html_head("gensou : register", user) + await dummy_form() + HTML_END, 200, None, None)
        
    return (await html_head("gensou : error unauthorized", user) + await err_body(401) + HTML_END, 401, None, None)

async def logout(user):
    if user is not None:
        destroy_session(user)
    return (await html_head("gensou : logged out", None) + LOGGED_OUT + HTML_END, 200, ["clear_cookie"], None)
