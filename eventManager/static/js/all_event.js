document.getElementById("event-format-filter").addEventListener("change", function () {
    let format = this.value;
    let url = new URL(window.location.href);
    
    if (format) {
        url.searchParams.set("event_format", format);
    } else {
        url.searchParams.delete("event_format");
    }
    
    window.location.href = url.toString();  // Обновляем страницу с новым фильтром
});

document.getElementById("event-date-filter").addEventListener("change", function () {
    let date = this.value;
    let url = new URL(window.location.href);

    if (date) {
        url.searchParams.set("date_start", date);
    } else {
        url.searchParams.delete("date_start");
    }

    window.location.href = url.toString();  // Перезагрузка страницы с новым фильтром
});

document.addEventListener("DOMContentLoaded", function () {
    const categorySelect = document.getElementById("event-category-filter");

    if (categorySelect) {
        categorySelect.addEventListener("change", function () {
            let params = new URLSearchParams(window.location.search);

            let category = categorySelect.value;
            if (category) {
                params.set("category", category);
            } else {
                params.delete("category");
            }

            window.location.search = params.toString();
        });
    }
});

document.addEventListener("DOMContentLoaded", function () {
    const citySelect = document.getElementById("event-city-filter");

    if (citySelect) {
        citySelect.addEventListener("change", function () {
            let params = new URLSearchParams(window.location.search);

            let city = citySelect.value;
            if (city === "all") {
                params.delete("city");  // Удаляем параметр city, если выбрано "Все"
            } else {
                params.set("city", city);  // Устанавливаем параметр city
            }

            window.location.search = params.toString();  // Перезагрузка страницы с новым фильтром
        });
    }
});
function resetFilters(){
    const url = new URL(window.location.href)
    const params = new URLSearchParams(url.search)

    params.delete('category')
    params.delete('city')
    params.delete('date_start')
    params.delete('event_format')

    url.search = params.toString()
    window.location.href = url.toString()
}
document.addEventListener("DOMContentLoaded", function () {
    let csrfToken = document.querySelector("meta[name='csrf-token']").getAttribute("content");

    document.querySelectorAll(".delete-event-btn").forEach(button => {
        button.addEventListener("click", function () {
            let eventId = this.getAttribute("data-event-id");

            if (!confirm("Вы уверены, что хотите удалить событие?")) {
                return;
            }

            fetch(`/events/delete/${eventId}/`, {
                method: "DELETE",
                headers: {
                    "X-CSRFToken": csrfToken,
                    "Content-Type": "application/json"
                }
            }).then(response => response.json()).then(data => {
                if (data.message) {
                    document.getElementById(`event-${eventId}`).remove();
                } else {
                    alert("Ошибка при удалении: " + data.error);
                }
            }).catch(error => {
                alert("Ошибка при удалении! " + error);
            });
        });
    });
});

document.addEventListener("DOMContentLoaded", function () {
    // Получаем форму и кнопку по классу
    const form = document.querySelector(".header_func_search");
    const button = document.querySelector(".header_btn_search");

    // Добавляем обработчик события на кнопку
    button.addEventListener("click", function () {
        form.submit();  // Отправляем форму
    });
});

