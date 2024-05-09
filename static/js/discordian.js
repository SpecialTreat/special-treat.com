document.addEventListener("DOMContentLoaded", function() {

    var tooltipElements = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    var tooltips = [...tooltipElements].map(el => new bootstrap.Tooltip(el));

    var days = document.querySelectorAll('td.day');
    days.forEach((day) => {
        day.addEventListener("mouseenter", (event) => {
            try {
                var dayNumber = event.target.dataset.day;
                var otherDays = document.querySelectorAll("td.day-" + dayNumber);
                otherDays.forEach((otherDay) => {
                    if (!otherDay.classList.contains('active')) {
                        otherDay.classList.add('active');
                    }
                    bootstrap.Tooltip.getOrCreateInstance(otherDay).show()
                });
            } catch(ex) {}
        });

        day.addEventListener("mouseleave", (event) => {
            try {
                var dayNumber = event.target.dataset.day;
                var otherDays = document.querySelectorAll("td.day.active");
                otherDays.forEach((otherDay) => {
                    if (otherDay.classList.contains('active')) {
                        otherDay.classList.remove('active');
                    }
                    bootstrap.Tooltip.getOrCreateInstance(otherDay).hide()
                });
            } catch(ex) {}
        });
    });
});
