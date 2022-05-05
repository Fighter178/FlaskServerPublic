from __future__ import with_statement			
from time import sleep
from flask import Flask, flash, redirect, url_for, render_template, session, request, abort, send_from_directory
from secrets import token_urlsafe
from hashlib import sha256
from flask_recaptcha import ReCaptcha
from flask_cors import CORS
from validators import url as is_url
from urllib.parse import urlparse
import jinja2
import pyshorteners
def shorten_url(long_url):
    #TinyURL shortener service
    type_tiny = pyshorteners.Shortener()
    short_url = type_tiny.tinyurl.short(long_url)
    return short_url
#context = ssl.SSLContext()
#context.load_cert_chain('fullchain.pem', 'privkey.pem')

app = Flask(__name__)
app.url_map.strict_slashes = False

CORS(app)   
#app.secret_key=sha256(token_urlsafe(16).encode()).hexdigest()
app.secret_key = "ed37e3308d7f1973d6b74fdc058a31ffda681f9d7f7cb9d2840d71d14acd1022" # <-- secret
app.config['RECAPTCHA_SITE_KEY'] = '6LdPrVceAAAAABZiwS1JBfw7qYfW_sLzSzmMzWNP' # <-- Add your site key
app.config['RECAPTCHA_SECRET_KEY'] = '6LdPrVceAAAAANSZvKNe8MQzwieTAQKrBz5ak6aW' # <-- Add your secret key
AUTO_LOGIN_ENABLED = True #set to false when in production

jinja_env = jinja2.Environment()

recaptcha = ReCaptcha(app)
#csrf = CSRFProtect(app)
CSRF_TOKEN =  sha256(token_urlsafe(16).encode()).hexdigest()
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
)
@app.before_request
def clear_trailing():
    rp = request.path 
    if rp != '/' and rp.endswith('/'):
        return redirect(rp[:-1])
@app.route("/userscripts/google-disabler.<ver>.js")
def google_disabler(ver="0.1"):
    return send_from_directory('static', f"google-disabler.{ver}.js")
@app.get("/autologin/")
def auto_login():
    if AUTO_LOGIN_ENABLED:
        session["user"] = "sys-AutoLogin-DevOnly"
        session["admin"] = "true"
        return redirect(url_for("search"))
    else: abort(404)

app.config.update(
    PERMANENT_SESSION_LIFETIME=86400000 / 4 #will remember a user's session for 6 hours.
)
def url_parser(url):
    parts = urlparse(url)
    directories = parts.path.strip('/').split('/')
    queries = parts.query.strip('&').split('&')
    
    elements = {
        'scheme': parts.scheme,
        'netloc': parts.netloc,
        'path': parts.path,
        'params': parts.params,
        'query': parts.query,
        'fragment': parts.fragment,
        'directories': directories,
        'queries': queries,
    }
    
    return elements

def gen_new_csrf_token():
    global CSRF_TOKEN 
    CSRF_TOKEN = sha256(token_urlsafe(16).encode()).hexdigest()
def send_to_login(onComplete=""):
    """Function to send a user to the login page. onComplete is the function to redirect to after user logs in. """
    flash("You must log in!", "alert")
    gen_new_csrf_token()
    return redirect(url_for("login", done=onComplete)), 302
@app.after_request
def apply_caching(response):
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["HTTP-HEADER"] = "VALUE"
    response.headers['X-Content-Type-Options'] = "nosniff"
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response
def setTimeDelay(time):
        """Returns True after the time is met. (in seconds)\nIt is reccomended to add this to a new thread to async it."""
        sleep(int(time))
        return True
@app.route("/dev/mde/")
def mde():
    return redirect(url_for("mde"))
@app.route("/dev/htmlp/")
def htmlp():
    return render_template("htmlp_docs.html")
@app.route("/trap/")
def trap():
    return render_template("trap.html")
