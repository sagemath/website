/*
 * JavaScript Code for displaying Sage developers on a Google Map.
 * Author: Harald Schilly, 2014
 * License: Apache 2.0
 */

var markerClusterer = null;
var map = null;
var imageUrl = "pix/developer_map/sagepin.png";
var contributors_xml  = "res/contributors.xml";
var contributors = null;
var geocode_xml       = "res/geocode.xml";
var geocode = null;
var devmap = null; // the map dom element;
var map_aspect        = 1.6; // height = width / map_aspect;
var map_max_width     = 800; // max width of map;
var overlay_max_width = null; //this is the width of the overlay div to restrict too wide layouts
var dx_base           = parseFloat("2"); // disturbance in degrees (=dy)
var zoom_level        = 3;    //holds current zoom level, for jitter
var tracSearch        = "http://trac.sagemath.org/sage_trac/search?q=";
var markers = [];
var points = [];
var cld = null;
var infoWindow = new google.maps.InfoWindow({});

var markerImage = {
    url: imageUrl,
    size: new google.maps.Size(32, 32),
    anchor: new google.maps.Point(16, 16)
};

var mapOptions = {
 scaleControl: true,
 zoomControl: true,
 panControl: true,
 overviewMapControl: true,
 overviewMapControlOptions:{opened:true},
 zoom: 2,
 center: new google.maps.LatLng(39.91, 116.38),
 mapTypeId: google.maps.MapTypeId.ROADMAP
};

function getPointFromLoc(loc) {
  if (loc == null) return null;
  for (var i=0; i<geocode.length; i++) {
    var l = geocode[i];
    if (l.getAttribute("location") == loc) {
      // console.log("Coords: " + l.getAttribute("loclat"), l.getAttribute("loclng"));
      return new google.maps.LatLng(l.getAttribute("loclat"), l.getAttribute("loclng"));
    }
  }
  console.log("Location: " + loc + " not found in geocode.xml!");
  return null;
}

function jitterPoint(point, amount) {
    var dx  = dx_base / (zoom_level * zoom_level);
    var x   = parseFloat(point.lat()) + parseFloat(amount) * 0.995 * Math.cos(parseFloat(point.lat())) * ( 2 * dx * Math.random() - dx );
    var y   = parseFloat(point.lng()) + parseFloat(amount) * ( 2 * dx * Math.random() - dx );
    var ret = new google.maps.LatLng(x,y);
    return ret;
}

// search url for contributions
function getTracLink(trac) {
   return "<a class='trac' href='" + tracSearch + trac + "'>search contributions</a>";
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


// builds the cloud of names below the map
function addDevCloud(dev, loc, point, marker, work, descr, url, pix, size, trac) {
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
      $(spn).click(function() {
        if (map.getZoom() < 5) {map.setZoom(5);}
        infoWindow.setContent(getInfoText(dev,loc,work,descr,url,pix,trac));
        infoWindow.open(map, marker);
      });
    } else {
      spn.removeAttribute("class");
    }
    cld.appendChild(spn);
}



function pinMarker(dev,loc,point,work,descr,url,pix,trac) {
  if (loc == null || point == null) { return null; }
  return pinToPoint(point,dev,loc,work,descr,url,pix,trac);
}


function pinToPoint(point,dev,loc,work,descr,url,pix,trac) {
   var marker = new google.maps.Marker({
       position: point,
       draggable: false,
       icon: markerImage
   });

    marker.title = dev;
    //map.addOverlay(marker);
    //GLog.write("marker point = lat: " + marker.getPoint().lat() + " lng: " + marker.getPoint().lng())
    google.maps.event.addListener(marker, "click", function() {
        //map.openInfoWindowHtml(point, getInfoText(dev,loc,work,descr,url,pix,trac));
        infoWindow.setContent(getInfoText(dev,loc,work,descr,url,pix,trac));
        infoWindow.open(map, this);
    });
    return marker;
}


