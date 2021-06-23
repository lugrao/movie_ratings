let $loadMore = document.getElementById("load-more")
let $movieList = document.getElementById("movie-list")
let page = 2
let genre_id = $loadMore.dataset.id
$loadMore.addEventListener("click", loadMoreResults)

async function loadMoreResults() {
  let url = `/more-genre-results/${genre_id}/${page}`
  let response
  let $li = document.querySelectorAll("li")
  let scrollItem = $li[$li.length - 2]

  try {
    response = await fetch(url)
      .then((res) => res.json())
      .then((data) => data)
  } catch (error) {
    return console.error(error)
  }

  response.movies.forEach((movie) => {
    let new_movie = document.createElement("li")
    new_movie.innerHTML = `<a href="/movie/${movie["id"]}">${movie["title"]} ${movie["year"]}</a>`
    $movieList.appendChild(new_movie)
  })

  scrollItem.scrollIntoView()

  page++

  if (page > response["total_pages"]) {
    $loadMore.style.display = "none"
  }
}
