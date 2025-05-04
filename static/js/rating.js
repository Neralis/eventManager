document.addEventListener('DOMContentLoaded', function () {
    const ratingContainers = document.querySelectorAll('.rating-stars');

    ratingContainers.forEach(container => {
        const rating = parseFloat(container.getAttribute('data-rating'));
        const stars = container.querySelectorAll('.star');

        stars.forEach(star => {
            const starValue = parseInt(star.getAttribute('data-value'));

            if (starValue <= Math.floor(rating)) {
                star.classList.add('filled');
            } else if (starValue === Math.ceil(rating) && rating % 1 >= 0.5) {
                star.classList.add('half-filled');
            }
        });
    });
});