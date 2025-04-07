function toggleAddressField() {
    let format = document.querySelector("select[name='event_format']").value;

    let offlineInput = document.querySelector("input[name='location_offline']");
    let onlineInput = document.querySelector("input[name='location_online']");
    let cityInput = document.querySelector("input[name='city']");  // Исправлено: имя поля 'city'

    if (format === "Offline") {
        document.getElementById("offline-address").style.display = "block";
        document.getElementById("city").style.display = "block";
        document.getElementById("online-address").style.display = "none";
        onlineInput.value = "";  // Очищаем скрытое поле
    } else {
        document.getElementById("offline-address").style.display = "none";
        document.getElementById("city").style.display = "none";
        document.getElementById("online-address").style.display = "block";
        offlineInput.value = "";  // Очищаем скрытое поле
        cityInput.value = "";  // Очищаем поле города
    }
}
let imagesToRemove = [];

    // Функция для удаления дополнительного изображения
    function removeImage(button, imageId) {
        // Находим родительский элемент (колонку) и удаляем его
        const imageItem = button.closest('.image-item');
        if (imageItem) {
            imageItem.remove();
            
            // Добавляем ID изображения в массив для удаления
            imagesToRemove.push(imageId);
            
            // Обновляем скрытое поле с ID изображений для удаления
            document.getElementById('images_to_remove').value = imagesToRemove.join(',');
        }
    }

    // Функция для удаления главного изображения
    function removeMainImage() {
        // Скрываем изображение и родительский контейнер
        const imageContainer = document.querySelector('.create_event_form_file .position-relative');
        if (imageContainer) {
            imageContainer.style.display = 'none';
            
            // Устанавливаем значение скрытого поля в true, чтобы удалить главное изображение
            document.getElementById('remove_main_photo').value = 'true';
        }
    }

    // Инициализация при загрузке страницы
    window.onload = function() {
        toggleAddressField();
        document.querySelector("select[name='event_format']").addEventListener("change", toggleAddressField);
    };