function refreshMap() {

  if (markers.length == 0) {
    if (markerClusterer != null) {
       markerClusterer.clearMarkers();
       }


    for (var i = 0; i < contribs.length; i++) {
          var dev   = contribs[i].getAttribute("name");
          var loc   = contribs[i].getAttribute("location");
          var work  = contribs[i].getAttribute("work");
          var descr = contribs[i].getAttribute("description");
          var url   = contribs[i].getAttribute("url");
          var pix   = contribs[i].getAttribute("pix");
          var size  = contribs[i].getAttribute("size");
          var jitter= contribs[i].getAttribute("jitter");
          var trac  = contribs[i].getAttribute("trac");
         
          // cache to avoid render errors
          //if (pix != null) {new Image().src = pix;}
         
          if (jitter == null) { jitter = 1; }
          if (trac == null) {trac = dev; }; //  else {trac = trac + " " + dev;}
           
          // and to table
          var point     = null;
          var pointOrig = getPointFromLoc(loc);
          if (pointOrig != null) {
            point = jitterPoint(pointOrig, jitter);
          }
          var m = pinMarker(dev,loc,point,work,descr,url,pix,trac);
          addDevCloud(dev,loc,point,m,work,descr,url,pix,size,trac);
          if (m != null) {
             markers.push(m);
             points.push(pointOrig);
          }
      }

      markerClusterer = new MarkerClusterer(map, markers, {
        //maxZoom: zoom,
        gridSize: 20,
        imagePath: 'pix/developer_map/m',
        //styles: styles[style]
      });

    } else { // never hit until now, see caching info above
        for (var i = 0; i < markers.length; i++) {
          markers[i].setPoint(jitterPoint(points[i], 1));
        }
        markerClusterer.redraw();
    }




  //var zoom = parseInt(document.getElementById('zoom').value, 10);
  //var size = parseInt(document.getElementById('size').value, 10);
  //var style = parseInt(document.getElementById('style').value, 10);
  //zoom = zoom == -1 ? null : zoom;
  //size = size == -1 ? null : size;
  //style = style == -1 ? null: style;

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

function initMap() {
  cld = document.getElementById("devcloud");
  adaptMapSize();
  map = new google.maps.Map(devmap, mapOptions);

  zoomTo("ALL");

   //on zoom, recalc disturbance factor and redraw
   google.maps.event.addDomListener(map, "zoomend", function(oldz,newz) {
        zoom_level = newz;
        refreshMap();
   });

  $.get(geocode_xml, function(data) {
    geocode = data.documentElement.getElementsByTagName("loc");
      $.get(contributors_xml, function(data) {
         contribs = data.documentElement.getElementsByTagName("contributor");
         refreshMap();
      });
  });
}

function clearClusters(e) {
  e.preventDefault();
  e.stopPropagation();
  markerClusterer.clearMarkers();
}

function zoomTo(where) {
    if (where == "USA") {
      map.setCenter(new google.maps.LatLng(37, -93));
      map.setZoom(4);
    } else if (where == "Europe") {
      map.setCenter(new google.maps.LatLng(51, 14));
      map.setZoom(4);
    } else if (where == "UW") {
      map.setCenter(new google.maps.LatLng(47.658345, -122.303017));
      map.setZoom(10);
    } else if (where == "USAW") {
      map.setCenter(new google.maps.LatLng(42,-110));
      map.setZoom(5);
    } else if (where == "USAE") {
      map.setCenter(new google.maps.LatLng(38, -84));
      map.setZoom(5);
    } else if (where == "SAM") {
      map.setCenter(new google.maps.LatLng(-25, -75));
      map.setZoom(3);
    } else if (where == "Africa") {
      map.setCenter(new google.maps.LatLng(3, 35));
      map.setZoom(3);
    } else if (where == "Asia") {
      map.setCenter(new google.maps.LatLng(38, 90));
      map.setZoom(3);
    } else if (where == "Australia") {
      map.setCenter(new google.maps.LatLng(-32, 145));
      map.setZoom(3);
    } else { // ALL
      map.setCenter(new google.maps.LatLng(20, 15));
      map.setZoom(2);
    }
    return false;
}


$(initMap);
