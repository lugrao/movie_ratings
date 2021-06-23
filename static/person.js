let $loadMore = document.getElementById("load-more")
let $resultsList = document.getElementById("results-list")
let query
let page = 2
let $jobList = document.querySelectorAll(".job-list")
let $jobNames = document.querySelectorAll(".job-name")

$jobNames.forEach((jobName) => {
  jobName.addEventListener("click", handleClick)
})

$jobList.forEach((list) => {
  list.style.display = "none"
})

if ($loadMore) {
  query = $loadMore.dataset.query
  $loadMore.addEventListener("click", loadMoreResults)
}

function handleClick(event) {
  let job = event.target
  let collapsed = job.dataset.collapsed
  let list = job.nextElementSibling

  if (collapsed == "true") {
    job.dataset.collapsed = "false"
    text = job.innerText
    job.innerText = `${text.slice(0, text.length - 1)}▾`
    list.style.display = ""
  } else {
    job.dataset.collapsed = "true"
    text = job.innerText
    job.innerText = `${text.slice(0, text.length - 1)}▸`
    list.style.display = "none"
  }
}

async function loadMoreResults() {
  let url = `/more-person-results/${query}/${page}`
  let response
  let $li = document.querySelectorAll("li")
  let scrollItem = $li[$li.length - 1]
  console.log(scrollItem)

  try {
    response = await fetch(url)
      .then((res) => res.json())
      .then((data) => data)
  } catch (error) {
    return console.error(error)
  }

  response.results.forEach((person) => {
    let new_person = document.createElement("li")
    let imgPath = person["profile_path"]
      ? "https://www.themoviedb.org/t/p/w180_and_h180_face/" +
        person["profile_path"]
      : "/static/blank_profile_pic.png"

    let movies = ""
    if (person["known_for"]) {
      person["known_for"].forEach((movie, i, ar) => {
        movies += `<a href="/movie/${movie["id"]}">${movie["title"]}</a>${
          i == ar.length - 1 ? "." : ", "
        }`
      })
    }

    new_person.innerHTML = `
        <li class="person-info">
            <a href="/person/${person["id"]}">
            <img src="${imgPath}" alt="${person["name"]}" width="100" height="100">
            ${person["name"]}</a> - ${person["known_for_department"]}
            <br>
            <br>
            <p>
                ${movies}
            </p>
        </li>
        `

    $resultsList.appendChild(new_person)
  })

  scrollItem.scrollIntoView()

  page++

  if (page > response["total_pages"]) {
    $loadMore.style.display = "none"
  }
}
