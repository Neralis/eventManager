window.addEventListener("DOMContentLoaded", function() {
    const form = document.getElementById("anon-register-form");
    if (!form) return;

    // Маска для ввода телефона
    function setCursorPosition(pos, e) {
        e.focus();
        if (e.setSelectionRange) e.setSelectionRange(pos, pos);
        else if (e.createTextRange) {
            var range = e.createTextRange();
            range.collapse(true);
            range.moveEnd("character", pos);
            range.moveStart("character", pos);
            range.select();
        }
    }

    function mask(e) {
        let matrix = this.placeholder,
            i = 0,
            def = matrix.replace(/\D/g, ""),
            val = this.value.replace(/\D/g, "");
        def.length >= val.length && (val = def);
        matrix = matrix.replace(/[_\d]/g, function(a) {
            return val.charAt(i++) || "_";
        });
        this.value = matrix;
        i = matrix.lastIndexOf(val.substr(-1));
        i < matrix.length && matrix != this.placeholder ? i++ : i = matrix.indexOf("_");
        setCursorPosition(i, this);
    }

    let input = document.querySelector(".registration_form_item_phone");
    input.addEventListener("input", mask, false);
    input.focus();
    setCursorPosition(3, input);

    form.addEventListener("submit", function(e) {
        e.preventDefault();
        console.log("Form submitted");
        console.log("Phone:", form.phone.value);
        console.log("Email:", form.email.value);
        console.log("CSRF Token:", getCSRFToken());
    });


    form.addEventListener("submit", async function(e) {
    e.preventDefault();

    const phone = form.phone.value.trim();
    const email = form.email.value.trim();

    if (!phone || !email) {
        alert("Укажите телефон и email");
        return;
    }

    const eventId = form.dataset.eventId;
    const url = `/events/${eventId}/registration_not_auth_user/`;  // Используем основной endpoint

    try {
        const response = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken(),
            },
            body: JSON.stringify({ phone, email })
        });

        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || "Ошибка сервера");
        }
        
        alert(data.message);
        window.location.href = "/"; // Перенаправление после успешной записи
    } catch (err) {
        alert(err.message || "Ошибка сети или сервера");
        console.error(err);
    }
});

    function getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }
    });