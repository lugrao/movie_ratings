import os
import re
import requests
import tmdbsimple as tmdb
from bs4 import BeautifulSoup

TMDB_KEY = os.environ.get("TMDB_KEY")
OMDB_KEY = os.environ.get("OMDB_KEY")


def get_movie(title="", year="", tmdb_id="", imdb_id=""):
    tmdb.API_KEY = TMDB_KEY

    movie_id = tmdb_id
    if not movie_id:
        search = tmdb.Search()
        res = search.movie(query=title, year=year, page=1)

        try:
            movie_id = res["results"][0]["id"]
        except Exception:
            return None, None

    movie_result = tmdb.Movies(movie_id)
    movie = movie_result.info()
    movie_credits = movie_result.credits()
    omdb = get_omdb_data(movie["imdb_id"])

    year = f'{movie["release_date"][:4]}' if movie["release_date"] else ""

    direction = [
        {"name": i["name"], "job": i["job"], "id": i["id"]}
        for i in movie_credits["crew"]
        if i["job"] == "Director"
    ]
    if not direction:
        direction = omdb["direction"]

    writing = [
        {"name": i["name"], "job": i["job"], "id": i["id"]}
        for i in movie_credits["crew"]
        if i["department"] == "Writing"
    ]
    if not writing:
        writing = omdb["writing"]

    actors = [{"name": i["name"], "id": i["id"]} for i in movie_credits["cast"][:6]]
    if not actors:
        actors = omdb["actors"]

    genres = [{"name": i["name"], "id": i["id"]} for i in movie["genres"]]
    if not genres:
        genres = omdb["genres"]

    imdb_url = (
        f'https://www.imdb.com/find?ref_=nv_sr_sm&q={movie["title"]}'
        f' {movie["release_date"][:4]}'
    )

    if movie["imdb_id"]:
        imdb_url = "https://www.imdb.com/title/" + movie["imdb_id"]

    movie_data = {
        "title": movie["title"],
        "original_title": movie["original_title"],
        "alternative_titles": [
            i["title"]
            for i in movie_result.alternative_titles()["titles"]
            if i["iso_3166_1"] in ["GB", "US"]
        ],
        "year": year,
        "runtime": f'{movie["runtime"]} mins' if movie["runtime"] else "",
        "overview": movie["overview"],
        "direction": direction,
        "writing": writing,
        "actors": actors,
        "genres": genres,
        "poster_path": movie["poster_path"],
        "imdb-id": movie["imdb_id"],
        "imdb-rating": omdb["imdb_rating"],
        "imdb-url": imdb_url,
        "rotten-tomatoes-rating": omdb["rotten_tomatoes_rating"],
        "rotten-tomatoes-url": (
            f'https://www.rottentomatoes.com/search?search={movie["title"]}'
        ),
        "metacritic-rating": omdb["metacritic_rating"],
        "metacritic-url": (
            f'https://www.metacritic.com/search/movie/{movie["title"]}/results'
        ),
        "tmdb-id": movie_id,
        "tmdb-rating": (
            [str(movie["vote_average"]) + "/10", float(movie["vote_average"])]
            if movie["vote_count"] > 0
            else ["Not found", -1]
        ),
        "tmdb-url": f'https://www.themoviedb.org/movie/{movie["id"]}',
    }

    more_results = {"movies": [], "total_pages": 1}

    if tmdb_id:
        more_movies = movie_result.similar_movies()
    else:
        more_movies = res

    more_results["total_pages"] = more_movies["total_pages"]
    for i in more_movies["results"]:
        try:
            year = f'({i["release_date"][:4]})' if i["release_date"] else ""
            more_results["movies"].append(
                {"title": i["title"], "year": year, "tmdb-id": i["id"]}
            )
        except KeyError:
            more_results["movies"].append(
                {"title": i["title"], "year": "", "tmdb-id": i["id"]}
            )

    return movie_data, more_results


def get_more_movies(title="", year="", tmdb_id="", page=2):
    tmdb.API_KEY = TMDB_KEY

    movie_id = tmdb_id
    if not movie_id:
        search = tmdb.Search()
        res = search.movie(query=title, year=year, page=page)
        movie_id = res["results"][0]["id"]

    movie_result = tmdb.Movies(movie_id)

    if tmdb_id:
        # Show similar movies when movie ID es provided
        more_movies = movie_result.similar_movies(page=page)
    else:
        # Show more results from user's query
        more_movies = res

    results = {"movies": [], "total_pages": more_movies["total_pages"]}
    for i in more_movies["results"]:
        try:
            year = f'({i["release_date"][:4]})' if i["release_date"] else ""
            results["movies"].append(
                {"title": i["title"], "year": year, "tmdb-id": i["id"]}
            )
        except KeyError:
            results["movies"].append(
                {"title": i["title"], "year": "", "tmdb-id": i["id"]}
            )

    return results


