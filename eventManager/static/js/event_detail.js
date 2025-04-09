document.addEventListener("DOMContentLoaded", function () {
    // Проверка формата события
    if (eventData.format === "Online") {
        document.getElementById("location_offline").style.display = "none";
        document.getElementById("map_place").style.display = "none";
        document.getElementById("location_online").style.display = "block";
        console.log('location_online');
    } else {
        document.getElementById("location_offline").style.display = "block";
        document.getElementById("map_place").style.display = "block";
        document.getElementById("location_online").style.display = "none";
        console.log('location_offline');
    }

    // Работа с картой
    var mapFrame = document.getElementById("mapFrame");
    var fullAddress = eventData.city && eventData.locationOffline ? 
        `${eventData.city}, ${eventData.locationOffline}` : 
        eventData.city || eventData.locationOffline;

    if (fullAddress && mapFrame) {
        var yandexApiUrl = `https://geocode-maps.yandex.ru/1.x/?format=json&apikey=72ad0fbf-7eeb-44ea-8f5d-2bc7174230be&geocode=${encodeURIComponent(fullAddress)}&results=1`;

        fetch(yandexApiUrl)
            .then(response => response.json())
            .then(data => {
                var geoObjects = data.response.GeoObjectCollection.featureMember;
                if (geoObjects.length > 0) {
                    var geoObject = geoObjects[0].GeoObject;
                    var coordinates = geoObject.Point.pos.split(" ");
                    var lon = coordinates[0], lat = coordinates[1];
                    var mapSrc = `https://yandex.ru/map-widget/v1/?ll=${lon},${lat}&z=15&pt=${lon},${lat},pm2rdm`;
                    mapFrame.src = mapSrc;
                }
            })
            .catch(error => console.error("Ошибка загрузки карты:", error));
    }

    // Обработка кликов по событиям
    const events = document.querySelectorAll(".all_event_grid_item");
    events.forEach(event => {
        event.addEventListener("click", function() {
            const eventId = event.id.split("-")[1];
            window.location.href = `/events/${eventId}/`;
        });
    });
});
document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".event_place_btn, .all_event_grid_item_btn").forEach(button => {
        button.addEventListener("click", async function (e) {
            e.stopPropagation();

            const eventId = this.getAttribute("data-id");
            const csrfToken = getCSRFToken();

            try {
                const response = await fetch(`/events/${eventId}/register/`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": csrfToken,
                    },
                    body: JSON.stringify({}),
                });

                const contentType = response.headers.get("content-type") || "";

                // Если вернулся не JSON — значит редирект на форму (или неавторизован)
                if (!contentType.includes("application/json")) {
                    // Перенаправляем на форму для неавторизованных
                    window.location.href = `/events/${eventId}/registration_not_auth_user/`;
                    return;
                }

                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.message || "Ошибка при записи");
                }

                alert(data.message);
                if (data.success) {
                    location.reload();
                }
            } catch (error) {
                console.error("Ошибка:", error);
                alert(error.message || "Произошла ошибка при записи");
            }
        });
    });
});

function getCSRFToken() {
            return document.querySelector("meta[name='csrf-token']")?.content || "";
        }



