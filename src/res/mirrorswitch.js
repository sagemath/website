/*
 * this script switches between the mirrors
 * created by Harald Schilly, 2008 for sagemath.org
 * see footer for data
 */

//dont forget: analytics _link function link to new url for cross domains!
function gotoPage(m) {
    var form = document.getElementById("mirrorselector");
    var sel = form.selector;
    var url = unescape(document.location.href);
    var local;
    var localurls = [ "http://www.sagemath.org/sandbox/", "http://lite.sagemath.org/", "http://www.sagemath.org/", "http://sagemath.org/"];
    for (var i = 0; i < localurls.length; i++) {
        local = localurls[i];
        if (url.indexOf(local) == 0) {
           return m + url.substring(local.length, url.length);
        }
    }
    for(var i = 0; i < sel.length; i++) {
        var cursel =  sel[i].value;
        if (url.indexOf(cursel) == 0) {
            //got a hit
            return m + url.substring(cursel.length,url.length);
        }
    }
    return m;
}
function switchPage(m) {
    if (m == "") { return false; }
    var newUrl = gotoPage(m);
    if (pageTracker) {pageTracker._link(newUrl);}
    document.location.href = newUrl;
}


