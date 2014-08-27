/*
 * JavaScript Code for displaying Sage developers on a Google Map.
 * Author: Harald Schilly
 * Created: 2008-04-02
 * (C) ALL RIGHTS RESERVED
 */

var map     = null;//the map, GMap2
var mgr     = null;//marker manager
//var geocoder = null;
var contributors_xml  = "./res/contributors.xml";
var geocode_xml       = "./res/geocode.xml";
var geocode           = null; //xml dom thing
var map_aspect        = 1.6; // height = width / map_aspect;
var map_max_width     = 800; // max width of map;
var overlay_max_width = null; //this is the width of the overlay div to restrict too wide layouts
var dx_base           = parseFloat("2"); // disturbance in degrees (=dy)
var zoom_level        = 3;    //holds current zoom level, for jitter
var contribs          = null; //array of contributors, processed
var devmap            = null; //dom element
var markers           = [];   //possible cache, but doesn't work, see below
var points            = [];   //same
var sagepinwww        = "./pix/sagepin.png";
var sagepin       = null;
var markerOptions     = null;
var tracSearch        = "http://trac.sagemath.org/sage_trac/search?q=";

function jitterPoint(point, amount) {
    var dx  = dx_base / (zoom_level * zoom_level);
    var x   = parseFloat(point.lat()) + parseFloat(amount) * 0.995 * Math.cos(parseFloat(point.lat())) * ( 2 * dx * Math.random() - dx );
    var y   = parseFloat(point.lng()) + parseFloat(amount) * ( 2 * dx * Math.random() - dx );
    var ret = new google.maps.LatLng(x,y);
    return ret;
}

// z-index overlay of markers
function orderOfCreation(marker,b) {return 1;}

// search url for contributions
function getTracLink(trac) {
   return "<a class='trac' target='_blank' href='" + tracSearch + trac + "'>search contributions</a>";
}

// clear contents (it is invoked on zoom for adapted jitter of points!)
function clearContents() {
    /*
    var devlist  = document.getElementById("devlist");
    var devlistp = devlist.parentNode;
    devlistp.removeChild(devlist);
    devlist = document.createElement("tbody");
    devlist.setAttribute("id", "devlist");
    devlistp.appendChild(devlist);
    */

    var cld  = document.getElementById("devcloud");
    var cldp = document.getElementById("devcloudp");
    cldp.removeChild(cld);
    cld = document.createElement("div");
    cld.setAttribute("id", "devcloud");
    cldp.appendChild(cld);
}

function scrollToElement(el){
  var xpos = 0;
  var ypos = 0;
  while(el != null){
    xpos += el.offsetLeft;
    ypos += el.offsetTop;
    el = el.offsetParent;
  }
 window.scrollTo(xpos,ypos);
}

var notFirstNameInCloud = false;
// builds the cloud of names below the map
function addDevCloud(dev, loc, point, work, descr, url, pix, size, trac) {
    var cld = document.getElementById("devcloud");
    //if(notFirstNameInCloud) {
    //  cld.appendChild(document.createTextNode(", "));
    //} else {    
    //  notFirstNameInCloud = true;
    //}
    cld.appendChild(document.createTextNode(" "));
    var spn = document.createElement("span");
    spn.setAttribute("class", "highlight");
    var style = "";
    if (size != null) {
      style += "font-size:"+size+"%;";
    }
    spn.setAttribute("style", style);
    spn.appendChild(document.createTextNode(dev));

    if(point != null) { //only those who have locations
      //spn.setAttribute("class", "border");
      GEvent.addDomListener(spn,"click",function() {
        //map.zoomIn();
        if (map.getZoom() < 5) {map.setZoom(5);}
        map.openInfoWindowHtml(point, getInfoText(dev,loc,work,descr,url,pix,trac));
        //GLog.write("clicked on span element: " + getInfoText(dev,loc,work,descr,url,pix,trac));
      });
    } else {
      spn.removeAttribute("class");
      //GEvent.addDomListener(spn, "click", function() {
      //window.alert("sorry, location unknown.");
      //});
    }
    /*
    GEvent.addDomListener(spn,"mouseover", function() {
      this.setAttribute("class","highlight");
    });
    GEvent.addDomListener(spn,"mouseout", function() {
      this.setAttribute("class","");
    });
*/
    cld.appendChild(spn);
}

