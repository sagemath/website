function tracklinks(id, cat) {
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
}
