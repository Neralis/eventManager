document.querySelector('.participants_list').addEventListener('click', (e) =>{
    if (e.target.className == "star_people" || e.target.className == "star_people active")
        e.target.classList.toggle('active');
})