// rebuilds the table of names with links to the map
function addDevTable(dev, loc, point, work, descr, url, pix, trac) {
    var tr = document.createElement("tr");
    tr.setAttribute("class", "highlight");
    var td = document.createElement("td");
    if (url == null) {
      td.appendChild(document.createTextNode(dev));
    } else {
      var a = document.createElement("a");
      a.setAttribute("href", url);
      a.appendChild(document.createTextNode(dev));
      td.appendChild(a);
    }
    td.setAttribute("class", "name");
    tr.appendChild(td);
    var td = document.createElement("td");
    if (work != null) {
      td.appendChild(document.createTextNode(work));
    }
    tr.appendChild(td);
    var td = document.createElement("td");
    if (loc != null) {
      td.appendChild(document.createTextNode(loc));
    }
    tr.appendChild(td);
    var td = document.createElement("td");
    var descrOld = descr;
    if (descr != null) {
        descr = descr.replace(/; /g, "<br />");//eat space if there
        descr = descr.replace(/;/g , "<br />");
        td.innerHTML = descr + "<br/>";
    }
    td.innerHTML = td.innerHTML + getTracLink(trac);
    //td.appendChild(document.createTextNode(descr));
    td.setAttribute("class", "description");
    tr.appendChild(td);
    if (point != null) {
      // event handler on click, mouseover, mouseout
/*
      GEvent.addDomListener(tr, 'mouseover', function(){
        this.setAttribute('class', 'highlight');
      });
      GEvent.addDomListener(tr, 'mouseout', function(){
        this.setAttribute('class', '');
      });
*/
      GEvent.addDomListener(tr,"click",function() {
        if (map.getZoom() < 5) {map.setZoom(5);}
        map.openInfoWindowHtml(point, getInfoText(dev,loc,work,descrOld,url,pix,trac));
        scrollToElement(document.getElementById("mapzoom"));
        //GLog.write("clicked on tr element: " + getInfoText(dev,loc,work,descr,url,pix,trac));
      });
    }
    var devlist = document.getElementById("devlist");
    devlist.appendChild(tr);
}

// this ends up inside the InfoWindow
function getInfoText(dev,loc,work,descr,url,pix,trac) {
  var txt = "";
  if (pix != null) {
    txt += "<img src='"+pix+"' align='left' vspace='5' hspace='5' alt='"+dev+"'/>";
    //GLog.write("added pix = " + pix);
  }
  txt += "<div class='mOverlay' style='max-width:"+overlay_max_width+"px'>";
  if (url != null) {
    txt += "<a class='mname' target='_blank' ref='external' href='"+url+"'>"+dev+"</a><br/>";
  } else {
    txt += "<span class='mname'>"+dev+"</span><br/>"
  }
  if (work  != null) {txt += "<span class='mwork'>" + work + "</span><br/>";}
  if (loc   != null) {txt += "<span class='mloc'>" + loc + "</span><br clear='all'/>";}
  if (descr != null) {
      if (descr.indexOf(";") >= 0) { //we have a ";"
        descr = descr.replace(/; /g, "</li><li>");//eat space if there
        descr = descr.replace(/;/g , "</li><li>");
      }
      descr = "<ul><li>" + descr + "</li></ul>";//always a list is prettier
      txt += "<div class='mdesc'>"+ descr+"</div>";
  }
  txt += getTracLink(trac);
  txt += "</div>";
  return txt;
}

