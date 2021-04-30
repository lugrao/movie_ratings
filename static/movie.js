let storage = window.localStorage;
let movieId = document.querySelector("#movie").dataset.tmdbid;
let $loadMore = document.getElementById("load-more");
let $moreResultsList = document.getElementById("more-results-list");
let $inputs = document.querySelectorAll(".checkbox div input");
let $averageRating = document.getElementById("average-rating");
let page = 2;

if ($loadMore) $loadMore.addEventListener("click", loadMoreResults);

$inputs.forEach((input) => {
  input.addEventListener("click", updateRating);
});

let metacritic = document.querySelector('[for="metacritic-rating"]');
if (metacritic.innerHTML.includes("Not found"))
  metacritic.innerHTML = "Metacritic rating: <span>loading...</span>";

let rottenTomatoes = document.querySelector('[for="rotten-tomatoes-rating"]');
if (rottenTomatoes.innerHTML.includes("Not found"))
  rottenTomatoes.innerHTML = "Rotten Tomatoes rating: <span>loading...</span>";

updateRating();
getRating("letterboxd");
getRating("filmaffinity");
if (metacritic.innerHTML.includes("loading")) getRating("metacritic");
if (rottenTomatoes.innerHTML.includes("loading")) getRating("rotten-tomatoes");

async function getRating(site) {
  let isFirstVisit = false;
  let storageItem = `/movie/${movieId}/${site}`;
  let $movie = document.getElementById("movie");
  let tmdbID = $movie.dataset.tmdbid;
  let title = $movie.dataset.title;
  let originalTitle = $movie.dataset.originaltitle;
  let alternativeTitles = $movie.dataset.alternativetitles;
  let year = $movie.dataset.year;
  let $checkbox = document.getElementsByName(`${site}-rating`)[0];
  let $label = $checkbox.previousElementSibling;
  let labelName;
  let url = `/${site}-rating/`;
  let query;
  let response;

  switch (site) {
    case "rotten-tomatoes":
      labelName = "Rotten Tomatoes";
      query = `?t=${title}&y=${year}`;
      break;
    case "metacritic":
      labelName = "Metacritic";
      query = `?t=${title}&y=${year}`;
      break;
    case "letterboxd":
      labelName = "Letterboxd";
      query = `?id=${tmdbID}&t=${title}&y=${year}`;
      break;
    case "filmaffinity":
      labelName = "FilmAffinity";
      query = `?t=${title}&ot=${originalTitle}&at=${alternativeTitles}&y=${year}`;
      break;
  }

  if (!storage.getItem(storageItem)) {
    try {
      response = await fetch(url + query)
        .then((res) => res.json())
        .then((data) => data);
      storage.setItem(storageItem, JSON.stringify(response));
      isFirstVisit = true;
    } catch (error) {
      $label.style.color = "black";
      $label.innerHTML = `${labelName} rating: <span style="color: crimson;">error</span>.`;
      return console.error(error);
    }
  } else {
    response = JSON.parse(storage.getItem(storageItem));
  }

  $label.innerHTML = `<a href="${response.url}" target="_blank">${labelName}</a> rating: ${response.rating[0]}`;
  $label.style.color = "black";
  $checkbox.dataset.rating = response.rating[1];
  $checkbox.checked = true;
  $checkbox.disabled = false;
  $checkbox.className = "clickable";

  updateRating();
  if (isFirstVisit) return;

  try {
    response = await fetch(url + query)
      .then((res) => res.json())
      .then((data) => data);
    stored_data = JSON.parse(storage.getItem(storageItem));

    if (stored_data.rating[0] != response.rating[0]) {
      storage.setItem(storageItem, JSON.stringify(response));
      $label.innerHTML = `<a href="${response.url}" target="_blank">${labelName}</a> rating: ${response.rating[0]}`;
      $label.style.color = "black";
      $checkbox.dataset.rating = response.rating[1];
      $checkbox.checked = true;
      $checkbox.disabled = false;
      $checkbox.className = "clickable";
      updateRating();
    }
  } catch (error) {
    return console.error(error);
  }
}

function updateRating() {
  let ratingSum = 0;
  let ratingCount = 0;

  $inputs.forEach((input) => {
    if (input.checked == true && input.dataset.rating != "-1") {
      ratingSum += Number(input.dataset.rating);
      ratingCount++;
    } else if (input.dataset.rating == "-1") {
      input.disabled = true;
      input.className = "";
      input.checked = false;

      let label = input.previousElementSibling;
      label.style.color = "grey";
      if (label.innerText.includes("loading")) {
        label.style.color = "black";
        label.firstElementChild.style.color = "#c58430";
      }
    }
  });

  if (ratingSum == 0) {
    $averageRating.innerHTML = "-/-";
    return;
  }

  let average = ratingSum / ratingCount;
  $averageRating.innerHTML = `${average.toFixed(1)}/10`;
}

async function loadMoreResults() {
  let title = $loadMore.dataset.title;
  let year = $loadMore.dataset.year;
  let id = $loadMore.dataset.id;
  let url = `/more-movie-results/?t=${title}&y=${year}&id=${id}&p=${page}`;
  let response;
  let $li = document.querySelectorAll("li");
  let scrollItem = $li[$li.length - 1];

  try {
    response = await fetch(url)
      .then((res) => res.json())
      .then((data) => data);
  } catch (error) {
    return console.error(error);
  }

  response.movies.forEach((movie) => {
    let new_movie = document.createElement("li");
    new_movie.innerHTML = `<a href="/movie/${movie["tmdb-id"]}">${movie["title"]} ${movie["year"]}</a>`;
    $moreResultsList.appendChild(new_movie);
  });

  scrollItem.scrollIntoView();

  page++;

  if (page > response["total_pages"]) {
    $loadMore.style.display = "none";
  }
}
