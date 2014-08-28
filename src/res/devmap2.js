/*
 * JavaScript Code for displaying Sage developers on a Google Map.
 * Author: Harald Schilly, 2014
 * License: Apache 2.0
 */

var markerClusterer = null;
var map = null;
var imageUrl = "pix/sagepin.png";
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
  for (var i=0; i<geocode.length; i++) {
    var l = geocode[i];
    if (l.getAttribute("location") == loc) {
      console.log("Coords: " + l.getAttribute("loclat"), l.getAttribute("loclng"));
      return new google.maps.LatLng(l.getAttribute("loclat"), l.getAttribute("loclng"));
    }
  }
  console.log("Locaton: " + loc + " not found in geocode.xml!");
  return null;
}

function refreshMap() {
  if (markerClusterer) {
    markerClusterer.clearMarkers();
  }

  var markers = [];

  var markerImage = {
    url: imageUrl,
    size: new google.maps.Size(32, 32),
    anchor: new google.maps.Point(16, 16)
   };

    for (var i = 0; i < contribs.length; i++) {
        //for (var i = 0; i < 15; i++) {
          var dev   = contribs[i].getAttribute("name");
          var loc   = contribs[i].getAttribute("location");
          if (loc == null) { continue; }
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
          //if (pointOrig != null) {
          //  point = jitterPoint(pointOrig, jitter);
          //}
          //addDevCloud(dev,loc,point,work,descr,url,pix,size,trac);
          //var m = pinMarker(dev,loc,point,work,descr,url,pix,trac);
          //if (m != null) { 
           //   markers.push(m);
          //    points.push(pointOrig);
          //}
        //}
        //mgr.addMarkers(markers, 1);
    //} else { // never hit until now, see caching info above
    //    for (var i = 0; i < markers.length; i++) {
    //      markers[i].setPoint(jitterPoint(points[i], 1));
    //    }
    //}

       var latLng = pointOrig;
       var marker = new google.maps.Marker({
           position: latLng,
           draggable: true,
           icon: markerImage
       });

    markers.push(marker);

  }

  //var zoom = parseInt(document.getElementById('zoom').value, 10);
  //var size = parseInt(document.getElementById('size').value, 10);
  //var style = parseInt(document.getElementById('style').value, 10);
  //zoom = zoom == -1 ? null : zoom;
  //size = size == -1 ? null : size;
  //style = style == -1 ? null: style;

  markerClusterer = new MarkerClusterer(map, markers, {
    //maxZoom: zoom,
    //gridSize: size,
    //styles: styles[style]
  });
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
  adaptMapSize();
  map = new google.maps.Map(devmap, mapOptions);

  // var refresh = document.getElementById('refresh');
  // google.maps.event.addDomListener(refresh, 'click', refreshMap);

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

$(initMap);
