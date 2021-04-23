let sessionStorage = window.sessionStorage;
let $selectSearch = document.getElementById('select-search');
let $searchMovie = document.getElementById('search-movie');
let $searchPerson = document.getElementById('search-person');
let $searchFields = document.querySelectorAll('.search-form');
let $dummyOption = document.querySelector('option');
$dummyOption.style.display = 'none';

$selectSearch.addEventListener('change', handleChange);

if (sessionStorage.getItem('search_type')) {
    $selectSearch.value = sessionStorage.getItem('search_type');
    switchSearch($selectSearch.value);
    document.getElementById($selectSearch.value)[0].focus();
} else {
    sessionStorage.setItem('search_type', 'search-movie');
    $selectSearch.value = 'search-movie';
    switchSearch('search-movie');
    document.getElementById($selectSearch.value)[0].focus();
}


function handleChange(event) {
    let value = event.target.value;
    switchSearch(value);
    sessionStorage.setItem('search_type', value);
}


function switchSearch(value) {
    $searchFields.forEach(element => {
        if (element.id != value) {
            element.style.display = 'none';
        } else {
            element.style.display = '';
        }
    })
}