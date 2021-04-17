import os
import math
import requests
import tmdbsimple as tmdb
from bs4 import BeautifulSoup


def get_movie(title='', year='', tmdb_id='', imdb_id=''):
    tmdb.API_KEY = os.environ.get('TMDB_KEY')

    id = tmdb_id
    if not id:
        search = tmdb.Search()
        res = search.movie(query=title, year=year, page=1)

        try:
            id = res['results'][0]['id']
        except:
            return None, None

    movie_result = tmdb.Movies(id)
    movie = movie_result.info()
    credits = movie_result.credits()
    omdb = get_omdb_data(movie['imdb_id'])

    direction = [{'name': i['name'], 'job': i['job'], 'id': i['id']}
                 for i in credits['crew'] if i['job'] == 'Director']
    if not direction:
        direction = omdb['direction']

    writing = [{'name': i['name'], 'job': i['job'], 'id': i['id']}
               for i in credits['crew'] if i['department'] == 'Writing']
    if not writing:
        writing = omdb['writing']

    actors = [{'name': i['name'], 'id': i['id']} for i in credits['cast'][:6]]
    if not actors:
        actors = omdb['actors']

    genres = [{'name': i['name'], 'id': i['id']} for i in movie['genres']]
    if not genres:
        genres = omdb['genres']

    imdb_url = f'https://www.imdb.com/find?ref_=nv_sr_sm&q={movie["title"]} {movie["release_date"][:4]}'
    if movie['imdb_id']:
        imdb_url = 'https://www.imdb.com/title/' + movie['imdb_id']

    movie_data = {
        'title': movie['title'],
        'year': f'({movie["release_date"][:4]})' if movie['release_date'] else '',
        'runtime': f'{movie["runtime"]} mins' if movie['runtime'] else '',
        'overview': movie['overview'],
        'direction': direction,
        'writing': writing,
        'actors': actors,
        'genres': genres,
        'poster_path': movie['poster_path'],
        'imdb-id': movie['imdb_id'],
        'imdb-rating': omdb['imdb_rating'],
        'imdb-url': imdb_url,
        'rotten-tomatoes-rating': omdb['rotten_tomatoes_rating'],
        'rotten-tomatoes-url': f'https://www.rottentomatoes.com/search?search={movie["title"]}',
        'metacritic-rating': omdb['metacritic_rating'],
        'metacritic-url': f'https://www.metacritic.com/search/movie/{movie["title"]}/results',
        'tmdb-id': id,
        'tmdb-rating': [str(movie['vote_average']) + '/10', float(movie['vote_average'])],
        'tmdb-url': f'https://www.themoviedb.org/movie/{movie["id"]}'
    }

    more_results = {'movies': [], 'total_pages': 1}

    if tmdb_id:
        more_movies = movie_result.similar_movies()
    else:
        more_movies = res

    more_results['total_pages'] = more_movies['total_pages']
    for i in more_movies['results']:
        try:
            year = f'({i["release_date"][:4]})' if i['release_date'] else ''
            more_results['movies'].append(
                {'title': i['title'], 'year': year, 'tmdb-id': i['id']})
        except KeyError:
            more_results['movies'].append(
                {'title': i['title'], 'year': '', 'tmdb-id': i['id']})

    return movie_data, more_results


def get_more_movies(title='', year='', tmdb_id='', page=2):
    tmdb.API_KEY = os.environ.get('TMDB_KEY')

    id = tmdb_id
    if not id:
        search = tmdb.Search()
        res = search.movie(query=title, year=year, page=page)
        id = res['results'][0]['id']

    movie_result = tmdb.Movies(id)

    if tmdb_id:
        # Show similar movies when movie ID es provided
        more_movies = movie_result.similar_movies(page=page)
    else:
        # Show more results from user's query
        more_movies = res

    results = {
        'movies': [],
        'total_pages': more_movies['total_pages']
    }
    for i in more_movies['results']:
        try:
            year = f'({i["release_date"][:4]})' if i['release_date'] else ''
            results['movies'].append(
                {'title': i['title'], 'year': year, 'tmdb-id': i['id']})
        except KeyError:
            results['movies'].append(
                {'title': i['title'], 'year': '', 'tmdb-id': i['id']})

    return results


