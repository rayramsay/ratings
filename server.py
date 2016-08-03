"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session
#from flask_debugtoolbar import DebugToolbarExtension

from model import User, Rating, Movie, connect_to_db, db


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    return render_template("homepage.html")


@app.route('/users')
def user_list():
    """Show list of users."""

    users = User.query.all()

    return render_template("user_list.html", users=users)


@app.route('/register', methods=['GET'])
def register_form():
    """Displays the login/registration form."""

    return render_template("register_form.html")


@app.route('/register', methods=['POST'])
def handle_register():
    """Handles input from login/registration form."""

    email = request.form["email"]
    password = request.form["password"]

    user = User.query.filter(User.email == email).first()

    if user:
        if password != user.password:
            flash("Way to enter the wrong password, CLOWN.")
            return redirect("/register")
    else:
        # If the user doesn't exist, create one.
        user = User(email=email, password=password)
        db.session.add(user)
        db.session.commit()
        flash("Account created. That's a great username. FOR A CLOWN.")

    #add their user_id to session
    session["user_id"] = user.user_id
    print "\n\n\n\nSession", session, "\n\n\n\n"
    flash("You've been logged in. Not bad. For a CLOWN.")

    return redirect("/")

@app.route('/logout')
def logout():

    if "user_id" in session:
        del session["user_id"]
        flash("You've been logged out, CLOWN.")
    print "\n\n\n\nSession", session, "\n\n\n\n"

    return redirect("/")


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    #DebugToolbarExtension(app)

    app.run()
