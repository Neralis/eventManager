function toggleAddressField() {
    let format = document.getElementById("format").value;
    document.getElementById("offline-address").style.display = (format === "Offline") ? "block" : "none";
    document.getElementById("city").style.display = (format === "Offline") ? "block" : "none"
    document.getElementById("online-address").style.display = (format === "Online") ? "block" : "none";
}

// Вызываем функцию при загрузке страницы, чтобы сразу показать нужное поле
window.onload = toggleAddressField;