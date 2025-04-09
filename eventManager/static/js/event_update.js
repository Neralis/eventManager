document.addEventListener("DOMContentLoaded", function () {
function toggleAddressField() {
    let format = document.querySelector("select[name='event_format']").value;

    let offlineInput = document.querySelector("input[name='location_offline']");
    let onlineInput = document.querySelector("input[name='location_online']");
    let cityInput = document.querySelector("input[name='city']");

    let offlineBlock = document.getElementById("offline-address");
    let onlineBlock = document.getElementById("online-address");
    let cityBlock = document.getElementById("city");

    if (format === "Offline") {
        offlineBlock.style.display = "block";
        cityBlock.style.display = "block";
        onlineBlock.style.display = "none";

        offlineInput.required = true;
        cityInput.required = true;
        onlineInput.required = false;

        onlineInput.value = "";  
    } else {
        offlineBlock.style.display = "none";
        cityBlock.style.display = "none";
        onlineBlock.style.display = "block";

        offlineInput.required = false;
        cityInput.required = false;
        onlineInput.required = true;

        offlineInput.value = "";  
        cityInput.value = "";     
    }
}

let imagesToRemove = [];


    function removeImage(button, imageId) {

        const imageItem = button.closest('.image-item');
        if (imageItem) {
            imageItem.remove();
            
            imagesToRemove.push(imageId);
            
            document.getElementById('images_to_remove').value = imagesToRemove.join(',');
        }
    }

    function removeMainImage() {

        const imageContainer = document.querySelector('.create_event_form_file .position-relative');
        if (imageContainer) {
            imageContainer.style.display = 'none';
            
            document.getElementById('remove_main_photo').value = 'true';
        }
    }


    window.onload = function() {
        toggleAddressField();
        document.querySelector("select[name='event_format']").addEventListener("change", toggleAddressField);
    };

    const create_form = document.querySelector('.create_event_form')
    const date_start = document.querySelector('.create_event_form_dateStart')
    const date_end = document.querySelector('.create_event_form_dateEnd')
    
    create_form.addEventListener('change', () =>{
        const startDate = new Date(date_start.value);
        const endDate = new Date(date_end.value);
        
        if (startDate >= endDate) {
            date_start.setCustomValidity("Дата конца не может быть раньше даты начала");
        } else {
            date_start.setCustomValidity("");
        }
    });

create_form.addEventListener('submit', (event) => {
    if (!create_form.checkValidity()) {
        event.preventDefault();
        console.log("Форма невалидна");
    }
});
});