def get_omdb_data(imdb_id):
    omdb_key = os.environ.get('OMDB_KEY')

    try:
        url = f'http://www.omdbapi.com/?apikey={omdb_key}&i={imdb_id}'
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        return None

    movie = response.json()

    try:
        direction = movie['Director']
    except:
        direction = 'N/A'

    try:
        writing = movie['Writer']
    except:
        writing = 'N/A'

    try:
        actors = movie['Actors']
    except:
        actors = 'N/A'

    try:
        genres = movie['Genre']
    except:
        genres = 'N/A'

    try:
        imdb = movie['Ratings'][0]['Value']
        imdb = [imdb, float(imdb.split('/')[0])]
    except (IndexError, ValueError, KeyError):
        imdb = ['Not available', -1]

    try:
        rotten_tomatoes = movie['Ratings'][1]['Value']
        rotten_tomatoes = [rotten_tomatoes, float(rotten_tomatoes[:-1]) / 10]
    except (IndexError, ValueError, KeyError):
        rotten_tomatoes = ['Not available', -1]

    try:
        metacritic = movie['Ratings'][2]['Value']
        metacritic = [metacritic, float(metacritic.split('/')[0]) / 10]
    except (IndexError, ValueError, KeyError):
        metacritic = ['Not available', -1]

    try:
        poster = movie['Poster']
    except:
        poster = ''

    return {
        'direction': direction,
        'writing': writing,
        'actors': actors,
        'genres': genres,
        'imdb_rating': imdb,
        'rotten_tomatoes_rating': rotten_tomatoes,
        'metacritic_rating': metacritic,
        'poster_url': poster
    }


def get_letterboxd_rating(tmdb_id, title='', year=''):

    try:
        search_res = requests.get(f'https://letterboxd.com/tmdb/{tmdb_id}')
        search_soup = BeautifulSoup(search_res.text, 'html.parser')
        movie_url = search_soup.find_all(
            attrs={'name': 'twitter:url'})[0]['content']
        movie_rating = round(float(search_soup.find_all(
            attrs={'name': 'twitter:data2'})[0]['content'].split()[0]), 1)

        return [str(movie_rating) + '/5', movie_rating * 2], movie_url
    except:
        url = f'https://letterboxd.com/search/{title} {year}'
        if movie_url:
            url = movie_url
        return ['Not available', -1], url


def get_person(id):
    tmdb.API_KEY = os.environ.get('TMDB_KEY')
    person = tmdb.People(id)
    crew_data = person.movie_credits()['crew']
    cast_data = person.movie_credits()['cast']
    jobs = {}

    for movie in crew_data:

        if movie['job'] not in jobs:
            jobs[movie['job']] = []

        try:
            year = f'({movie["release_date"][:4]})' if movie['release_date'] else ''
        except:
            year = ''

        jobs[movie['job']].append({
            'title': movie['title'],
            'year': year,
            'id': movie['id']
        })

    if cast_data:
        jobs['Actor'] = []
        for movie in cast_data:
            try:
                year = f'({movie["release_date"][:4]})' if movie['release_date'] else ''
            except:
                year = ''

            jobs['Actor'].append({
                'title': movie['title'],
                'year': year,
                'id': movie['id']
            })

    return person.info(), jobs


def get_genre(id, name='', page=1):
    tmdb.API_KEY = os.environ.get('TMDB_KEY')
    genre = tmdb.Genres(id)
    genre_movies = genre.movies(page=page, include_all_movies=True)
    movies = []

    for movie in genre_movies['results']:
        try:
            year = f'({movie["release_date"][:4]})' if movie['release_date'] else ''
        except:
            year = ''

        movies.append({
            'title': movie['title'],
            'year': year,
            'poster_path': movie['poster_path'],
            'id': movie['id']
        })

    movies_data = {
        'genre': {'name': name, 'id': id},
        'movies': movies,
        'total_pages': genre_movies['total_pages']
    }

    return movies_data
