import model
import peewee
from model import User, Drill
import nodes
from flask import Flask, g, redirect, request, session, url_for, abort, flash, render_template

import json
import peewee

app = Flask(__name__)
app.secret_key = "THIS IS A HUGE SECRET"

@app.before_request
def before_request():
    model.db.connect()
    uid = session.get("user_id")
    if uid:
        try:
            g.user =  User.get(User.id == uid)
        except peewee.DoesNotExist, e:
            session.pop("user_id")

@app.after_request
def after_request(response):
    model.db.close()
    return response


@app.route("/")
def index():
    """Steps: Query for the latest unfilled exercise. If none exists, create a new one. Display it."""
    if not session.get("user_id"):
        return redirect(url_for("show_login"))

    drill = g.user.get_latest_drill()
    drills_today = g.user.num_solved()
    print drills_today

    return render_template("prompt.html", problem=drill, num_solved = drills_today)

@app.route("/solve/<int:id>", methods=["POST"])
def solve(id):
    print request.form
    attempt = request.form.get("solution")
    drill = Drill.get(Drill.id == id)
    drill.solution = attempt
    drill.save()

    success = drill.compare()

    return json.dumps({"result": success})



@app.route("/next")
def next():
    try:
        unsolved = Drill.get(Drill.user == g.user, Drill.solved == False)
        unsolved.solved = True
        unsolved.save()
    except peewee.DoesNotExist, e:
        pass

    return redirect("/")


@app.route("/login", methods=["GET"])
def show_login():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("email")
    if not email:
        flash("Please enter an email address.")
        return redirect(url_for("show_login"))

    name = email.strip()

    user  = User.get_by_name(name)
    session["user_id"] = user.id

    return redirect("/")

@app.route("/reset")
def reset():
    session.pop("user_id")
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
