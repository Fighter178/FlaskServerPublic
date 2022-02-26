import threading
from time import sleep
from flask import Flask, redirect, url_for, render_template, session, request
from flask_session import Session
from flask_wtf.csrf import CSRFProtect
from secrets import token_urlsafe
from hashlib import sha256
from flask_recaptcha import ReCaptcha
from flask_cors import CORS
from validators import url as is_url
import werkzeug

#context = ssl.SSLContext()
#context.load_cert_chain('fullchain.pem', 'privkey.pem')

app = Flask(__name__)
CORS(app)
app.secret_key=sha256(token_urlsafe(16).encode()).hexdigest()
app.secret_key = "testing. testing. testing."
app.config['RECAPTCHA_SITE_KEY'] = '6LdPrVceAAAAABZiwS1JBfw7qYfW_sLzSzmMzWNP' # <-- Add your site key
app.config['RECAPTCHA_SECRET_KEY'] = '6LdPrVceAAAAANSZvKNe8MQzwieTAQKrBz5ak6aW' # <-- Add your secret key


recaptcha = ReCaptcha(app)

#csrf = CSRFProtect(app)
CSRF_TOKEN =  sha256(token_urlsafe(16).encode()).hexdigest()

#how to use this? found out that my Flask server is vulerable to cookie stealing, and I found this on how to
#protect from it, but don't know how to use it, can someone please tell me? Or is just putting it in enough?
#It also breaks my login page, so that's great!
app.config.update(
    SESSION_COOKIE_SECURE=False,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
)

def gen_new_csrf_token():
    global CSRF_TOKEN 
    CSRF_TOKEN = sha256(token_urlsafe(16).encode()).hexdigest()
def send_to_login():
    gen_new_csrf_token()
    return redirect(url_for("login"))

@app.after_request
def apply_caching(response):
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["HTTP-HEADER"] = "VALUE"
    response.headers['X-Content-Type-Options'] = "nosniff"
    response.headers['X-XSS-Protection'] = "1; mode=bl ;mb/,ock"
    return response
def setTimeDelay(time):
        """Returns True after the time is met. (in seconds)\nIt is reccomended to add this to a new thread to asyc it."""
        sleep(int(time))
        return True
@app.route("/content-request-err/")
def csrf_token_invalid(e):
    return render_template("bad_req_err.html", details=e)
@app.errorhandler(404)
def page_not_found(e):
    return render_template("page_not_found.html"), 404
@app.errorhandler(500)
def internal_server_error(e):
    return render_template("internal_server_error_500.html"), 50
@app.errorhandler(400)
def bad_request(e):
    return render_template("bad_req_err.html", details=e), 400
@app.route("/admin/login/", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if request.form.get("adminPassw") != "admin1234":
            return redirect(url_for("admin_login"))
        else:
            session["user"] = request.form.get("adminName")
            session["admin"] = "true"
            return redirect(url_for("search"))
    return render_template("admin_login.html")
@app.route("/adminCheck/")
def admin_check():
    if "admin" in session:
        return render_template("admin_check.html", userType="an Admin.")
    else:
        return render_template("admin_check.html", userType="not an Admin.")
@app.route("/")
def home():
    if "user" in session:
        return redirect(url_for("search"))
    return render_template("index.html")

@app.route("/login/", methods=["GET", "POST"])
def login():
    if "user" in session:
           return redirect(url_for("user"))
    else:
        message = '' # Create empty message
        if request.method == 'POST': # Check to see if flask.request.method is POST
            if request.form.get("csrf_token") != CSRF_TOKEN:
                return redirect(url_for("csrf_token_invalid"))
            if recaptcha.verify(): # Use verify() method to see if ReCaptcha is filled out
                if request.form.get("name") != "":
                    message = 'Thanks for filling out the form!' # Send success message
                    session["user"] = request.form.get("name")
                    return redirect(url_for("search"))
                message = "Fill out your name first!";
                return render_template("login.html")
            else:
                message = 'Please fill out the ReCaptcha!' # Send error message
    return render_template('login.html', message=message, csrf_token=CSRF_TOKEN)
@app.route("/logout/", methods=["POST", "GET"])
def logout():
    if "user" in session:
        message = '' # Create empty message
        if request.method == 'POST': # Check to see if flask.request.method is POST
            if request.form.get("csrf_token") == CSRF_TOKEN:
                if recaptcha.verify(): # Use verify() method to see if ReCaptcha is filled out
                    message = 'Thanks for filling out the form!' # Send success message
                    session.pop("user")
                    if "admin" in session:
                        session.pop("admin")
                    return redirect(url_for("home"))
                else:
                    message = 'Please fill out the ReCaptcha!' # Send error message
            else: return redirect(url_for("csrf_token_invalid"))
        return render_template('logout.html', message=message, csrf_token=CSRF_TOKEN)
    else:
        return send_to_login()

@app.route("/user")
def user():
    return redirect(url_for("search"))
@app.route("/search")
def search():
    if "user" in session:
        user = session.get("user")
        return render_template("user.html", userName = user)
    else: return send_to_login()
@app.route("/content.html")
def content():
    return render_template("content.html")
@app.route("/games/breakout/")
def breakout():
    if "user" in session:
        return render_template("game-breakout.html")
    return send_to_login()

@app.route("/games/snake/")
def snake():
    if "user" in session:
        return render_template("game-snake.html")
    return send_to_login()
@app.route("/games/snake/standard/")
def standard_snake():
    if "user" in session:
        return render_template("game-snake-noPause.html")
    return send_to_login()
@app.route("/games/snake/v2")
def snake_v2():
    if "user" in session:
        return render_template("game-snake2.html"), 200
    return send_to_login()
@app.route("/services/redirect/", methods=["GET","POST"])
def redirect_service():
    siteKeys = [
        "key1",
        "key2",
        "key3",
        "test"
    ]
    if request.args:

        args = request.args
        
        if request.method == "GET":
            if is_url(args.get("continue")) == True:
                if args.get("passive", default="false") == "true":
                    if args.get("key", default="", type=str) in siteKeys:
                        return redirect(args.get("continue", default="", type=str))
                    return render_template("nonPassiveRedirectPage.html", csrf_token=CSRF_TOKEN, url=args.get("continue", default="DEBUG: NO URL PROVIDED;", type=str)), 200
                else:
                    return render_template("nonPassiveRedirectPage.html", csrf_token=CSRF_TOKEN, url=args.get("continue", default="DEBUG: NO URL PROVIDED;", type=str)), 200
            else:
                return "For Site Owner: CONTINE QUERY STRING IS NOT A VALID URL!", 400
        else:
            if request.form.get("csrf_token") == CSRF_TOKEN:
                return redirect(args.get("continue", default="", type=str))
            return csrf_token_invalid("Unknown Data Error")
    else:
        return "No query strigs were provided", 400
@app.route("/sim/error/500/")
def error_500():
    return None
@app.route("/sim/error/404")
def errror_404():
    return redirect("/sim/error/404/this-page-does-not-exist")
@app.route(("/sim"))
def sim():
    return "Simulator for debug purposes."
@app.route("/sim/error")
def sim_error():
    return "Error simulator for debug purpoes."

if __name__ == "__main__":
    
    app.run(host="0.0.0.0", port="80")
    
    #csrf.init_app(app)