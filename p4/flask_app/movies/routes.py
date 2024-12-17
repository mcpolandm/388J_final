import os, requests
from requests import get
import base64,io
from io import BytesIO
from flask import Flask, Blueprint, json, render_template, url_for, redirect, request, flash, session
from flask_login import current_user

from .. import movie_client
from ..forms import MovieReviewForm, SearchForm, MovieRatingForm
from ..models import User, Review, Rating
from ..utils import current_time

from spotipy import Spotify
from spotipy import SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler

from ..client import SpotifyClient

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)

client_id = '5817050472aa40e488cfe5e5d80dd6be'
client_secret = 'a6327884a1fd428683b2e5ec2ebfa3d8'
redirect_uri = 'http://localhost:5000/callback'
scope = 'playlist-read-private'

cache_handler = FlaskSessionCacheHandler(session)
sp_oauth = SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope=scope,
    cache_handler=cache_handler,
    show_dialog=True
)
sp = Spotify(auth_manager=sp_oauth)
spotify_client: SpotifyClient

movies = Blueprint("movies", __name__)
""" ************ Helper for pictures uses username to get their profile picture************ """
def get_b64_img(username):
    user = User.objects(username=username).first()
    bytes_im = io.BytesIO(user.profile_pic.read())
    image = base64.b64encode(bytes_im.getvalue()).decode()
    return image

""" ************ View functions ************ """

@movies.route('/callback')
def callback():
    sp_oauth.get_access_token(request.args['code'])
    return redirect(url_for('movies.index'))


@movies.route("/", methods=["GET", "POST"])
def index():
    form = SearchForm()

    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)

    if form.validate_on_submit():
        return redirect(url_for("movies.query_results", query=form.search_query.data))

    return render_template("index.html", form=form)


@movies.route("/search-results/<query>", methods=["GET"])
def query_results(query):
    spotify_client = SpotifyClient(sp_oauth.get_access_token()['access_token'])
    try:
        results = spotify_client.search(query)
    except ValueError as e:
        return render_template("query.html", error_msg=str(e))

    return render_template("query.html", results=results)


@movies.route("/movies/<movie_id>", methods=["GET", "POST"])
def movie_detail(movie_id):
    spotify_client = SpotifyClient(sp_oauth.get_access_token()['access_token'])
    try:
        result = spotify_client.get_album_details(movie_id)
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
