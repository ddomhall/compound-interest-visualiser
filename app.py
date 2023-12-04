from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from markupsafe import Markup
from dateutil.relativedelta import relativedelta
from helpers import apology, login_required
from io import BytesIO
from matplotlib.figure import Figure
from datetime import datetime
import base64

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
def index():
    # Generate the figure **without using pyplot**.
    fig = Figure(figsize=[8, 4.5], facecolor="black", layout="constrained")
    ax = fig.subplots()
    ax.patch.set_facecolor('black')
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')
    ax.spines['bottom'].set_color('white')
    ax.spines['left'].set_color('white')

    fields = {
        'start': '', 
        'contribution': '',
        'value': '',
        'performance': '',
        'target': '',
    }

    if request.method == "POST":

        fields = {
            'start': datetime.strptime(request.form.get('start'), '%Y-%m'),
            'contribution': float(request.form.get('contribution')),
            'value': float(request.form.get('value')),
            'performance': float(request.form.get('performance')),
            'target': float(request.form.get('target')),
        }

        x = [fields['start']]
        y = [fields['value']]
        while y[-1] < fields['target']:
            x.append(x[-1] + relativedelta(months=1))
            y.append(y[-1] + fields['contribution'] + ((y[-1] + fields['contribution']) * fields['performance']/100/12))
        ax.plot(x, y)

    # Save it to a temporary buffer.
    buf = BytesIO()
    fig.savefig(buf, format="png")
    # Embed the result in the html output.
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    return render_template('index.html', data=Markup(f"<img src='data:image/png;base64,{data}' class='h-full rounded-2xl'/>"), fields=fields)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("need username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("need password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/home")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == 'POST':

        username = request.form.get('username')
        password = request.form.get('password')
        confirmation = request.form.get('confirmation')
        # Ensure username was submitted
        if not username or len(db.execute('SELECT * FROM users WHERE username = ?', username)) != 0:
            return apology("username error")

            # Ensure password was submitted
        elif not password or not confirmation or password != confirmation:
            return apology("password error")

        db.execute('INSERT INTO users (username, hash) VALUES(?, ?)', request.form.get('username'), generate_password_hash(password)) 

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        return redirect('/')

    else:
        return render_template("register.html")

@app.route("/home")
def home():
    return render_template("home.html")
