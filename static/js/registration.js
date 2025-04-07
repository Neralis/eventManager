const registration_form = document.querySelector('.registration_form');

const registration_form_password = registration_form.querySelector('.password');
const registration_form_password_replay = registration_form.querySelector('.password_replay');
const registration_form_data_brt = registration_form.querySelector(".registration_form_item_data_brt");

registration_form_password_replay.addEventListener('change', () =>{
    if (registration_form_password.value != registration_form_password_replay.value){
        registration_form_password_replay.setCustomValidity("Пароли не совпадают");
    }
    else if (/^[0-9]+$/i.test(registration_form_password.value)){
        registration_form_password_replay.setCustomValidity("Пароль содержит только цифры");
    }
    else{
        registration_form_password_replay.setCustomValidity("");
    }
})

registration_form_data_brt.addEventListener("change", () => {
    
    const selectedYear = Number(String(registration_form_data_brt.value.slice(0, 4)));
    const currentYear = new Date().getFullYear();

    if (currentYear - 14 < selectedYear || currentYear - 89 > selectedYear ){
        registration_form_data_brt.setCustomValidity("Ваши возраст не соответствует требованиям");
    }
    else {
        registration_form_data_brt.setCustomValidity("");
    }
})

function setCursorPosition(pos, e) {
    e.focus();
    if (e.setSelectionRange) e.setSelectionRange(pos, pos);
    else if (e.createTextRange) {
      var range = e.createTextRange();
      range.collapse(true);
      range.moveEnd("character", pos);
      range.moveStart("character", pos);
      range.select()
    }
  }

function mask(e) {
    let matrix = this.placeholder,
        i = 0,
        def = matrix.replace(/\D/g, ""),
        val = this.value.replace(/\D/g, "");
    def.length >= val.length && (val = def);
    matrix = matrix.replace(/[_\d]/g, function(a) {
      return val.charAt(i++) || "_"
    });
    this.value = matrix;
    i = matrix.lastIndexOf(val.substr(-1));
    i < matrix.length && matrix != this.placeholder ? i++ : i = matrix.indexOf("_");
    setCursorPosition(i, this)
  }

window.addEventListener("DOMContentLoaded", function() {
    let input = document.querySelector(".registration_form_item_phone");
    input.addEventListener("input", mask, false);
    input.focus();
    setCursorPosition(3, input);
});