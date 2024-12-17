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
spotify_client = None

albums = Blueprint("albums", __name__)
""" ************ Helper for pictures uses username to get their profile picture************ """
def get_b64_img(username):
    user = User.objects(username=username).first()
    bytes_im = io.BytesIO(user.profile_pic.read())
    image = base64.b64encode(bytes_im.getvalue()).decode()
    return image

""" ************ View functions ************ """

@albums.route('/callback')
def callback():
    if request.args.get('error') == 'access_denied':
        auth_url = sp_oauth.get_authorize_url()
        return render_template('403.html', auth_url=auth_url)
    
    global spotify_client
    sp_oauth.get_access_token(request.args['code'])
    spotify_client = SpotifyClient(sp_oauth.get_access_token()['access_token'])
    return redirect(url_for('albums.index'))


@albums.route("/", methods=["GET", "POST"])
def index():
    form = SearchForm()

    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)

    if form.validate_on_submit():
        return redirect(url_for("albums.query_results", query=form.search_query.data))
    
    return render_template("index.html", form=form, name=sp.me()["display_name"], auth_url=sp_oauth.get_authorize_url())


@albums.route("/search-results/<query>", methods=["GET"])
def query_results(query):
    try:
        results = spotify_client.search(query)
    except ValueError as e:
        return render_template("query.html", error_msg=str(e), name=sp.me()["display_name"], auth_url=sp_oauth.get_authorize_url())

    return render_template("query.html", results=results, name=sp.me()["display_name"], auth_url=sp_oauth.get_authorize_url())


@albums.route("/albums/<album_id>", methods=["GET", "POST"])
def album_detail(album_id):
    try:
        result = spotify_client.get_album_details(album_id)
    except ValueError as e:
        return render_template("album_detail.html", error_msg=str(e), name=sp.me()["display_name"], auth_url=sp_oauth.get_authorize_url())

    form_review = MovieReviewForm()
    form_rating = MovieRatingForm()
    if form_rating.validate_on_submit():
        print("HERE")
        rating = Rating(
            rating=form_rating.movieRating.data,
            imdb_id=album_id,
            commenter=current_user._get_current_object(),
            date=current_time(),
        )

        rating.save()

        return redirect(request.path)
    
    if form_review.validate_on_submit():
        review = Review(
            commenter=current_user._get_current_object(),
            content=form_review.text.data,
            date=current_time(),
            imdb_id=album_id,
            movie_title=result['name'],
        )

        review.save()

        return redirect(request.path)

    reviews = Review.objects(imdb_id=album_id)
    ratings = Rating.objects(imdb_id=album_id)
    avg = 0
    for rating in ratings:
        avg += rating.rating
    if len(ratings) > 0:
        avg = avg/(len(ratings))
    print(avg)
    return render_template(
        "album_detail.html", form_review=form_review, album=result, reviews=reviews, rating=avg, form_rating=form_rating, ratings = ratings, 
        name=sp.me()["display_name"], auth_url=sp_oauth.get_authorize_url()
    )
