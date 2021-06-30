from flask import Flask, render_template, request
from helpers import get_movie, get_more_movies, get_person, get_genre
from helpers import get_rottentomatoes_rating, get_letterboxd_rating, get_filmaffinity_rating, get_metacritic_rating

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/search/movie/')
def search_title():
    title = request.args.get('t').strip()
    if not title:
        return render_template('index.html', error='You must provide a title.')

    year = request.args.get('y')
    if year != '':
        try:
            int(year)
        except ValueError:
            return render_template('index.html', error='You must provide a valid year.')

    movie, more_results = get_movie(title, year)

    return render_template('movie.html', title=title, year=year, movie=movie, more_results=more_results)


@app.route('/search/person/')
def search_person():
    name = request.args.get('n')
    if not name:
        return render_template('index.html', error='You must provide a name.')
    result = get_person(query=name)
    return render_template('person.html', search_result=result, query=name, info='')


@app.route('/movie/<movie_id>')
def movie(movie_id):
    movie, more_results = get_movie(tmdb_id=movie_id)
    return render_template('movie.html', title='', year='', id=movie_id, movie=movie, more_results=more_results)


@app.route('/person/<person_id>')
def person(person_id):
    info, jobs = get_person(person_id)
    return render_template('person.html', info=info, jobs=jobs)


@app.route('/genre/<genre_id>/<name>')
def genre(genre_id, name):
    movies = get_genre(genre_id, name)
    return render_template('genre.html', movies=movies)


@app.route('/rotten-tomatoes-rating/')
def rotten_tomatoes_rating():
    title = request.args.get('t')
    year = request.args.get('y')
    rating, url = get_rottentomatoes_rating(title, year)
    return {'rating': rating, 'url': url}


@app.route('/metacritic-rating/')
def metacritic_rating():
    title = request.args.get('t')
    year = request.args.get('y')
    rating, url = get_metacritic_rating(title, year)
    return {'rating': rating, 'url': url}


@app.route('/letterboxd-rating/')
def letterboxd_rating():
    tmdb_id = request.args.get('id')
    title = request.args.get('t')
    year = request.args.get('y')
    rating, url = get_letterboxd_rating(tmdb_id, title, year)
    return {'rating': rating, 'url': url}


@app.route('/filmaffinity-rating/')
def filmaffinity_rating():
    title = request.args.get('t')
    original_title = request.args.get('ot')
    year = request.args.get('y')
    alternative_titles = request.args.get('at')
    rating, url = get_filmaffinity_rating(
        title, original_title, alternative_titles, year)
    return {'rating': rating, 'url': url}


@app.route('/more-movie-results/')
def more_results():
    title = request.args.get('t')
    year = request.args.get('y')
    movie_id = request.args.get('id')
    page = int(request.args.get('p'))
    return get_more_movies(title, year, movie_id, page)


@app.route('/more-person-results/<query>/<page>')
def more_person_results(query, page):
    return get_person(query=query, page=page)


@app.route('/more-genre-results/<genre_id>/<page>')
def more_genre_results(genre_id, page):
    return get_genre(genre_id, page=page)
