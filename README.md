# Movie Ratings

[Movie Ratings](https://movie-ratings.vercel.app) is a web application for searching movies and their ratings from [IMDb](https://www.imdb.com/), [Rotten Tomatoes](https://www.rottentomatoes.com/), [Metacritic](https://www.metacritic.com/), [Letterboxd](https://letterboxd.com/), [TMDb](https://www.themoviedb.org/) and [FilmAffinity](http://www.filmaffinity.com/).

## Project overview

Inside the project's root folder we find `app.py` and `helpers.py`.

- `app.py` contains the routes by which the user will access the different pages of the site and the ones that `movie.js` uses to fetch data.

- `helpers.py` takes care of all things data related. It uses three different APIs to get movie data and ratings from TMDb, IMDb, Rotten Tomatoes and Metacritic. It scrapes the web to get data from FilmAffinity. It also scrapes RottenTomatoe's and Metacritic's websites in case no data is provided by the APIs.

Inside `/templates` are the HTML files.

- `layout.html` is used by all the pages in the site. It contains the nav bar and the search form.

- `index.html` is the home page. It shows `layout.html`'s nav bar and search form, and error messages when the search button is clicked but no input is provided.

- `movie.html` shows information and ratings of a single movie, as well as search results for a _movie search_.

- `person.html` shows either search results of a _person search_ or a person's profile listing all the movies in which she or he participated.

- `genre.html` lists movies of a specific genre. This page can only be accesed by clicking on a genre in a movie's page.

In `/static` we have the JavaScript and CSS files.

- `styles.css` is used across the entire site to style the different components and the overall layout.

- `movie.js` is used by `movie.html`. It gets and displays ratings from Letterboxd and FilmAffinity, and from Rotten Tomatoes and Metacritic if needed. It also shows the movie's average rating based on the checked ratings. Finally, it takes care of loading more movie results when the `Load more` link is clicked.

- `person.js` collapses the different lists of a person's profile and expands them when they're clicked. It also loads more results when a name is searched and `Load more` is clicked.

- `search.js` is used by all the site's pages. It shows the user a search bar with to options: _movie_ and _person_. Under the hood there are two forms, one for each option; `search.js` shows the selected one and hides the other.

- `genre.js` is used by `genre.html` and just loads more results when `Load more` is clicked.
