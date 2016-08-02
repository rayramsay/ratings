"""Utility file to seed ratings database from MovieLens data in seed_data/"""

from sqlalchemy import func
from model import User, Movie, Rating

from datetime import datetime

from model import connect_to_db, db
from server import app


def load_users():
    """Load users from u.user into database."""

    print "Users"

    # Delete all rows in table, so if we need to run this a second time,
    # we won't be trying to add duplicate users
    User.query.delete()

    # Read u.user file and insert data
    for row in open("seed_data/u.user"):
        row = row.rstrip()
        user_id, age, gender, occupation, zipcode = row.split("|")

        user = User(user_id=user_id,
                    age=age,
                    zipcode=zipcode)

        # We need to add to the session or it won't ever be stored
        db.session.add(user)

    # Once we're done, we should commit our work
    db.session.commit()


def load_movies():
    """Load movies from u.item into database."""

    print "Movies"

    # Delete all rows in table, so if we need to run this a second time,
    # we won't be trying to add duplicate users
    Movie.query.delete()

    # Read u.item file and insert data. Rather than unpack the whole list,
    # assign elements by index, so we don't have to worry about genres.
    for row in open("seed_data/u.item"):
        row = row.rstrip()
        fields = row.split("|")

        movie_id = fields[0]

        # Slice up to index -7, to leave off year and trailing space
        title = fields[1][:-7]
        # title = title.decode("latin-1")

        # First store the date as a string.
        released_str = fields[2]

        # If there was actually a date for this movie, parse it with datetime.
        if released_str:
            released_at = datetime.strptime(released_str, "%d-%b-%Y")
        else:
            released_at = None

        imdb_url = fields[4]

        # Create an instance of the Movie object
        movie = Movie(movie_id=movie_id,
                      title=title,
                      released_at=released_at,
                      imdb_url=imdb_url)

        # Add the movie to the database.
        db.session.add(movie)

    # Commit all additions
    db.session.commit()


def load_ratings():
    """Load ratings from u.data into database."""

    print "Ratings"

    Rating.query.delete()

    for row in open("seed_data/u.data"):
        row = row.rstrip()

        # We need four vars to unpack into, even though we don't care about 
        # timestamp.
        user_id, movie_id, score, timestamp = row.split("\t")
        
        # Strings don't have to be converted into integers in Python if their
        # SQL data type is Integer.
        rating = Rating(user_id=user_id,
                        movie_id=movie_id,
                        score=score)

        db.session.add(rating)

    db.session.commit()


def set_val_user_id():
    """Set value for the next user_id after seeding database"""

    # Get the Max user_id in the database
    result = db.session.query(func.max(User.user_id)).one()
    max_id = int(result[0])

    # Set the value for the next user_id to be max_id + 1
    query = "SELECT setval('users_user_id_seq', :new_id)"
    db.session.execute(query, {'new_id': max_id + 1})
    db.session.commit()


if __name__ == "__main__":
    connect_to_db(app)

    # In case tables haven't been created, create them
    db.create_all()

    # Import different types of data
    load_users()
    load_movies()
    load_ratings()
    set_val_user_id()
