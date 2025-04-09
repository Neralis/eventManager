    document.getElementById("event-format-filter").addEventListener("change", function () {
        let format = this.value;
        let url = new URL(window.location.href);
        
        if (format) {
            url.searchParams.set("event_format", format);
        } else {
            url.searchParams.delete("event_format");
        }
        
        window.location.href = url.toString();
    });

    document.getElementById("event-date-filter").addEventListener("change", function () {
        let date = this.value;
        let url = new URL(window.location.href);

        if (date) {
            url.searchParams.set("date_start", date);
        } else {
            url.searchParams.delete("date_start");
        }

        window.location.href = url.toString();
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
                    params.delete("city");  
                } else {
                    params.set("city", city);  
                }

                window.location.search = params.toString(); 
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
        // Получаем форму и кнопку по классу
        const form = document.querySelector(".header_func_search");
        const button = document.querySelector(".header_btn_search");

        // Добавляем обработчик события на кнопку
        button.addEventListener("click", function () {
            form.submit();  // Отправляем форму
        });
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

    document.addEventListener("DOMContentLoaded", function () {
        document.querySelectorAll(".all_event_grid_item_btn").forEach(button => {
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
