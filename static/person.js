let $jobList = document.querySelectorAll('.job-list');
let $jobNames = document.querySelectorAll('.job-name');

$jobNames.forEach(jobName => {
    jobName.addEventListener('click', handleClick);
});

$jobList.forEach(list => {
    list.style.display = 'none';
})

function handleClick(event) {
    let job = event.target;
    let collapsed = job.dataset.collapsed;
    let list = job.nextElementSibling;

    if (collapsed == 'true') {
        job.dataset.collapsed = 'false';
        text = job.innerText;
        job.innerText = `${text.slice(0, text.length - 1)}▾`;
        list.style.display = '';
    } else {
        job.dataset.collapsed = 'true';
        text = job.innerText;
        job.innerText = `${text.slice(0, text.length - 1)}▸`;
        list.style.display = 'none';
    }
}