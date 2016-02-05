"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session, get_flashed_messages

from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, Rating, Movie

from collections import Counter



app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    return render_template("homepage.html")

@app.route("/users")
def user_list():
    """Show list of users"""

    users = User.query.all()
    return render_template("user_list.html", users=users)

@app.route("/signup")
def sign_up_form():
    """Show and submit sign up form"""

    return render_template("sign_up_form.html")

@app.route("/login")
def login_form():
    """Show and submit login form"""

    return render_template("login_form.html")


@app.route("/login-verification", methods=["POST"])
def check_for_email_password_match():
    """Check if email and password match"""

    email = request.form.get("email")
    password = request.form.get("password")

    user_with_match = db.session.query(User).filter((User.email == email) 
        & (User.password == password)).first()

    if not user_with_match:
        flash("Information you provided does not match our records. Please try again.")
        return redirect ("/") 
    else:
        user_id = user_with_match.user_id
        session['user'] = user_id
        flash("You have been successfully logged in.")
        return redirect("/users/" + str(user_id))

@app.route("/users/<int:user_id>")
def show_user_info(user_id):
    """Show information about the user"""

    user = db.session.query(User).get(user_id)
    age = user.age
    zipcode = user.zipcode
   
    all_ratings = user.ratings

    all_scores = []

    all_titles = []

    for rating in all_ratings:
        score = rating.score
        all_scores.append(score)
        movie_id = rating.movie_id
        movie = db.session.query(Movie).get(movie_id)
        title = movie.title
        all_titles.append(title)

    zipped = zip(all_titles, all_scores) 

    return render_template("user_profile.html",
                            age=age,
                            zipcode=zipcode,
                            zipped = zipped)


@app.route("/processing-form", methods=["POST"])
def check_for_user():
    """Check if user exists. If not, add new user to database."""

    email = request.form.get("email")
    password = request.form.get("password")

    users_with_email = db.session.query(User).filter(User.email == email).all()

    if len(users_with_email) == 0:
        user=User(email=email, password=password)
        db.session.add(user)
        db.session.commit()
        flash("Great success!!!!!!!!")
        return render_template('homepage.html')
    else:
        flash("""User with this email address already exists. 
            Please register with a different email address.""")
        return redirect("/")

@app.route("/logout")
def logout():
    """Logs out user"""

    session['user'] = None
    flash("Logged out!")
    return redirect ("/")

@app.route("/movies")
def show_movie_list():
    """Shows a list of all movies"""

    movies = Movie.query.all()

    return render_template("movie_list.html", movies=movies)

@app.route("/movies/<int:movie_id>")
def show_movie_details(movie_id):
    """Show movie details"""

    movie = db.session.query(Movie).get(movie_id)

    title = movie.title
    released_at = movie.released_at
    imdb_url = movie.imdb_url

    # movie_ratings = movie.ratings.group_by(Rating.score).count()
    # movie_ratings = db.session.query(Rating.score).filter_by(movie_id = movie.movie_id).group_by(Rating.score)

    movie_ratings = db.session.query(Rating.score).filter_by(movie_id = movie.movie_id).all()

    # scores = []

    # for score in movie_ratings:
    #     score = tuple[0]
    #     scores.append(score)




    return render_template("movie_details.html",
                            title=title,
                            released_at=released_at,
                            imdb_url=imdb_url,
                            movie_ratings=movie_ratings)


@app.route("/processing-user-score")
def processing_user_score():
    """Records new rating or updates existing rating"""

    user_score = request.args.get("score")

    #for user_id and movie_id 
    # if score is Null create new rating in db +flash "u ranked the movie!"
    # else: update score in db + flash
    # add to db
    # commit

    rating_in_db = db.session.query(Rating.score).filter((Rating.movie_id == movie_id) &
        (Rating.user_id == user_id)).first()

    if not rating_in_db:
        flash("Yay you've rated this movie!")
        rating_in_db = Rating(user_id=user_id, movie_id=movie_id, user_score=score)
        db.session.add(rating_in_db)  
    else:
        flash("We've updated your score for this movie!")
        rating_in_db.score = int(user_score)

    db.session.commit()

    return redirect("/movies" + str(movie_id))


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()
