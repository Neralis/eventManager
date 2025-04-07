document.addEventListener("DOMContentLoaded", function () {
    const stars = document.querySelectorAll(".add_review_stars .add_review_star");
    const ratingInput = document.getElementById("rating-value");
    const error = document.querySelector(".add_review_star_error")

    let selectedRating = 0;

    function updateStars() {
        stars.forEach((star) => {
            const starValue = parseFloat(star.getAttribute("data-value"));
            if (starValue <= selectedRating) {
                star.classList.add("active");
            } else {
                star.classList.remove("active");
            }
        });
    }

    stars.forEach((star) => {
        star.addEventListener("click", function () {
            selectedRating = parseFloat(star.getAttribute("data-value"));
            ratingInput.value = selectedRating;
            updateStars();
            error.style.visibility = "hidden"
        });
    });

    // Обработчик отправки формы
    const form = document.querySelector(".add_review_form");
    form.addEventListener("submit", function (event) {
        event.preventDefault(); 
        const rating = parseFloat(ratingInput.value);
        if (rating > 0) {
            event.target.submit();
        } else {
            error.style.visibility = "visible"
        }
    });
});