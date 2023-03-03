"""Server for movie ratings app."""

from flask import Flask, render_template, request, flash, session, redirect
from model import connect_to_db, db
import crud
from jinja2 import StrictUndefined

app = Flask(__name__)

app.secret_key = "dev"
app.jinja_env.undefined = StrictUndefined

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/movies")
def all_movies():

    movies = crud.get_movies()
    return render_template("movies.html", movies=movies)


@app.route("/movies/<movie_id>")
def movie_details(movie_id):

    movie = crud.get_movie(movie_id)
    rating = crud.get_rating(movie_id)
    return render_template("movie.html", movie=movie, rating=rating)


@app.route("/users", methods=["GET"])
def all_users():
    if 'user_id' not in session:
        return redirect("/login")

    users = crud.get_users()
    return render_template("users.html", users=users)

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/users", methods=["POST"])
def register_user():
    email = request.form.get("email")
    password  = request.form.get("password")

    user = crud.get_user_by_email(email)

    if user:
        flash("Account already exists.")
    else:
        user = crud.create_user(email, password)
        db.session.add(user)
        db.session.commit()
        flash("Account created! Please log in.")

    return redirect("/")

@app.route("/movies/<movie_id>", methods=["POST"])
def add_rating(movie_id):
    user = crud.get_user(session["user_id"])
    movie = crud.get_movie(movie_id)
    score = request.form.get("score")

    rating = crud.create_rating(user, movie, int(score))
    db.session.add(rating)
    db.session.commit()
    return redirect(f"/movies/{movie_id}")

@app.route("/ratings/<rating_id>", methods=["GET"])
def delete_rating(rating_id):
    rating = crud.get_rating_by_id(rating_id)
    db.session.delete(rating)
    db.session.commit()
    user_id = session['user_id']
    return redirect (f"/users/{user_id}")

@app.route("/rating/<rating_id>", methods=["GET"])
def edit_rating(rating_id):
    rating = crud.get_rating_by_id(rating_id)
    return render_template("rating.html", rating=rating)

@app.route("/upd_rating/<rating_id>", methods=["GET"])
def update_rating(rating_id):
    rating_to_update = crud.get_rating_by_id(rating_id)
    rating_to_update.score = request.form.get("score")
    db.session.add(rating_to_update)
    db.session.commit()
    user_id = session['user_id']
    return redirect (f"/users/{user_id}")


@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("email")
    password  = request.form.get("password")

    user = crud.get_user_by_email(email)

    if not user or user.password != password:
        flash("Invalid username or password")
        return redirect('/login')

    session["user_id"] = user.user_id
    flash("Logged in.")
    return redirect("/")

@app.route("/login", methods=["GET"])
def login_page():
    return render_template("login.html")

@app.route("/logout")
def logout():
    del session["user_id"]
    flash("Logged out!")
    return redirect("/login")

@app.route("/users/<user_id>")
def user_details(user_id):

    user = crud.get_user(user_id)
    rating = crud.get_rating_for_user(user_id)
    return render_template("user.html", user=user, rating=rating)


if __name__ == "__main__":
    connect_to_db(app)
    app.run(host="0.0.0.0", debug=True)
