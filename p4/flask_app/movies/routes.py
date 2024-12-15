import base64,io
from io import BytesIO
from flask import Blueprint, render_template, url_for, redirect, request, flash
from flask_login import current_user

from .. import movie_client
from ..forms import MovieReviewForm, SearchForm, MovieRatingForm
from ..models import User, Review, Rating
from ..utils import current_time

movies = Blueprint("movies", __name__)
""" ************ Helper for pictures uses username to get their profile picture************ """
def get_b64_img(username):
    user = User.objects(username=username).first()
    bytes_im = io.BytesIO(user.profile_pic.read())
    image = base64.b64encode(bytes_im.getvalue()).decode()
    return image

""" ************ View functions ************ """


@movies.route("/", methods=["GET", "POST"])
def index():
    form = SearchForm()

    if form.validate_on_submit():
        return redirect(url_for("movies.query_results", query=form.search_query.data))

    return render_template("index.html", form=form)


@movies.route("/search-results/<query>", methods=["GET"])
def query_results(query):
    try:
        results = movie_client.search(query)
    except ValueError as e:
        return render_template("query.html", error_msg=str(e))

    return render_template("query.html", results=results)


@movies.route("/movies/<movie_id>", methods=["GET", "POST"])
def movie_detail(movie_id):
    try:
        result = movie_client.retrieve_movie_by_id(movie_id)
    except ValueError as e:
        return render_template("movie_detail.html", error_msg=str(e))

    form_review = MovieReviewForm()
    form_rating = MovieRatingForm()
    if form_rating.is_submitted():
        print("HERE")
        rating = Rating(
            rating=form_rating.movieRating.data,
            imdb_id=movie_id,
        )

        rating.save()

        return redirect(request.path)
    
    if form_review.validate_on_submit():
        review = Review(
            commenter=current_user._get_current_object(),
            content=form_review.text.data,
            date=current_time(),
            imdb_id=movie_id,
            movie_title=result.title,
        )

        review.save()

        return redirect(request.path)

    reviews = Review.objects(imdb_id=movie_id)
    ratings = Rating.objects(imdb_id=movie_id)
    avg = 0
    for rating in ratings:
        avg += rating.rating
    if len(ratings) > 0:
        avg = avg/(len(ratings))

    return render_template(
        "movie_detail.html", form_review=form_review, movie=result, reviews=reviews, rating=avg, form_rating=form_rating
    )


@movies.route("/user/<username>")
def user_detail(username):
    #uncomment to get review image
    #user = find first match in db
    user = User.objects(username=username).first()
    if (user == None):
        return render_template("user_detail.html", error="User does not exist!")
    img = get_b64_img(user.username)
    reviews = Review.objects(commenter=user)
    
    return render_template("user_detail.html", username=username, reviews=reviews, image=img)
