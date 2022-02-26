"""Simple flask CSRF protection\n\n In a form, add a <input type='hidden' value=csrf_protection.csrf.token, name='csrf_token'>\n\nMake Sure to set the CSRF token first, or use .generate_csrf_token()"""

from flask import current_app, Flask, request
from flask_api import status
from secrets import token_urlsafe
from hashlib import sha256
global csrf_is_inited
csrf_is_inited = False
class csrf:
    token = ""
app = Flask(__name__)
if csrf_is_inited == True:
    @app.name.before_request()
    def check_csrf():
        if request.form.get("csrf_token") != csrf.token:
            return "CSRF Token Missing", status.HTTP_403_FORBIDDEN
def generate_csrf_token():
    csrf.token = sha256(token_urlsafe(16).encode()).hexdigest()
            
def init():
    csrf_is_inited = True
