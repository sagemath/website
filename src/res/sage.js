/** global sagemath.org javascript file
 *  author: harald schilly <harald.schilly@gmail.com>
 *  license: apache 2.0
 * */

var isTouch = !!('ontouchstart' in window);
var isMac = navigator.platform.toUpperCase().indexOf('MAC')!==-1;
var isWindows = navigator.platform.toUpperCase().indexOf('WIN')!==-1;
var isLinux = navigator.platform.toUpperCase().indexOf('LINUX')!==-1;

var sage = {
    //tracklinks: function () {
    //    $("[track]").each(function() {
    //        var $this = $(this);
    //        var cat = $this.attr("track");
    //        $this.children("a").each(function() {
    //           var $a = $(this);
    //           $a.click(function() {
    //             pageTracker._trackEvent('Clicks', cat, $a.attr("href"), 0);
    //           });
    //        });
    //    });
    //},

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
        if (isWindows) return "/download-windows.html";
        if (isMac)     return "/download-mac.html";
        if (isLinux)   return "/download-linux.html";
        return "/download.html";
    },

    setDownloadUrls: function () {
        $("a[downloadurl]").each(function() {
            this.href = sage.downloadUrl();
        });
    },

    scrollNavbarInit: function () {
        var $w = $(window);
        var $b = $("body");
        var $navbar = $('#sage-nav');
        var navbar_top = $navbar.offset().top;
        $navbar.css({'width' : $navbar.width()});
        var height = $navbar.height();
        $nav_buffer = $("#sage-nav-buffer");
        $nav_buffer.height(height);

        /* note to self: animation is cute, but one has to device a way to re-trigger it while animations are still running */
        var scrollNavbar = function(){
            /* -10 or -9?, see CSS */
            $navbar.width($b.width() - 10);
            var curtop = $w.scrollTop();
            if (curtop > navbar_top) {
                var left = $b.offset().left;
                if ($b.offset().left == 0 && $w.scrollLeft() > 0) {
                    left = -$w.scrollLeft();
                }
                $navbar.css({"position" : "fixed",
                    "top" : 0, "left" : left,
                    'height' : "3em", background: "#e9e9f9"});
                /* $navbar.animate({'height' : "3em", background: "#e9e9f9"}); */
                $nav_buffer.show();
            } else {
                $navbar.css({'position': 'relative',
                "height" : height, background: "#fff", "left" : 0});
                /* $navbar.animate({"height" : height, background: "#fff" }); */
                $nav_buffer.hide();
            }
        };


        /* scroll up, G+ style */
        $navbar.on("click", function(evt) {
            if (this == evt.target) {
                $("html, body").animate({scrollTop: 0}, "slow");
            }
        });

        /* run it once and then every time the window scrolls or resizes */
        scrollNavbar();
        $w.scroll(scrollNavbar);
        $w.resize(scrollNavbar);
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
                    }
                    menus[active].removeClass(cn);
                }
                evt.preventDefault();
                evt.stopPropagation();
                $li.addClass(cn);
                active = idx;
                return false;
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

/* MathJax */
function initMathjax() {
  var head = document.getElementsByTagName("head")[0], script;
  script = document.createElement("script");
  script.type = "text/x-mathjax-config";
  script[(window.opera ? "innerHTML" : "text")] =
    "MathJax.Hub.Config({\n" +
    "  tex2jax: { inlineMath: [['$','$'], ['\\\\(','\\\\)']] }\n" +
    "});"
  head.appendChild(script);
  script = document.createElement("script");
  script.type = "text/javascript";
  script.src  = "//cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML";
  head.appendChild(script);
}

/* Twitter */
function initTwitter(d,s,id){
  var js,fjs=d.getElementsByTagName(s)[0],p=/^http:/.test(d.location)?'http':'https';
  if(!d.getElementById(id)){
    js=d.createElement(s);
    js.id=id;
    js.src=p+'://platform.twitter.com/widgets.js';
    fjs.parentNode.insertBefore(js,fjs);
  }
}

/* facebook app */
//function initFacebook(d, s, id) {
//  var js, fjs = d.getElementsByTagName(s)[0];
//  if (d.getElementById(id)) return;
//  js = d.createElement(s); js.id = id;
//  js.src = "//connect.facebook.net/en_US/sdk.js#xfbml=1&appId=109731879648&version=v2.0";
//  fjs.parentNode.insertBefore(js, fjs);
//}

//var _gaq = _gaq || [];
//_gaq.push(['_setAccount', 'UA-66100-10']);
//_gaq.push(['_setDomainName("sagemath.org")']);
//_gaq.push(['_setAllowLinker(true)']);
//_gaq.push(['_trackPageview']);
//_gaq.push(['_trackPageLoadTime']);
//
//function googleAnalytics() {
//  var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
//  ga.src = ('https:' == document.location.protocol ? 'https://' : 'http://') + 'stats.g.doubleclick.net/dc.js';
//  var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
//}

var _Hasync= _Hasync|| [];
_Hasync.push(['Histats.startgif', '1,1579950,4,10051,"div#histatsC {position: absolute;top:0px;left:0px;}body>div#histatsC {position: fixed;}"']);
_Hasync.push(['Histats.fasi', '1']);
_Hasync.push(['Histats.track_hits', '']);

function initHistats() {
  var hs = document.createElement('script'); hs.type = 'text/javascript'; hs.async = true;
  hs.src = ('//s10.histats.com/js15_gif_as.js');
  (document.getElementsByTagName('head')[0] || document.getElementsByTagName('body')[0]).appendChild(hs);
}

function initClustermap() {
 function _cantload() {
   var img = document.getElementById("clustrMapsImg");
   img.onerror = null;
   img.src = "https://www.clustrmaps.com/images/clustrmaps-back-soon.jpg";
   document.getElementById("clustrMapsLink").href = "https://www.clustrmaps.com";
 }
 var img = document.getElementById("clustrMapsImg");
 img.onerror = _cantload;
}

$(sage.setDownloadUrls);
$(sage.scrollNavbarInit);
$(sage.touchMenu);
//$(googleAnalytics);
//$(sage.tracklinks);
$(initHistats);
$(initMathjax);
$(function() { initTwitter(document, 'script', 'twitter-wjs');});
//$(function() { initFacebook(document, 'script', 'facebook-jssdk');});
$(initClustermap);