@app.route("/trap/lock/")
def trap_lock():
    return render_template("trap_lock.html")
@app.route("/content-request-err/")
def csrf_token_invalid():
    flash("ERROR, 400", "alert-error")
    return render_template("bad_req_err.html"), 400
@app.errorhandler(404)
def page_not_found(e):
    flash("Error: 404", "notify-error")
    return render_template("page_not_found.html"), 404
@app.errorhandler(500)
def internal_server_error(e):
    flash("ERROR: 500", "alert-error")
    return render_template("internal_server_error_500.html"), 500
@app.errorhandler(400)
def bad_request(e):
    flash("ERROR, 400", "alert-error")
    return render_template("bad_req_err.html", details=e), 400
@app.errorhandler(405)
def method_not_allowed(e):
    flash("ERROR: 405", "alert-error")
    return render_template("method_not_allowed.html", method=request.method), 405

@app.route("/js-not-on/")
def js_disabled():
    return "JS (JavaScript) is required for many of our core services to work properly!<br>JS is what allows the ReCaptcha to work & load, search to load, games to run, and for the comments to work. <br>Without ReCaptcha, you cannot log in. It will give you an error when you attempt to log in, related to ReCaptcha, as it cannot load! The navbar on some pages will also not show correctly sometimes!"
@app.route("/admin/login/", methods=["GET", "POST"])
def admin_login():
    if "admin" in session:
        return redirect(url_for("admin_console"))
    if request.method == "POST":
        if request.form.get("csrf_token") == CSRF_TOKEN:
            if request.form.get("adminPassw") != "0903admin":
                return redirect(url_for("admin_login"))
            else:
                session["user"] = request.form.get("adminName")
                session["admin"] = "true"
                flash("Logged in as admin", "notify-success")
                return redirect(url_for("search"))
    return render_template("admin_login.html", csrf_token=CSRF_TOKEN), 200
@app.route("/admin/console/")
def admin_console():
    if "admin" in session:
        return render_template("admin_console.html")
    abort(404)
@app.route("/admin/console/commit/", methods=["GET", "POST"])
def admin_console_commit():
    if "admin" in session:
        if request.form.get("logoutall") == "on":
            session.clear() #log everyone out
            flash("Logged Out!", "notify")
            return redirect(url_for("login"))
        if request.form.get("reset-secret-key") == "on":
            app.secret_key = sha256(token_urlsafe(16).encode()).hexdigest()
            return redirect(url_for("admin_login"))
        if request.form.get("shutdown") == "on":
            if request.form.get("ownerKey") == "adminAcceptableKey":
                flash("Sorry! the server just unexpectedly went temporally went offline", "alert-info")
                shutdown_func = request.environ.get('werkzeug.server.shutdown')
                shutdown_func()
        return redirect(url_for("admin_console"))
    abort(404)
@app.route("/adminCheck/")
def admin_check():
    return redirect(url_for("whoami"))
@app.route("/whoami/")
def whoami():
    if "admin" in session:
        return render_template("admin_check.html", userType="an Admin."), 200
    else:
        return render_template("admin_check.html", userType="Standard User"), 200
@app.route("/")
def home():
    if "user" in session:
        flash("Already Logged in!", "notify")
        return redirect(url_for("search"))
    return render_template("index.html")
@app.route("/creator/") 
def creator():
    if "user" in session:
        return render_template("creatorPage.html")
    return send_to_login("creator")
@app.route("/comment/")
def comment():
    if "user" in session:
        return render_template("comment.html")
    return send_to_login("comment")
@app.route("/comment/policy/")
def comment_policy():
    if "user" in session:
        return render_template("comment-policy.html")
    return send_to_login("comment-policy")   
@app.route("/page-creator/")
def page_creator():
    return render_template("page_creator.html")
