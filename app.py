from flask import Flask, render_template, request
from helpers import get_movie, get_letterboxd_rating, get_more_movies, get_person, get_genre

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/search')
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


@app.route('/movie/<id>/')
def movie(id):
    movie, more_results = get_movie(tmdb_id=id)
    return render_template('movie.html', title='', year='', id=id, movie=movie, more_results=more_results)


@app.route('/person/<id>/')
def person(id):
    info, jobs = get_person(id)
    return render_template('person.html', info=info, jobs=jobs)

@app.route('/genre/<id>/<name>')
def genre(id, name):
    movies = get_genre(id, name)
    return render_template('genre.html', movies=movies)


@app.route('/letterboxd-rating')
def letterboxd_rating():
    imdb_id = request.args.get('id')
    title = request.args.get('t')
    year = request.args.get('y')
    rating, url = get_letterboxd_rating(imdb_id, title, year)
    response = {'rating': rating, 'url': url}
    return response


@app.route('/more-results')
def more_results():
    title = request.args.get('t')
    year = request.args.get('y')
    id = request.args.get('id')
    page = int(request.args.get('p'))
    more_results = get_more_movies(title, year, id, page)
    return more_results

@app.route('/more-genre-results/<id>/<page>')
def more_genre_results(id, page):
    response = get_genre(id, page=page)
    return response
