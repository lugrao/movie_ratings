let storage = window.localStorage;
let current_url = window.location.toString();
let $loadMore = document.getElementById('load-more');
let $moreResultsList = document.getElementById('more-results-list');
let $inputs = document.querySelectorAll('.checkbox div input');
let $averageRating = document.getElementById('average-rating');
let title = null;
let year = null;
let id = null;
let page = 2;

if ($loadMore) {
    title = $loadMore.dataset.title;
    year = $loadMore.dataset.year;
    id = $loadMore.dataset.id;
    $loadMore.addEventListener('click', loadMoreResults);
}

$inputs.forEach(input => {
    input.addEventListener('click', updateRating);
})

updateRating();
getLetterboxdRating();


async function getLetterboxdRating() {
    let $movie = document.getElementById('movie');
    let tmdbID = $movie.dataset.tmdbid;
    let title = $movie.dataset.title;
    let year = $movie.dataset.year;
    let $checkbox = document.getElementsByName('letterboxd-rating')[0];
    let $label = $checkbox.previousElementSibling;
    let url = `/letterboxd-rating?id=${tmdbID}&t=${title}&y=${year}`;
    let response;

    if (!storage.getItem(current_url)) {
        try {
            response = await fetch(url).then(res => res.json()).then(data => data);
            storage.setItem(current_url, JSON.stringify(response));
        } catch (error) {
            $label.style.color = 'black';
            $label.innerHTML = 'Letterboxd rating: <span style="color: crimson;">error</span>.';
            return console.error(error);
        }
    } else {
        response = JSON.parse(storage.getItem(current_url));
    }

    $label.innerHTML = `<a href="${response.url}" target="_blank">Letterboxd</a> rating: ${response.rating[0]}`;
    $label.style.color = 'black';
    $checkbox.dataset.rating = response.rating[1];
    $checkbox.checked = true;
    $checkbox.disabled = false;
    $checkbox.className = 'clickable';

    updateRating();

    if (storage.getItem(current_url)) {
        try {
            response = await fetch(url).then(res => res.json()).then(data => data);
            stored_data = JSON.parse(storage.getItem(current_url));

            if (stored_data.rating[0] != response.rating[0]) {
                storage.setItem(current_url, JSON.stringify(response));
                $label.innerHTML = `<a href="${response.url}" target="_blank">Letterboxd</a> rating: ${response.rating[0]}`;
                $label.style.color = 'black';
                $checkbox.dataset.rating = response.rating[1];
                $checkbox.checked = true;
                $checkbox.disabled = false;
                $checkbox.className = 'clickable';
                updateRating();
            }
        } catch (error) {
            return console.error(error);
        }
    }
}


async function loadMoreResults() {
    let url = `/more-results?t=${title}&y=${year}&id=${id}&p=${page}`;
    let response;
    let $li = document.querySelectorAll('li');
    let scrollItem = $li[$li.length - 1];

    try {
        response = await fetch(url).then(res => res.json()).then(data => data);
    } catch (error) {
        return console.error(error);
    }

    response.movies.forEach(movie => {
        let new_movie = document.createElement('li');
        new_movie.innerHTML = `<a href="/movie/${movie['tmdb-id']}">${movie['title']} ${movie['year']}</a>`;
        $moreResultsList.appendChild(new_movie);
    });

    scrollItem.scrollIntoView();

    page++;

    if (page > response['total_pages']) {
        $loadMore.style.display = 'none';
    }
}


function updateRating() {
    let ratingSum = 0;
    let ratingCount = 0;

    $inputs.forEach(input => {
        if (input.checked == true && input.dataset.rating != '-1') {
            ratingSum += Number(input.dataset.rating);
            ratingCount++;
        }
        else if (input.dataset.rating == '-1') {
            input.disabled = true;
            input.className = '';
            input.checked = false;

            let label = input.previousElementSibling;
            label.style.color = 'grey';
            if (label.innerText.includes('loading')) {
                label.style.color = 'black';
                label.firstElementChild.style.color = '#c58430';
            }
        }
    })

    if (ratingSum == 0) {
        $averageRating.innerHTML = '-/-';
        return
    }

    let average = ratingSum / ratingCount;
    $averageRating.innerHTML = `${average.toFixed(1)}/10`;
}
