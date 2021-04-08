from flask import Flask, render_template, request
from helpers import get_movie, get_movies, get_letterboxd_rating

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/search/title')
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

    movie = get_movie(title, year)
    movies, total_results = get_movies(title)

    return render_template('movie.html', title=title, movie=movie, movies=movies, total_results=total_results)


@app.route('/search/imdb-id')
def search_imdb_id():

    imdb_id = request.args.get('id').strip()
    if not imdb_id:
        return 'Yo must provide a valid IMDb ID.'

    movie = get_movie(imdb_id=imdb_id)
    if not movie:
        return render_template('movie.html')

    title = movie['title']

    return render_template('movie.html', title=title, movie=movie, movies='1')


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
    page = int(request.args.get('p'))
    movies, total_results = get_movies(title, page)
    response = {'movies': movies, 'total_results': total_results}
    return response
