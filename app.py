from flask import Flask, render_template, request
from helpers import get_movie, get_more_movies, get_person, get_genre
from helpers import get_letterboxd_rating, get_filmaffinity_rating, get_metacritic_rating

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/search/movie/')
def search_title():
    title = request.args.get('t').strip()
    if not title:
        return 'You must provide a title.'

    year = request.args.get('y')
    if year != '':
        try:
            int(year)
        except ValueError:
            return 'You must provide a valid year.'

    movie, more_results = get_movie(title, year)

    return render_template('movie.html', title=title, year=year, movie=movie, more_results=more_results)


@app.route('/search/person/')
def search_person():
    name = request.args.get('n')
    if not name:
        return 'You must provide a name.'
    result = get_person(query=name)
    return render_template('person.html', search_result=result, query=name, info='')


@app.route('/movie/<id>')
def movie(id):
    movie, more_results = get_movie(tmdb_id=id)
    return render_template('movie.html', title='', year='', id=id, movie=movie, more_results=more_results)


@app.route('/person/<id>')
def person(id):
    info, jobs = get_person(id)
    return render_template('person.html', info=info, jobs=jobs)


@app.route('/genre/<id>/<name>')
def genre(id, name):
    movies = get_genre(id, name)
    return render_template('genre.html', movies=movies)


@app.route('/rotten-tomatoes-rating/')
def rotten_tomatoes_rating():
    title = request.args.get('t')
    year = request.args.get('y')
    rating, url = get_rotten_tomatoes_rating(title, year)
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
    rating, url = get_filmaffinity_rating(title, original_title, year)
    return {'rating': rating, 'url': url}


@app.route('/more-movie-results/')
def more_results():
    title = request.args.get('t')
    year = request.args.get('y')
    id = request.args.get('id')
    page = int(request.args.get('p'))
    return get_more_movies(title, year, id, page)


@app.route('/more-person-results/<query>/<page>')
def more_person_results(query, page):
    return get_person(query=query, page=page)


@app.route('/more-genre-results/<id>/<page>')
def more_genre_results(id, page):
    return get_genre(id, page=page)
