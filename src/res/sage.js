/** global sagemath.org javascript file
 *  author: harald schilly <harald.schilly@gmail.com>
 *  license: apache 2.0
 * */

var isTouch = !!('ontouchstart' in window);
var isMac = navigator.platform.toUpperCase().indexOf('MAC')!==-1;
var isWindows = navigator.platform.toUpperCase().indexOf('WIN')!==-1;
var isLinux = navigator.platform.toUpperCase().indexOf('LINUX')!==-1;

var sage = {
    tracklinks: function () {
        $("[track]").each(function() {
            var $this = $(this);
            var cat = $this.attr("track");
            $this.children("a").each(function() {
               var $a = $(this);
               $a.click(function() {
                 pageTracker._trackEvent('Clicks', cat, $a.attr("href"), 0);
               });
            });
        });
    },

    /* this variant doesn't work ...
    tracklinks: function() {
        $("*[track] a").on("click", function() {
            var $a = $(this);
            var $track = $a.parent("*[track]");
            var cat = $track.attr("track");
            pageTracker._trackEvent('Clicks', cat, $a.attr("href"), 0);
        });
    },
    */

    downloadUrl: function() {
        if (isWindows) return "download-windows.html";
        if (isMac)     return "download-mac.html";
        if (isLinux)   return "download-linux.html";
        return "download.html";
    },

    setDownloadUrls: function () {
        $("a[downloadurl]").each(function() {
            this.href = sage.downloadUrl();
        });
    },

    scrollNavbarInit: function () {
        var $w = $(window);
        var $navbar = $('#sage-nav');
        var navbar_top = $navbar.offset().top;
        $navbar.css({'width' : $navbar.width()});
        var height = $navbar.height();
        $nav_buffer = $("#sage-nav-buffer");
        $nav_buffer.height(height);

        /* note to self: animation is cute, but one has to device a way to re-trigger it while animations are still running */
        var scrollNavbar = function(){
            var curtop = $w.scrollTop();
            if (curtop > navbar_top) {
                $navbar.css({"position" : "fixed", "top" : 0, 'height' : "3em", background: "#e9e9f9"});
                /* $navbar.animate({'height' : "3em", background: "#e9e9f9"}); */
                $nav_buffer.show();
            } else {
                $navbar.css({'position': 'relative', "height" : height, background: "#fff"});
                /* $navbar.animate({"height" : height, background: "#fff" }); */
                $nav_buffer.hide();
            }
        };

        /* run it once and then every time the window scrolls */
        scrollNavbar();
        $(window).scroll(scrollNavbar);
    },

    touchMenu: function() {
        if (!isTouch) { return; }
        var cn = "hovered";
        var menus = [];
        var active = -1;

        /* tri-state mechanism to show submenus on touch devices */
        $("#sage-nav > li > a").each(function(idx) {
            var $a = $(this);
            var $li = $a.parent("li");
            menus.push($li);

            $li.click(function(evt) {
                if (active >= 0) {
                    if (active == idx) {
                        return;
                    } else {
                        menus[active].removeClass(cn);
                    }
                }
                evt.preventDefault();
                $li.addClass(cn);
                active = idx;
            });
        });

        /* this removes the menu by clicking somewhere else */
        $("html").on("click", function (evt) {
            if ($(evt.target).parents("#sage-nav").length) {
                return;
            }
            if (active >= 0) {
                menus[active].removeClass(cn);
                active = -1;
            }
        });
    }
};

$(sage.setDownloadUrls);
$(sage.scrollNavbarInit);
$(sage.touchMenu);
$(sage.tracklinks);