document.addEventListener("DOMContentLoaded", function() {
    var $navbar = document.getElementById('top-navbar');

    if (!$navbar.classList.contains('opaque')) {
        var $navbarContent = document.getElementById('top-navbar-content');
        $navbarContent.addEventListener('hide.bs.collapse', function () {
            if ($navbar.classList.contains('expanded')) {
                $navbar.classList.remove('expanded');
            }
        });
        $navbarContent.addEventListener('show.bs.collapse', function () {
            if (!$navbar.classList.contains('expanded')) {
                $navbar.classList.add('expanded');
            }
        });

        var navbarHeight = $navbar.getBoundingClientRect().height;
        var transparencyOffset = Math.max(100 - navbarHeight, navbarHeight);

        var updateNavbarTransparency = function() {
            var scrolled = document.scrollingElement.scrollTop;
            if (scrolled >= transparencyOffset) {
                if (!$navbar.classList.contains('opaque')) {
                    $navbar.classList.add('opaque');
                }
            } else {
                if ($navbar.classList.contains('opaque')) {
                    $navbar.classList.remove('opaque');
                }
            }
        };
        updateNavbarTransparency();
        window.addEventListener('scroll', updateNavbarTransparency);
    }
});
