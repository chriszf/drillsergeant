import model
import peewee
from model import User, Drill
import nodes
from flask import Flask, g, redirect, request, session, url_for, abort, flash, render_template

import peewee

app = Flask(__name__)
app.secret_key = "THIS IS A HUGE SECRET"

@app.before_request
def before_request():
    model.db.connect()
    uid = session.get("user_id")
    if uid:
        g.user =  User.get(User.id == uid)

@app.after_request
def after_request(response):
    model.db.close()
    return response


@app.route("/")
def index():
    """Steps: Query for the latest unfilled exercise. If none exists, create a new one. Display it."""
    if not session.get("user_id"):
        return redirect(url_for("show_login"))

    try:
        unsolved = Drill.get(Drill.user == g.user, Drill.solution == None)
    except peewee.DoesNotExist, e:
        unsolved = Drill.create(user = g.user)
        unsolved.generate()
        unsolved.save()

    print g.user.drills

    return "Blob"


@app.route("/login", methods=["GET"])
def show_login():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("email")
    if not email:
        flash("Please enter an email address.")
        return redirect(url_for("show_login"))

    email = email.strip()
    try:
        user = User.get(User.email == email)
    except peewee.DoesNotExist, e:
        user = User.create(email = email)
        user.save()

    session["user_id"] = user.id

    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