@app.post("/page-creator/make")
def make_page():
    title= "title="+request.form.get("pg-title")
    if request.form.get("title-branding") != "on":
        title_branding = "&rTitle=true"
    else: title_branding = "&rTitle=false"
    heading1 = "&heading1="+request.form.get("hd1-txt")
    if request.form.get("center-hd1") == "on":
        heading1_center ="&heading1-center=true"
    else: heading1_center = "&heading1-center=false"
    content = "&content="+request.form.get("main-content")
    if request.form.get("center-content") == "on":
        content_center = "&content-center=true"
    else: content_center = "&content-center=false"
    if request.form.get("cute-image") == "on":
        cute_image = "&cute-image=true"
    else: cute_image = "&cute-image=false"
    query = f'{title}{title_branding}{heading1}{heading1_center}{content}{content_center}{cute_image}'
    hostname=request.host
    url = f'{hostname}/page-creator/view?{title}{title_branding}{heading1}{heading1_center}{content}{content_center}{cute_image}'
    return render_template("link_viewer_for_page_creator.html", url=url, host=hostname, query=query, surl=shorten_url(url))
@app.route("/page-creator/view/")
def view_page():
    args = request.args
    jinja2.escape(args.get("content", type=str)).unescape().replace("\n", "<br>")
    return render_template("view_page_from_creator.html", title=args.get("title", default="Untitled Page", type=str), hd1=args.get("heading1", default="", type=str), main_content=args.get("content", default="", type=str))
@app.route("/page-creator/make-tiny/<url>")
def make_tiny(url):
    return shorten_url(url)
@app.route("/login/", methods=["GET", "POST"])
def login():
    args = request.args
    if "user" in session:
        flash("Already Logged in!", "notify")
        if args and args.get("done", "search", str):
            return redirect(url_for(args.get("done", "search", str)))
        else: 
            return redirect(url_for("search"))
    else:
        message = '' # Create empty message
        if request.method == 'POST': # Check to see if flask.request.method is POST
            if request.form.get("csrf_token") != CSRF_TOKEN:
                return csrf_token_invalid()
            if recaptcha.verify():
                if request.form.get("name") != "":
                    session["user"] = request.form.get("name")
                    if request.form.get("autologout") == "on":
                        session["autologout"] = "true";
                        session["save-autologout-setting"] = "true"
                        flash("Quick Logout Enabled!", "notify-success")
                        flash("Logged in!", "notify-success")
                        if request.form.get("save-session") == "on":
                            session["save-session-setting"] = "true"
                            session.permanent = True
                        elif "save-session-setting" in session and request.form.get("save-session") == "off": 
                            session.pop("save-session-setting")
                            session.permanent = False
                    if "save-autologout-setting" in session and request.form.get("autologout") == "off":
                        session.pop("save-autologout-setting")
                    if args.get("done", default=url_for("search"), type=str):
                        return redirect(url_for(args.get("done", default="search", type=str)))
                    else:
                        flash("Logged in!", "notify-success")
                        return redirect(url_for("search"))
                message = "Fill out your name first!";
                flash("Name required", "notify-error")
                return render_template("login.html", message=message, csrf_token=CSRF_TOKEN), 200
            else:
                flash("ERROR, reCaptcha could not be verified.", "error")
                return redirect(url_for("home"))
    return render_template('login.html', message=message, csrf_token=CSRF_TOKEN), 200
@app.route("/logout/", methods=["POST", "GET"])
def logout():
    if "user" in session:
        if request.method == 'POST': # Check to see if flask.request.method is POST
            if request.form.get("csrf_token") == CSRF_TOKEN:
                session.pop("user")
                if "admin" in session:
                   session.pop("admin")
                flash("Logged out!", "notify")
                return redirect(url_for("login"))
            else: return redirect(url_for("csrf_token_invalid"))
        if "autologout" in session:
            session.pop("user")
            session.pop("autologout")
            if "admin" in session:
                session.pop("admin")
            flash("Automatically Logged Out!", "notify-success")
            return redirect(url_for("login"))
        return render_template('logout.html', csrf_token=CSRF_TOKEN), 200
    else:
        return send_to_login()