function pinToPoint(point,dev,loc,work,descr,url,pix,trac) {
  if (!point) {
    google.maps.Log.write("pinToPoint: point was null");
  } else {
    var marker = new google.maps.Marker(point, markerOptions);
    marker.title = dev;
    //map.addOverlay(marker);
    //GLog.write("marker point = lat: " + marker.getPoint().lat() + " lng: " + marker.getPoint().lng())
    google.maps.event.addListener(marker, "click", function() {
      map.openInfoWindowHtml(point, getInfoText(dev,loc,work,descr,url,pix,trac));
    });
    return marker;
  }
}

function getPointFromLoc(loc) {
  for (var i=0; i<geocode.length; i++) {
    l = geocode[i];
    if (l.getAttribute("location") == loc) {
      //GLog.write("Coords: " + l.getAttribute("loclat"), l.getAttribute("loclng"));
      return new google.maps.LatLng(l.getAttribute("loclat"), l.getAttribute("loclng"));
    }
  }
  //GLog.write("Locaton: " + loc + " not found in geocode.xml!");
  return null;
}

function pinMarker(dev,loc,point,work,descr,url,pix,trac) {
  if (loc == null || point == null) {
    //GLog.write(dev + " has no location specified");
  } else {
    return pinToPoint(point,dev,loc,work,descr,url,pix,trac);
  }
}

function draw_population() {
    //this would be ready for caching points,
    //but doesn't work, because we need to relocate the popup
    //windows, too. Unless someone has an idea, this is deactivated...
    markers = [];
    points  = [];
    if (markers.length == 0) {
        //map.clearOverlays(); 
        map.overlayMapTypes.setAt( 0, null);
        clearContents();
        mgr.clearMarkers();

        //GLog.write("markers.length = " + markers.length);

        for (var i = 0; i < contribs.length; i++) {
        //for (var i = 0; i < 15; i++) {
          var dev   = contribs[i].getAttribute("name");
          var loc   = contribs[i].getAttribute("location");
          var work  = contribs[i].getAttribute("work");
          var descr = contribs[i].getAttribute("description");
          var url   = contribs[i].getAttribute("url");
          var pix   = contribs[i].getAttribute("pix");
          var size  = contribs[i].getAttribute("size");
    var jitter= contribs[i].getAttribute("jitter");
          var trac  = contribs[i].getAttribute("trac");
         
          //GLog.write("current: " + dev + ", " + loc + ", " + work + ", " + pix); 

          // cache to avoid render errors
          if (pix != null) {new Image().src = pix;}
         
    if (jitter == null) { jitter = 1; }
          if (trac == null) {trac = dev; }; //  else {trac = trac + " " + dev;}
           
          // and to table
          var point     = null;
          var pointOrig = getPointFromLoc(loc);
          if (pointOrig != null) {
            point = jitterPoint(pointOrig, jitter);
          }
          //addDevTable(dev,loc,point,work,descr,url,pix,trac);
          addDevCloud(dev,loc,point,work,descr,url,pix,size,trac);
          var m = pinMarker(dev,loc,point,work,descr,url,pix,trac);
          if (m != null) { 
              markers.push(m);
              points.push(pointOrig);
          }
        }
        mgr.addMarkers(markers, 1);
    } else { // never hit until now, see caching info above
        for (var i = 0; i < markers.length; i++) {
          markers[i].setPoint(jitterPoint(points[i], 1));
        }
    }
    if (map.getZoom() > 16) { map.setZoom(16); }
    mgr.refresh();

    
    //GLog.write("markers.length = " + markers.length + " -- marker manager count= " + mgr.getMarkerCount(zoom_level));
}

// our population of Sage developers
function population() {
  downloadUrl(contributors_xml, function(data) {
    //var xml = google.maps.Xml.parse(data);
    contribs = data.documentElement.getElementsByTagName("contributor");
    draw_population();
  });
}

