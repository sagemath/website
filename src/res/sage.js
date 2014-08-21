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
    }
};

$(sage.setDownloadUrls);