@app.route("/user/")
def user():
    flash("This page has moved!", "alert")
    return redirect(url_for("search")), 308 
@app.route("/search/")
def search():
    if "user" in session:
        user = session.get("user")
        return render_template("user.html", userName = user), 200
    else: 
        return send_to_login("search")
@app.route("/changelog/")
def changelog():
    if "user" in session:
        return render_template("changelog.html"), 200
    return send_to_login("changelog")
@app.route("/shortcuts/")
def shortcuts():
    return "<h1>Page Under Construction</h1><br><a href='/'>Go to homepage</a>"
    #return render_template("keyboard_shortcuts.html")
@app.route("/content.html")
def content():
    if "admin" in session:
        return render_template("content.html")
    abort(404)
@app.route("/games/breakout/")
def breakout():
    if "user" in session:
        return render_template("game-breakout.html")
    return send_to_login("breakout")

@app.route("/games/snake/")
def snake():
    if "user" in session:
        return render_template("game-snake.html")
    return send_to_login("snake")
@app.route("/games/snake/standard/")
def standard_snake():
    if "user" in session:
        return render_template("game-snake-noPause.html")
    return send_to_login("standard_snake")
@app.route("/games/snake/v2")
def snake_v2():
    if "user" in session:
        return render_template("game-snake2.html"), 200
    return send_to_login("snake_v2")
@app.route("/games/connect-four/")
def connect_four():
    if "user" in session:
        return render_template("game-connectFour.html")
    return send_to_login("connect_four")
@app.route("/games/tic-tac-toe/")
def tic_tac_toe():
    if "admin" in session:
        return render_template("tic_tac_toe.html")
    abort(404)
@app.route("/games/pong/")
def pong_mgr():
    args = request.args
    if args.get("vs", default="ai", type=str) == "ai":
        if args.get("mode", default="easy", type=str) == "easy":
            return render_template("games-loader-pong_mgr.html", vs="ai", mode="easy")
        elif args.get("mode", default="easy", type=str) == "hard":
            return render_template("games-loader-pong_mgr.html", vs="ai", mode="hard")
        return render_template("games-loader-pong_mgr.html")
@app.route("/games/pong/vs/ai/easy")
def pong_vs_ai_easy():
    if "user" in session:
        return render_template("game-pong_vs_ai-easy.html")
    return send_to_login("pong_vs_ai_easy")
@app.route("/games/pong/vs/ai/hard")
def pong_vs_ai_hard():
    if "user" in session:
        return render_template("games-pong_vs_ai-hard.html")
    return send_to_login("pong_vs_ai_hard")
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
            if is_url(args.get("continue")):
                
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
            return csrf_token_invalid()
    else:
        return "<h2>No query strings were provided</h2>", 400
@app.route("/cookie-settings/")
def cookie_settings():
    if "user" in session:
        return render_template("cookie-settings-page.html")
    else: return send_to_login("cookie_settings")
@app.route("/sim/error/500/")
def error_500():
    if "admin" in session:
        return None
    return "HTTP_ERROR_403: You are unauthorized to view this page.", 403
@app.route("/sim/error/404")
def error_404():
    return redirect("/sim/error/404/this-page-does-not-exist")
@app.route(("/sim"))
def sim():
    if "admin" in session:
        return "Simulator for debug purposes.", 200
    abort(404)
@app.route("/sim/error")
def sim_error():
    if "admin" in session:
        return "Error simulator for debug purposes.", 200
    abort(404)

if __name__ == "__main__":
    print("NOTE: If this is a production server, set AUTO_LOGIN_ENABLED to false.")
    app.run(ssl_context=("selfsigned.crt", "private.key"), port="443", host="0.0.0.0")
    #app.run(port="80", host="0.0.0.0")
    #csrf.init_app(app)
