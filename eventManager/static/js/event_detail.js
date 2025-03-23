document.addEventListener("DOMContentLoaded", function () {
    var isOnline = "{{ object.event_format }}"=== "Online";  // Предполагаем, что в объекте есть поле is_online (True/False)
    
    if (isOnline) {
        document.getElementById("location_onffine").style.display = "none";
        document.getElementById("map_place").style.display = "none"
        document.getElementById("location_online").style.display = "block"
    }
    else{
        document.getElementById("location_onffine").style.display = "block";
        document.getElementById("map_place").style.display = "block"
        document.getElementById("location_online").style.display = "none"
   
    }
});

document.addEventListener("DOMContentLoaded", function () {
    var city = "{{ object.city|default:''|escapejs }}";  // Город
    var locationOffline = "{{ object.location_offline|default:''|escapejs }}";  // Улица и дом
    var mapFrame = document.getElementById("mapFrame");

    var fullAddress = city && locationOffline ? `${city}, ${locationOffline}` : city || locationOffline;

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
                } else {
                    console.error("Адрес не найден");
                }
            })
            .catch(error => console.error("Ошибка загрузки карты:", error));
    }
});

document.addEventListener("DOMContentLoaded",function(){
    const events = document.querySelectorAll(".all_event_grid_item")

    events.forEach(event => {
        event.addEventListener("click", function(){
            const eventId = event.id.split("-")[1]
            window.location.href = `/events/${eventId}/`

        })
        
    })
   
})