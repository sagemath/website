// --------------------------------------------------------------------
// Javascript Magnifier v 0.97
// Written by Dino Termini - termini@email.it - May 9, 2003
// This script is freeware (GPL) but if you use it, please let me know!
//
// Portions of code by zoomIN, zoomOUT
// Author: Nguyen Duong Minh (Obie) - obie4web@yahoo.com
// WWW: http://ObieWebsite.SourceForge.net
// License: GNU (GPL)
//
// Portions of code by Webreference Javascript Cookie Functions
// Jupirmedia Corporation
// http://www.internet.com
// --------------------------------------------------------------------
//
// Please refer to DEMO.htm file for details and usage
//
// --------------------------------------------------------------------

// Configuration parameters
// ------------------------
// Measure unit in pixel (px) or points (pt)
// measureUnit = "pt"
measureUnit = "px"

// Minimum size allowed for SIZE attribute (like in <FONT SIZE="1"> )
minSize = 1;

// Minimum size allowed for STYLE attribute (like in <FONT STYLE="font-size: 10px"> )
minStyleSize = 10;

// Maximum size allowed for SIZE attribute
maxSize = 6;

// Maximum size allowed for STYLE attribute
maxStyleSize = 30;

// Start size for tags with no SIZE attribute defined
startSize = 1;

// Start size for tags with no font-size STYLE or CLASS attribute defined
startStyleSize = 14;

// Increasing and decreasing step
stepSize = 1;

// Increasing step for STYLE definition (measure previously declared will be used)
stepStyleSize = 2;

// To set your own hotkeys, use key generator tool page included
// Keys to zooming in (with and without CAPS lock). Default: "+"
var keyin = 61;
var keyinCAPS = 43;

// Keys to zooming out (with and without CAPS lock). Default: "-"
var keyout = 45;
var keyoutCAPS = 95;

// Keys for "hard" zooming in (with and without CAPS lock). Default: ">"
var keyinIe = 46;
var keyinIeCAPS = 62;

// Keys for "hard" zooming out (with and without CAPS lock). Default: "<"
var keyoutIe = 44;
var keyoutIeCAPS = 60;

// "Hard" zoom factor
var zoomFactor = 1.1;

// Max zoom allowed
var maxZoom = 4.096;

// Min zoom allowed
var minZoom = 0.625;

// Initial decrease zoom
var startDecZoom = 0.7;

// Initial increase zoom
var startIncZoom = 1.3;

// Cookie expiry (default one year, actually 365 days)
// 365 days in a year
// 24 hours in a day
// 60 minutes in an hour
// 60 seconds in a minute
// 1000 milliseconds in a second
userExpiry = 365 * 24 * 60 * 60 * 1000;

// Enable or disable alert messages
alertEnabled = false;

// Allow input fields resize (text, buttons, and so on)
allowInputResize = false;

// End of configuration parameters. Please do not edit below this line
// --------------------------------------------------------------------------------

// Input values:
// name - name of the cookie
// value - value of the cookie
// [expires] - expiration date of the cookie (defaults to end of current session)
// [path] - path for which the cookie is valid (defaults to path of calling document)
// [domain] - domain for which the cookie is valid (defaults to domain of calling document)
// [secure] - Boolean value indicating if the cookie transmission requires a secure transmission
// * an argument defaults when it is assigned null as a placeholder
// * a null placeholder is not required for trailing omitted arguments
function setCookie(name, value, expires, path, domain, secure) {
  return;
  // Check whether cookies enabled
  document.cookie = "Enabled=true";
  var cookieValid = document.cookie;

  // if retrieving the VALUE we just set actually works
  // then we know cookies enabled
  if (cookieValid.indexOf("Enabled=true") != -1) {
    var curCookie = name + "=" + escape(value) +
        ((expires) ? "; expires=" + expires.toGMTString() : "") +
        ((path) ? "; path=" + path : "") +
        ((domain) ? "; domain=" + domain : "") +
        ((secure) ? "; secure" : "");

    document.cookie = curCookie;
    return(true);
  }
  else {
    return(false);
  }
}

