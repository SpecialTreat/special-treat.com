jQuery(document).ready(function($) {

    var $days = $('td.day');

    $('.gregorian-to-discordian-calendar [data-toggle="tooltip"]').tooltip({
        container : '.gregorian-to-discordian-calendar'
    });

    $('.discordian-to-std-scale [data-toggle="tooltip"]').tooltip({
        container : '.discordian-to-std-scale'
    });

    $days.hover(function(event) {
        try {
            var dayNumber = $(this).data("day");
            $("td.day-" + dayNumber).addClass("active").tooltip("show");
        } catch(ex) {}
    },
    function(event) {
        try {
            var dayNumber = $(this).data("day");
            $("td.day.active").removeClass("active").tooltip("hide");
        } catch(ex) {}
    });
});