function zoomTo(where) {
    if (where == "USA") {
      map.setCenter(new google.maps.LatLng(37, -93), 4);
    } else if (where == "Europe") {
      map.setCenter(new google.maps.LatLng(51, 14), 4);
    } else if (where == "UW") {
      map.setCenter(new google.maps.LatLng(47.658345, -122.303017),12);
    } else if (where == "USAW") {
      map.setCenter(new google.maps.LatLng(42,-110), 5);
    } else if (where == "USAE") {
      map.setCenter(new google.maps.LatLng(38, -84), 5);
    } else if (where == "SAM") {
      map.setCenter(new google.maps.LatLng(-25, -75), 3);
    } else if (where == "Africa") {
      map.setCenter(new google.maps.LatLng(3, 35) , 3); 
    } else if (where == "Asia") {
      map.setCenter(new google.maps.LatLng(38, 90) , 3); 
    } else if (where == "Australia") {
      map.setCenter(new google.maps.LatLng(-32, 145),3);
    } else { // ALL
      map.setCenter(new google.maps.LatLng(20, 15), 2);
    }
    return false;
}


function adaptMapSize() {
    var devlist   = document.getElementById("devlist");
    var mapwidth  = Math.min(devlist.offsetWidth, map_max_width);
    //GLog.write("mapwidth = " + mapwidth);
    //var mapwidth  = document.body.clientWidth*0.9;
    var mapheight = mapwidth/map_aspect;
    devmap        = document.getElementById("devmap");
    // devmap.setAttribute("style","width: "+Math.floor(mapwidth)+"px; height: "+Math.floor(mapheight)+"px");
    devmap.setAttribute("style","width: 100%; height: "+Math.floor(mapheight)+"px");
    //GLog.write("clientWidth = " +document.body.clientWidth+ " / width = " + Math.floor(mapwidth));
    overlay_max_width = Math.floor(mapwidth/3);
}

function load() {

  //if (GBrowserIsCompatible()) {
    adaptMapSize();

    var mapOptions = {
       scaleControl: true,
       zoomControl: true,
       panControl: true,
       overviewMapControl: true,
       overviewMapControlOptions:{opened:true},
       mapTypeId: google.maps.MapTypeId.ROADMAP
    };
    //map.addControl(new google.maps.MapTypeControl());
    //map.addControl(new google.maps.LargeMapControl());
    //map.enableDoubleClickZoom();
    //map.enableContinuousZoom();
    //map.enableGoogleBar();
    //map.enableScrollWheelZoom();

    map = new google.maps.Map(devmap, mapOptions);
    zoomTo("ALL");

    mgr = new MarkerManager(map);

    // pin icon
    sagepin = new google.maps.MarkerImage(sagepinwww,
                 new google.maps.Size(27,27),
                 new google.maps.Point(14,14),
                 new google.maps.Point(14,14));
    markerOptions = { icon:sagepin, zIndexProcess:orderOfCreation };
    
    //on zoom, recalc disturbance factor and redraw
    google.maps.event.addDomListener(map, "zoomend", function(oldz,newz) {
        zoom_level = newz;
        draw_population();
    });

    if (geocode == null) {
      downloadUrl(geocode_xml, function(data) {
        //var xmldata = google.maps.Xml.parse(data);
        geocode = data.documentElement.getElementsByTagName("loc");
        population();
      });
    }

    // resize is most complicated: new map, since check resize
    // doesn't work! then do everything again, new markers
    // on new map, but we already know the geocodes (see above)!
    //GEvent.addDomListener(window, "resize", function() {
    //    //GLog.write("captured resize event");
    //    if (map != null && contribs != null) {
    //      markers = [];
    //      points  = [];
    //      load();
    //      if(geocode != null) {draw_population(); }
    //    }
    //});

    return true; // end here
  //}
  //var d = document.getElementById("devmap");
  //d.innerHTML = "YOUR BROWSER IS NOT SUPPORTED :(";
}