// Input value:
// name - name of the desired cookie
// * return string containing value of specified cookie or null if cookie does not exist
function getCookie(name) {
  var dc = document.cookie;
  var prefix = name + "=";
  var begin = dc.indexOf("; " + prefix);
  if (begin == -1) {
    begin = dc.indexOf(prefix);
    if (begin != 0) return null;
  } else
    begin += 2;
  var end = document.cookie.indexOf(";", begin);
  if (end == -1)
    end = dc.length;
  return unescape(dc.substring(begin + prefix.length, end));
}

// Input values:
// name - name of the cookie
// [path] - path of the cookie (must be same as path used to create cookie)
// [domain] - domain of the cookie (must be same as domain used to create cookie)
// * path and domain default if assigned null or omitted if no explicit argument proceeds
function deleteCookie(name, path, domain) {
  if (getCookie(name)) {
    document.cookie = name + "=" + 
    ((path) ? "; path=" + path : "") +
    ((domain) ? "; domain=" + domain : "") +
    "; expires=Thu, 01-Jan-70 00:00:01 GMT";
  }
}

// Input value:
// date - any instance of the Date object
// * hand all instances of the Date object to this function for "repairs"
function fixDate(date) {
  var base = new Date(0);
  var skew = base.getTime();
  if (skew > 0)
    date.setTime(date.getTime() - skew);
}

function searchTags(childTree, level) {
  var retArray = new Array();
  var tmpArray = new Array();
  var j = 0;
  var childName = "";
  for (var i=0; i<childTree.length; i++) {
    childName = childTree[i].nodeName;
    if (childTree[i].hasChildNodes()) {
      if ((childTree[i].childNodes.length == 1) && (childTree[i].childNodes[0].nodeName == "#text"))
        retArray[j++] = childTree[i];
      else {
        tmpArray = searchTags(childTree[i].childNodes, level+1);
        for (var k=0;k<tmpArray.length; k++)
          retArray[j++] = tmpArray[k];
        retArray[j++] = childTree[i];
      }
    }
    else
      retArray[j++] = childTree[i];
  }
  return(retArray);
}

function changeFontSize(stepSize, stepStyleSize, useCookie) {
if(stepSize == 0)
	return;
  if (document.body) {
    var myObj = searchTags(document.body.childNodes, 0);
    var myCookieSize = parseInt(getCookie("incrSize"));
    var myCookieStyleSize = parseInt(getCookie("incrStyleSize"));
    var myStepSize = stepSize;
    var myStepStyleSize = stepStyleSize;

    var now = new Date();

    // Fix the bug in Navigator 2.0, Macintosh
    fixDate(now);

    if (isNaN(myCookieSize)) myCookieSize = 0;
    if (isNaN(myCookieStyleSize)) myCookieStyleSize = 0;

    // For debug purpose only
    // if (!confirm("COOKIE: SIZE ["+myCookieSize+"] STYLESIZE ["+myCookieStyleSize+"]")) return(0);

    // Check valid increment/decrement sizes or useCookie parameter
    if (useCookie) {
      myStepSize = myCookieSize;
      myStepStyleSize = myCookieStyleSize;
    }

    now.setTime(now.getTime() + userExpiry);
    myObjNumChilds = myObj.length;
	var when = false;
    for (i=0; i<myObjNumChilds; i++) {
	  if(!when) {
		if(myObj[i].className && myObj[i].className == "narrow txt")
			when = true;
		else
			continue;
	  }
      myObjName = myObj[i].nodeName;

      // Only some tags will be parsed
      if (myObjName != "#text" && myObjName != "HTML" &&
          myObjName != "HEAD" && myObjName != "TITLE" &&
          myObjName != "STYLE" && myObjName != "SCRIPT" &&
          myObjName != "BR" && myObjName != "TBODY" &&
          myObjName != "#comment" && myObjName != "FORM") {

        // Skip INPUT fields, if required
        if (!allowInputResize && myObjName == "INPUT" || myObjName == "SELECT" || myObjName == "OPTION") continue;

		if(myObj[i].className && myObj[i].className.indexOf("noresize") != -1) continue;
		
        size = parseInt(myObj[i].getAttribute("size"));

        // Internet Explorer uses a different DOM implementation
        if (myObj[i].currentStyle)
          styleSize = parseInt(myObj[i].currentStyle.fontSize);
        else 
          styleSize = parseInt(window.getComputedStyle(myObj[i], null).fontSize);

        // For debug purpose only. Note: can be very annoying
        // if (!confirm("TAG ["+myObjName+"] SIZE ["+size+"] STYLESIZE ["+styleSize+"]")) return(0);

        if (isNaN(size) || (size < minSize) || (size > maxSize))
          size = startSize;

        if (isNaN(styleSize) || (styleSize < minStyleSize) || (styleSize > maxStyleSize))
          styleSize = startStyleSize;

        if ( ((size > minSize) && (size < maxSize)) || 
             ((size == minSize) && (stepSize > 0)) || 
             ((size == maxSize) && (stepSize < 0)) || useCookie) {
          myObj[i].setAttribute("size", size+myStepSize);
        }

        if ( ((styleSize > minStyleSize) && (styleSize < maxStyleSize)) || 
             ((styleSize == minStyleSize) && (stepStyleSize > 0)) ||
             ((styleSize == maxStyleSize) && (stepStyleSize < 0)) || useCookie) {
          newStyleSize = styleSize+myStepStyleSize;
          myObj[i].style.fontSize = newStyleSize+measureUnit;
        }
      } // End if condition ("only some tags")
    } // End main for cycle

    // Set the cookies
    if (!useCookie) {
      cookieIsSet = setCookie("incrSize", myStepSize+myCookieSize, now);
      cookieIsSet = setCookie("incrStyleSize", myStepStyleSize+myCookieStyleSize, now);
      if (alertEnabled && !cookieIsSet) {
        alert("Per mantenere in memoria la dimensione scelta, abilita i cookie nel browser");
      }
    }

  } // End if condition ("document.body exists")
} // End function declaration

