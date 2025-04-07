const create_event_form = document.querySelector('.create_event_form');

// category, format
const create_event_category = document.querySelector('.create_event_form_category');
const create_event_format = document.querySelector('.create_event_form_format');

// city, adress, url
const create_event_city = document.querySelector('.create_event_form_item_city');
const create_event_adress = document.querySelector('.create_event_form_item_adress');
const create_event_url = document.querySelector('.create_event_form_item_url');

// dateStart, dateEnd
const create_event_userdate1 = document.querySelector(".create_event_form_dateStart");
const create_event_userdate2 = document.querySelector(".create_event_form_dateEnd");

create_event_format.addEventListener('change', () => {
	if (create_event_format.value == 'internal'){
        create_event_url.style.display = "none";
        create_event_url.value = "";
        create_event_url.required = false;
        create_event_adress.style.display = "block";
        create_event_city.style.display = "block";
        create_event_adress.required = true;
        create_event_city.required = true;
    }
    else{
        create_event_url.style.display = "block";
        create_event_adress.style.display = "none";
        create_event_city.style.display = "none";
        create_event_adress.value = "";
        create_event_city.value = "";
        create_event_adress.required = false;
        create_event_city.required = false;
        create_event_url.required = true;
    }
});

function TDateStart() {
    let userdate1 = create_event_userdate1.value;
    var ToDate = new Date();

    if (new Date(userdate1) <= ToDate) {
        return false;
    }

    return true;
}

function TDateEnd() {
    let userdate1 = create_event_userdate1.value;
    let userdate2 = create_event_userdate2.value;
    
    if (new Date(userdate1) >= new Date(userdate2) && userdate2 != null){
        return false;
    }

    return true;
}

create_event_userdate1.addEventListener("change", () =>{
    if (!TDateStart()) {
        create_event_userdate1.setCustomValidity("Укажите дату больше текущей");
    } else{
        create_event_userdate1.setCustomValidity("");
    }
})

create_event_userdate2.addEventListener("change", () =>{
    if (!TDateEnd()) {
        create_event_userdate2.setCustomValidity("Укажите дату больше даты начала");
    } else{
        create_event_userdate2.setCustomValidity("");
    }
})

create_event_form.addEventListener('submit', (event) =>{
    if (!TDateEnd()) {
        event.preventDefault();
        create_event_userdate2.setCustomValidity("Укажите дату больше даты начала");
    }
})