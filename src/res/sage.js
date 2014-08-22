/** global sagemath.org javascript file
 *  author: harald schilly <harald.schilly@gmail.com>
 *  license: apache 2.0
 * */

var isTouch = !!('ontouchstart' in window);
var isMac = navigator.platform.toUpperCase().indexOf('MAC')!==-1;
var isWindows = navigator.platform.toUpperCase().indexOf('WIN')!==-1;
var isLinux = navigator.platform.toUpperCase().indexOf('LINUX')!==-1;

var sage = {
    tracklinks: function (id, cat) {
        var list = document.getElementById(id);
        if (!list) { return; }
        function getTarget(x){
            x = x || window.event;
            return x.target || x.srcElement;
        }
        function klick(e) {
            var t = getTarget(e);
            //alert (t);
            if (t.nodeName.toLowerCase() == 'a') {
              var u = t.href;
              pageTracker._trackEvent('Clicks', cat, u, 0);
            }
        }
        list.addEventListener('click',klick,false);
    },

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

        /* note to self: animation is cute, but one has to device a way to re-trigger it while animations are still running */
        var scrollNavbar = function(){
            var curtop = $w.scrollTop();
            if (curtop > navbar_top) {
                $navbar.css({"position" : "fixed", "top" : 0, 'height' : "3em", background: "#e9e9f9"});
                /* $navbar.animate({'height' : "3em", background: "#e9e9f9"}); */
            } else {
                $navbar.css({'position': 'relative', "height" : height, background: "#fff"});
                /* $navbar.animate({"height" : height, background: "#fff" }); */
            }
        };

        /* run it once and then every time the window scrolls */
        scrollNavbar();
        $(window).scroll(scrollNavbar);
    }
};

$(sage.setDownloadUrls);
$(sage.scrollNavbarInit);