function increaseFontSize() {
  if (document.body) {
    changeFontSize(stepSize, stepStyleSize, false);
	calctut.fontPlus();
  }
  else {
    if (alertEnabled) {
      alert("Spiacente, il tuo browser non supporta questa funzione");
    }
  }
}

function decreaseFontSize() {
  if (document.body) {
    myStepSize = -stepSize;
    myStepStyleSize = -stepStyleSize;
    changeFontSize(myStepSize, myStepStyleSize, false);
	calctut.fontMinus();
  }
  else {
    if (alertEnabled) {
      alert("Spiacente, il tuo browser non supporta questa funzione");
    }
  }
}

function zoomin() {
  if (window.parent.document.body.style.zoom < maxZoom) {
    if (window.parent.document.body.style.zoom > 0) {
      window.parent.document.body.style.zoom *= zoomFactor; 
    }
    else { 
      window.parent.document.body.style.zoom = startIncZoom;
    }
  }
  else {
    if (alertEnabled) {
      alert("Warning: Max size reached");
    }
  }
}

function zoomout() {
  if ( (window.parent.document.body.style.zoom > minZoom) ||
       (window.parent.document.body.style.zoom == 0) ) {
    if (window.parent.document.body.style.zoom > 0) {
      window.parent.document.body.style.zoom /= zoomFactor; 
    }
    else {
      window.parent.document.body.style.zoom = startDecZoom;
    }
  }
  else {
    if (alertEnabled) {
      alert("Warning: Min size reached");
    }
  }
}

function checkzoom(e) {

  if (document.all) {
    myEvent = event.keyCode;
  }
  else {
    myEvent = e.which;
  }

  switch(myEvent) {
    case keyinIe:
    case keyinIeCAPS:
      zoomin();
      break;

    case keyoutIe:
    case keyoutIeCAPS:
      zoomout();
      break;

    case keyin:
    case keyinCAPS:
      increaseFontSize();
      break;

    case keyout:
    case keyoutCAPS:
      decreaseFontSize();
      break;

    default:
      break;
  }
}

if (document.layers) {
  document.captureEvents(Event.KEYPRESS);
}

document.onkeypress = checkzoom;
