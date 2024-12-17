import requests


class Movie(object):
    def __init__(self, omdb_json, detailed=False):
        if detailed:
            self.genres = omdb_json["Genre"]
            self.director = omdb_json["Director"]
            self.actors = omdb_json["Actors"]
            self.plot = omdb_json["Plot"]
            self.awards = omdb_json["Awards"]

        self.title = omdb_json["Title"]
        self.year = omdb_json["Year"]
        self.imdb_id = omdb_json["imdbID"]
        self.type = "Movie"
        self.poster_url = omdb_json["Poster"]

    def __repr__(self):
        return self.title

class SpotifyClient(object):
     def __init__(self, api_key):
        self.sess = requests.Session()
        self.base_url = 'https://api.spotify.com/v1/search'
        self.headers = { 'Authorization': f"Bearer {api_key}" }

     def get_current_user(self):
        user = self.sess.get('https://api.spotify.com/v1/me', headers=self.headers)
        user = user.json()["display_name"]
        return user
    
     def search(self, search_string):
        params = { 'q': search_string, 'type': 'album', 'limit': '30' }
        search_results = self.sess.get(self.base_url, headers=self.headers, params=params)
        search_results = search_results.json()

        albums = list(map(lambda x: {
            'id': x["id"],
            'name': x["name"],
            'image': x["images"][0],
            'release_date': x["release_date"]
        }, search_results["albums"]["items"]))

        return albums
     
     def get_album_details(self, id):
         params = { 'market': 'US' }
         album = self.sess.get(f'https://api.spotify.com/v1/albums/{id}', headers=self.headers, params=params)
         album = album.json()
         album_object = {
             "id": album["id"],
             "artist_name": album["artists"][0]["name"],
             "name": album["name"],
             "total_tracks": album["total_tracks"],
             "image": album["images"][0],
             "release_date": album["release_date"],
             "url": album["external_urls"]["spotify"],
             "popularity": album["popularity"],
         }
         return album_object


class MovieClient(object):
    def __init__(self, api_key):
        self.sess = requests.Session()
        self.base_url = f"http://www.omdbapi.com/?apikey={api_key}&r=json&type=movie&"

    def search(self, search_string):
        """
        Searches the API for the supplied search_string, and returns
        a list of Media objects if the search was successful, or the error response
        if the search failed.

        Only use this method if the user is using the search bar on the website.
        """
        search_string = "+".join(search_string.split())
        page = 1

        search_url = f"s={search_string}&page={page}"

        resp = self.sess.get(self.base_url + search_url)

        if resp.status_code != 200:
            raise ValueError(
                "Search request failed; make sure your API key is correct and authorized"
            )

        data = resp.json()

        if data["Response"] == "False":
            raise ValueError(f'[ERROR]: Error retrieving results: \'{data["Error"]}\' ')

        search_results_json = data["Search"]
        remaining_results = int(data["totalResults"])

        result = []

        ## We may have more results than are first displayed
        while remaining_results != 0:
            for item_json in search_results_json:
                result.append(Movie(item_json))
                remaining_results -= len(search_results_json)
            page += 1
            search_url = f"s={search_string}&page={page}"
            resp = self.sess.get(self.base_url + search_url)
            if resp.status_code != 200 or resp.json()["Response"] == "False":
                break
            search_results_json = resp.json()["Search"]

        return result

    def retrieve_movie_by_id(self, imdb_id):
        """
        Use to obtain a Movie object representing the movie identified by
        the supplied imdb_id
        """
        movie_url = self.base_url + f"i={imdb_id}&plot=full"

        resp = self.sess.get(movie_url)

        if resp.status_code != 200:
            raise ValueError(
                "Search request failed; make sure your API key is correct and authorized"
            )

        data = resp.json()

        if data["Response"] == "False":
            raise ValueError(f'[ERROR]: Error retrieving results: \'{data["Error"]}\' ')

        movie = Movie(data, detailed=True)

        return movie


## -- Example usage -- ###
if __name__ == "__main__":
    import os

    client = MovieClient(os.environ.get("OMDB_API_KEY"))

    movies = client.search("guardians")

    for movie in movies:
        print(movie)

    print(len(movies))
