"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session, url_for
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

####################################################
# User-related routes
####################################################

@app.route('/users')
def user_list():
    """Show list of users, with links to detailed user pages."""

    users = User.query.all()

    return render_template("user_list.html", users=users)

@app.route('/users/<user_id>')
def user_details(user_id):
    """Show a user's profile page."""

    user = User.query.filter(User.user_id == user_id).first()
    ratings = Rating.query.filter(Rating.user_id == user_id).all()
    # ratings = Rating.query.options(db.joinedload('movie')).filter(Rating.user_id == user_id).order_by(Movie.title).all()
    # FIXME: figure out how to sort movies by title

    print ratings[0:11]

    return render_template("user_details.html", user=user, ratings=ratings)

####################################################
# Movie-related routes
####################################################

@app.route('/movies')
def movie_list():
    """Shows a list of movie titles, with links to detailed movie pages."""

    # Fetch all movies from database, filter out unknown titles, and sort by title.
    movies = Movie.query.filter(Movie.title != "").order_by(Movie.title).all()

    return render_template("movie_list.html", movies=movies)

@app.route('/movies/<movie_id>')
def movie_details(movie_id):
    """Shows a movie's information, including ratings."""

    movie = Movie.query.filter(Movie.movie_id == movie_id).first()
    ratings = Rating.query.filter(Rating.movie_id == movie_id).all()

    if "user_id" in session:
        user_rating = Rating.query.filter(Rating.movie_id == movie_id, Rating.user_id == session["user_id"]).first()
    else:
        user_rating = None

    return render_template("movie_details.html",
        movie=movie,
        ratings=ratings,
        user_rating=user_rating)

####################################################
# Rating routes
####################################################

@app.route('/update-rating', methods=['GET'])
def rating_form():
    """Displays the rating form."""

    user_id = session["user_id"]
    print user_id
    movie_id = request.args.get("movie_id")
    print movie_id
    movie = Movie.query.filter(Movie.movie_id == movie_id).first()
    print movie
    rating = Rating.query.filter(Rating.movie_id == movie_id, 
                                 Rating.user_id == user_id).first()
    print rating

    return render_template("rating_form.html", movie=movie, rating=rating)

@app.route('/update-rating', methods=['POST'])
def handle_rating():
    """Handles input from rating form."""

    # Get the values needed to create a rating.
    movie_id = request.form["movie_id"]
    score = request.form["score"]
    user_id = session["user_id"]

    # Fetch a rating record.
    rating = Rating.query.filter(Rating.movie_id == movie_id, 
                                 Rating.user_id == user_id).first()
   
    # If the fetched rating record exists, update it with new rating.
    if rating:
        rating.score = score
        db.session.commit()
        flash("Your rating has been updated, indecisive CLOWN.")

    # If the rating record doesn't exist, create a new rating in the database.
    else:
        rating = Rating(movie_id=movie_id, user_id=user_id, score=score)
        db.session.add(rating)
        db.session.commit()
        flash("Thanks for rating. LIKE A CLOWN.")

    return redirect(url_for('.movie_details', movie_id=movie_id))


####################################################
# Registration routes
####################################################

@app.route('/register', methods=['GET'])
def register_form():
    """Displays the registration form."""

    return render_template("register_form.html")

@app.route('/register', methods=['POST'])
def handle_register():
    """Handles input from registration form."""

    email = request.form["email"]
    password = request.form["password"]
    age = request.form["age"]
    zipcode = request.form["zipcode"]

    user = User.query.filter(User.email == email).first()

    if user:
        flash("That email has already been registered.")
        return redirect("/register")
    else:
        # If the user doesn't exist, create one.
        user = User(email=email, password=password, age=age, zipcode=zipcode)
        db.session.add(user)
        db.session.commit()
        flash("Account created. That's a great email. FOR A CLOWN.")
        
        #Code 307 preserves the POST request, including form data.
        return redirect("/login", code=307)

####################################################
# Authentication/Deauthentication routes
####################################################

@app.route('/login', methods=['GET'])
def login_form():
    """Displays the login form."""

    return render_template("login_form.html")

@app.route('/login', methods=['POST'])
def handle_login():
    """Handles input from login/registration form."""

    email = request.form["email"]
    password = request.form["password"]

    user = User.query.filter(User.email == email).first()

    if user:
        if password != user.password:
            flash("Way to enter the wrong password, CLOWN.")
            return redirect("/login")
        else:
            #add their user_id to session
            session["user_id"] = user.user_id
            print "\n\nSession:", session, "\n\n"
            flash("You've been logged in. Not bad. For a CLOWN.")
            return redirect(url_for('.user_details', user_id=user.user_id))

    else:
        flash("No account with that email exists.")
        flash("Did you make a typo, CLOWN?")
        return redirect("/login")


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
