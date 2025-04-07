document.addEventListener("DOMContentLoaded", function () {
    const ratingBlocks = document.querySelectorAll(".rating-stars"); // Находим все блоки с рейтингом

    ratingBlocks.forEach((ratingStars) => {
        const stars = ratingStars.querySelectorAll(".star");
        const ratingValue = parseFloat(ratingStars.getAttribute("data-rating")); // Получаем значение рейтинга

        stars.forEach((star) => {
            const starValue = parseFloat(star.getAttribute("data-value"));

            if (starValue <= Math.floor(ratingValue)) {
                // Закрашиваем звезду полностью, если её значение меньше целой части рейтинга
                star.style.backgroundImage = `linear-gradient(to right, gold 100%, gold 100%)`;
            } else if (starValue === Math.ceil(ratingValue)) {
                // Закрашиваем звезду частично, если её значение равно целой части + 1
                const fraction = ratingValue - Math.floor(ratingValue); // Дробная часть
                star.style.backgroundImage = `linear-gradient(to right, gold ${fraction * 100}%, #ccc ${fraction * 100}%)`;
            } else {
                // Оставляем звезду серой
                star.style.backgroundImage = `linear-gradient(to right, #ccc 100%, #ccc 100%)`;
            }
        });
    });
});