def get_omdb_data(imdb_id):

    try:
        url = f"http://www.omdbapi.com/?apikey={OMDB_KEY}&i={imdb_id}"
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        return None

    movie = response.json()

    try:
        direction = movie["Director"]
    except Exception:
        direction = "N/A"

    try:
        writing = movie["Writer"]
    except Exception:
        writing = "N/A"

    try:
        actors = movie["Actors"]
    except Exception:
        actors = "N/A"

    try:
        genres = movie["Genre"]
    except Exception:
        genres = "N/A"

    try:
        imdb = movie["Ratings"][0]["Value"]
        imdb = [imdb, float(imdb.split("/")[0])]
    except (IndexError, ValueError, KeyError):
        imdb = ["Not found", -1]

    try:
        rotten_tomatoes = movie["Ratings"][1]["Value"]
        rotten_tomatoes = [rotten_tomatoes, float(rotten_tomatoes[:-1]) / 10]
    except (IndexError, ValueError, KeyError):
        rotten_tomatoes = ["Not found", -1]

    try:
        metacritic = movie["Ratings"][2]["Value"]
        metacritic = [metacritic, float(metacritic.split("/")[0]) / 10]
    except (IndexError, ValueError, KeyError):
        metacritic = ["Not found", -1]

    try:
        poster = movie["Poster"]
    except Exception:
        poster = ""

    return {
        "direction": direction,
        "writing": writing,
        "actors": actors,
        "genres": genres,
        "imdb_rating": imdb,
        "rotten_tomatoes_rating": rotten_tomatoes,
        "metacritic_rating": metacritic,
        "poster_url": poster,
    }


def get_person(person_id="", query="", page=1):
    tmdb.API_KEY = TMDB_KEY

    if person_id:
        person = tmdb.People(person_id)
        crew_data = person.movie_credits()["crew"]
        cast_data = person.movie_credits()["cast"]
        jobs = {}

        for movie in crew_data:
            if movie["job"] not in jobs:
                jobs[movie["job"]] = []

            year = ""
            try:
                if movie["release_date"]:
                    year = f'({movie["release_date"][:4]})'
            except Exception:
                pass

            jobs[movie["job"]].append(
                {"title": movie["title"], "year": year, "id": movie["id"]}
            )

        if cast_data:
            jobs["Actor"] = []

            for movie in cast_data:
                year = ""
                try:
                    if movie["release_date"]:
                        year = f'({movie["release_date"][:4]})'
                except Exception:
                    pass

                jobs["Actor"].append(
                    {"title": movie["title"], "year": year, "id": movie["id"]}
                )

        return person.info(), jobs

    search = tmdb.Search()
    result = search.person(query=query, page=page)

    # Remove tv shows from 'known_for' list
    for person in result["results"]:
        person["known_for"][:] = [
            x for x in person["known_for"] if x["media_type"] == "movie"
        ]

    return result


def get_genre(genre_id, name="", page=1):
    tmdb.API_KEY = TMDB_KEY
    genre = tmdb.Genres(genre_id)
    genre_movies = genre.movies(page=page, include_all_movies=True)
    movies = []
    name = " ".join(name.split("%20"))

    for movie in genre_movies["results"]:
        year = ""
        try:
            if movie["release_date"]:
                year = f'({movie["release_date"][:4]})'
        except Exception:
            pass

        movies.append(
            {
                "title": movie["title"],
                "year": year,
                "poster_path": movie["poster_path"],
                "id": movie["id"],
            }
        )

    movies_data = {
        "genre": {"name": name, "id": genre_id},
        "movies": movies,
        "total_pages": genre_movies["total_pages"],
    }

    return movies_data


