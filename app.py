from collections import OrderedDict
from crypt import methods
from re import A
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from cs50 import SQL
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required
from datetime import timedelta, datetime

products = [["apple", "orange", "pineapple", "plum"], 
            ["banana", "grapes", "kiwi", "mango"], 
            ["passionfruit", "peach", "pears", "strawberry"]]

# Configure Application
app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True

app.secret_key = "abcdefghi"

db = SQL("sqlite:///ecommerce.db")

@app.after_request
def after_request(response):
    "Ensure responses arent cached"
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST":
        # user tried to add something to cart
        item = request.form.get("item")
        # create cart if cart does not exist yet
        if "cart" not in session:
            session["cart"] = {}
        # create item in cart
        if item not in session["cart"]:
            session["cart"][item] = 0
        session["cart"][item] += 1
        flash(item.title() + " Added To Cart!", "info")
        print(session["cart"])
        return render_template("index.html", products = products)  
    return render_template("index.html", products=products)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

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
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        if not username:
            return apology("must provide username", 400)
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        if len(rows) != 0:
            return apology("Username is not available", 400)
        if not password:
            return apology("Password must be set", 400)
        if password != confirmation:
            return apology("Password doesn't match confirmation")
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, generate_password_hash(password))
        flash("User registered successfully!", "info")
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        session["user_id"] = rows[0]["id"]
        return redirect("/")

    return render_template("register.html")


@app.route("/cart", methods=["GET", "POST"])
@login_required
def cart():
    # show items added to cart
    if "cart" not in session:
        return apology("No Items In The Cart Yet!")
    return render_template("cart.html", cart=session["cart"])

@app.route("/order", methods=["POST"])
@login_required
def order():
    # update database with the order
    if "cart" not in session:
        return apology("No Items In The Cart Yet!")
    order_id = db.execute("SELECT MAX(order_id) AS order_id FROM orders")[0]["order_id"]
    if order_id:
        order_id += 1
    else:
        order_id = 1
    dt = datetime.now().strftime("%y-%m-%d %H:%M:%S")
    for item, quantity in session["cart"].items():
        db.execute("INSERT INTO orders (order_id, user_id, item, quantity, datetime) VALUES (?, ?, ?, ?, ?)", 
            order_id, session.get("user_id"), item, quantity, dt)
    flash("Order Placed!")
    session["cart"] = {}
    return redirect("/")