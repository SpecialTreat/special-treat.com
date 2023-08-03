
jQuery(document).ready(function($) {

    var $window = $(window),
        $body = $('body'),
        $navbar = $('#top-navbar'),
        $navbarContent = $('#top-navbar-content'),
        $navbarToggle = $('#top-navbar-toggle');

    $body.localScroll({
        filter:'.smoothScroll',
        duration: 300,
        hash: true,
        onBefore: function() {
            if ($navbarToggle.is(':visible')) {
                $navbarContent.collapse('hide');
            }
        }
    });

    $navbarContent.on('hide.bs.collapse', function () {
        $navbar.removeClass('expanded');
    });

    $navbarContent.on('show.bs.collapse', function () {
        $navbar.addClass('expanded');
    });

    var navbarHeight = $navbar.outerHeight()
    var transparencyOffset = Math.max(100 - navbarHeight, navbarHeight);

    var updateNavbarTransparency = function() {
        if ($window.scrollTop() >= transparencyOffset) {
            $navbar.addClass('opaque');
        } else {
            $navbar.removeClass('opaque');
        }
    };
    updateNavbarTransparency();
    $window.scroll(updateNavbarTransparency);
});