def get_letterboxd_rating(tmdb_id, title="", year=""):
    movie_url = None

    try:
        search_res = requests.get(f"https://letterboxd.com/tmdb/{tmdb_id}")
        search_soup = BeautifulSoup(search_res.text, "html.parser")
        movie_url = search_soup.find_all(attrs={"name": "twitter:url"})[0]["content"]
        movie_rating = round(
            float(
                search_soup.find_all(attrs={"name": "twitter:data2"})[0][
                    "content"
                ].split()[0]
            ),
            1,
        )

        return [str(movie_rating) + "/5", movie_rating * 2], movie_url
    except Exception:
        url = f"https://letterboxd.com/search/{title} {year}"
        if movie_url:
            url = movie_url
        return ["Not found", -1], url


def get_rottentomatoes_rating(title, year):
    rating = ["Not found", -1]
    movie_url = f"https://www.rottentomatoes.com/search?search={title}"

    if not year:
        return rating, movie_url

    try:
        res = requests.get(movie_url)
        soup = BeautifulSoup(res.text, "html.parser")
        movies = soup.find_all(type="movie")[0].find_all("search-page-media-row")
    except Exception as e:
        print(e)
        return rating, movie_url

    for movie in movies:
        movie_name = movie.find_all("a")[-1].text.strip()
        url = movie.a["href"]
        movie_score = movie.attrs["tomatometerscore"]
        release_year = movie.attrs["releaseyear"]

        if movie_name == title and release_year == year:
            rating = [f"{movie_score}%", float(movie_score) / 10]
            movie_url = url
            break

    return rating, movie_url


def get_metacritic_rating(title, year):
    url = f"https://www.metacritic.com/search/{title}/"
    rating = None
    movie_url = None
    user_agent = (
        "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.37"
    )

    if not year:
        return ["Not found", -1], url

    try:
        res = requests.get(url, headers={"User-Agent": user_agent})
        soup = BeautifulSoup(res.text, "html.parser")
        movies = soup.find_all(
            "a",
            class_=lambda css_class: css_class is not None
            and css_class in "c-pageSiteSearch-results-item",
        )
    except Exception as e:
        print(e)
        return ["Not found", -1], url

    for movie in movies:
        t = movie.find("p").text.strip().lower()
        y = movie.find_all("span")[2].text.strip()
        is_movie = "movie" == movie.find_all("span")[0].text.strip().lower()

        if t == title.lower() and y == year and is_movie:
            rating = movie.find_all("span")[-1].text.strip()
            movie_url = f"https://www.metacritic.com{movie['href']}"
            break

    try:
        return [f"{rating}/100", float(rating) / 10], movie_url
    except Exception as e:
        print(e)
        return ["Not found", -1], url


def get_filmaffinity_rating(title, original_title, alternative_titles, year):
    def clean(title):
        title = title.lower().replace("the", "").strip()
        title = re.sub(r"[\(\[].*?[\)\]]|[^a-z0-9]", "", title)
        return title

    url = f"https://www.filmaffinity.com/en/search.php?stype=title&stext={title}"
    rating = None
    movie_url = None
    title = clean(title)
    original_title = clean(original_title)
    try:
        res = requests.get(url)
        soup = BeautifulSoup(res.text, "html.parser")
    except Exception:
        return ["Not found", -1], url

    results = soup.find_all("div", class_="se-it mt")

    if results:
        try:
            for movie in results:
                t = movie.find_all("a")[1].get("title").strip()
                y = movie.find("div", class_="ye-w").text
                titles = [title, original_title]

                if (clean(t) in titles or t in alternative_titles) and y == year:
                    rating = movie.find("div", class_="avgrat-box").text
                    movie_url = movie.a.get("href")
                    break
        except Exception:
            pass
    else:
        try:
            t = soup.find_all("h1", {"id": "main-title"})[0].text
            ot = clean(soup.find_all("dl", class_="movie-info")[0].dd.contents[0])
            y = soup.find_all("dd", {"itemprop": "datePublished"})[0].text
            titles = [clean(t), ot]
            try:
                akas = soup.find_all("dd", class_="akas")[0].ul.find_all("li")
                for i in akas:
                    titles.append(clean(i.text))
            except Exception:
                pass

            if year == y and (
                title in titles or original_title in titles or t in alternative_titles
            ):
                rating = soup.find_all("div", {"id": "movie-rat-avg"})[0].text.strip()
                movie_url = soup.find_all("link", {"rel": "canonical"})[0].get("href")
        except Exception:
            pass

    try:
        return [f"{rating}/10", float(rating)], movie_url
    except Exception:
        return ["Not found", -1], url
