from pages.parts import html_head, HTML_END, err_body

REGISTRATION_CLOSED = False

LOGGED_IN = '<h1 class="rainbow rainbow_text_animated">You have successfully logged in.</h1><p><a href=/home>Return to home page</a></p>'

LOGIN_FORM = """<div class=login_center><h2>Login:</h2></div>
<div class=login_center><form action="/login">
  <label for="uname">Username:</label><br>
  <input type="text" id="uname" name="uname"><br><br>
  <label for="pwd">Password:</label><br>
  <input type="password" id="pwd" name="pwd"><br><br>
  <input class=login_submit type="submit" value="Submit">
</form></div>
<div class=login_center><p>Don't have an account yet? <a href=/register>Register</a> now.</p></div>
"""

REGISTER_FORM = """<div class=login_center><h2>Register:</h2></div>
<div class=login_center><form action="/login">
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
<div class=login_center><p>All fields above can be changed later.</p></div>
<div class=login_center><p>Already have an account? <a href=/login>Log in</a>.</p></div>
"""

CLOSED_FORM = """<div class=login_center><h2>Register:</h2></div>
<div class=login_center><p>Registration is currently closed.</p></div>
<div class=login_center><p>Already have an account? <a href=/login>Log in</a>.</p></div>
"""

async def login_page(s, context):
    user = context['user_id']
    if user is not None:
        return (await html_head("gensou : logged in", user) + LOGGED_IN + HTML_END, 200)
    return (await html_head("gensou : login", user) + LOGIN_FORM + HTML_END, 200)


async def register_page(s, context):
    user = context['user_id']
    if REGISTRATION_CLOSED:
        return (await html_head("gensou : registration closed", user) + CLOSED_FORM + HTML_END, 200)
    if user is not None:
        return (await html_head("gensou : logged in", user) + LOGGED_IN + HTML_END, 200)
    return (await html_head("gensou : register", user) + REGISTER_FORM + HTML_END, 200)
