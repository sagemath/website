/*
 * demo for an interactive database of Sage example 
 * copyright: Harald Schilly <harald@schil.ly>
 * license: apache 2.0
 */

/* this neat helper comes from stackoverflow and various blogs. it 
 * extracts a certain parameter from a query in the url (GET request) */
function getParameterByName(name) {
  var match = RegExp('[?&]' + name + '=([^&]*)').exec(window.location.search);
  return match ? decodeURIComponent(match[1].replace(/\+/g, ' ')) : null;
}

var mysagecell = {};

/* helper, used twice 
 * TODO is there a way to dynamically replace the content of the codemirror code ? */
function initSageCell(doClick) {
 sagecell.init(function() {
  mysagecell = singlecell.makeSagecell({
   inputLocation: "#sageInput", 
   /* outputLocation: '#sageOutput', */
   replaceOutput: true,
   hide: ["messages", "computationID", "files", "sageMode", "editorToggle", "sessionTitle", "done"],
   evalButtonText: "Evaluate"
  });
 });
}

/* initialize interactive code */
$(function() {

 var c = getParameterByName("code");
 if (c) { $("#sageInput").html(unescape(c)); }

 initSageCell(c);
});

/* contains the 2-level database of examples */
var DB = {}
var DB_subdir = "eval";
var DB_files = Array("db1.json", "db2.json", "eberhart.json", "novoseltsev.json");
var $descr = "";

function updateDescr(html) {
  var c = "";
  if (CAT1) {
    c += "<span style='color: grey;'>" + CAT1;
    if (CAT2) { c+= ">" + CAT2 + "</span><br/>";
      if (html) { c+= html; }
    } else { c+= "</span><br/>"; }
   }
   $descr.html(c);
}

/* initializes the interactive database */
$(function() {
  var cnt = 0;
  var nbex = 0;
  $descr = jQuery("#db-descr");
  var $nbex = jQuery("#nb-examples");
  for (var i in DB_files) {
   jQuery.getJSON(DB_subdir +"/"+ DB_files[i], function(data) {
     jQuery.each(data, function(key, item) {
       var cat = item["cat"];
       if (!(cat[0] in DB)) { DB[cat[0]] = {}; }
       var DB1 = DB[cat[0]];
       if (!(cat[1] in DB1)) { DB1[cat[1]] = {}; }
       DB1[cat[1]][key] = item;;
       nbex++;
     });
   })
   .error(function() { alert("json parser error, most likely …");})
   /* and populate UI when we have all files */
   .success(function() { 
     $nbex.text(nbex);
     cnt++; 
     if (cnt == DB_files.length) { 
      $descr.empty();
      populateLists(jQuery); 
     } else {
      $descr.html("progress: " + ((cnt/DB_files.length)*100.0) + "%");
     }
   });
  }
});

/* selection state vars */
var CAT1 = "";
var CAT2 = "";
var EX   = "";

/* takes a map and returns an array, sorted by map's keys */
function mapsort(m) {
  var ret = [];
  for (var k in m) { ret.push([k, m[k]]); }
  ret.sort(function(a,b) { return a[0] < b[0] ? -1 : ( a[0] > b[0] ? 1 : 0); });
  return ret;
}

/* store the state in the URI, exid is the id of the example - or nothing */
function storeState() {
 // TODO re-enable this once #restoreState() works
 return
 var s = "";
 if (CAT1) {
  s += encodeURI(CAT1);
  if (CAT2) {
   s += "/" + encodeURI(CAT2);
   if (EX) { s += "/" + encodeURI(EX); }
  }
 }
 window.location.hash = s;
}

/* get the state+example after the # in the URI, "/" delmimiter */
function restoreState() {
  var state = window.location.hash.substring(1).split("/") 
  if (state.length >= 0) CAT1 = decodeURI(state[0]);
  if (state.length >= 1) CAT2 = decodeURI(state[1]);
  if (state.length >= 2) {
    EX = decodeURI(state[2]);
    showExample();
  }
  /* TODO menu isn't updated, but that's a bit harder */
}

/* this function actually adds the content to the DB and makes it interactive.
 * it is only called once! jQuery's "on" is used to dispatch all the clicks in 
 * only a few handlers. */
function populateLists($) {
  var $db1 = $("#db1").empty();
  var $db2 = $("#db2").empty();
  var $exs = $("#exs").empty();

  $.each(mapsort(DB), function(idx, item) {
    var key1 = item[0];
    var $li = $("<div>" + key1 + "</div>");
    $li.prop("key", key1);
    $db1.append($li);
  });

  /* topic column logic */
  $("#db1>div").click(function() { 
      $("#db1>div").removeClass("selected");
      $(this).addClass("selected");
      $db2.empty();
      $exs.empty();
      var key1 = $(this).prop("key");
      CAT1 = key1;
      CAT2 = "";
      EX = "";
      //storeState();
      $.each(mapsort(DB[key1]), function(idx, item) {
        var key2 = item[0];
        var $li2 = $("<div>" + key2 + "</div>");
        $li2.prop("key", key2);
        $db2.append($li2);
      });
      //updateDescr();
  });

  /* subtopic column logic, when clicking on a subtopic, it
   * clears the list of examples and adds the matching ones */
  $("#db").on("click", "#db2>div", function(event) {
    $this = $(this);
    $exs.empty();
    $("#db2>div").removeClass("selected");
    $this.addClass("selected");
    CAT2 = $this.prop("key");
    EX = "";
    //storeState();
    $.each(mapsort(DB[CAT1][CAT2]), function(idx, entry) {
      var key = entry[0];
      var item = entry[1];
      var $ex = $("<div>"+key+"</div>");
      $ex.prop("key", key);
      $exs.append($ex);
    });
    //updateDescr();
  });

  /* examples clumn, on click load the code */
  $("#db").on("click", "#exs>div", function(event) {
    $this = $(this);
    $("#exs>div").removeClass("selected");
    $this.addClass("selected");
    EX = $this.prop("key");
    storeState();
    showExample();
  });

  /* this could also be done via the :hover CSS selector, but maybe we want to add some
   * additional UI aides or updates later */
  $("#db").on("mouseover", "#db div>div", function() { $(this).addClass("hover");    });
  $("#db").on("mouseout",  "#db div>div", function() { $(this).removeClass("hover"); });

  restoreState();
}

function showExample() {
  var item = DB[CAT1][CAT2][EX];
  var code = item["code"].join("\n"); // the code is an array of strings
  updateDescr("<strong>" + EX + "</strong>: " + item["descr"]);
  jQuery('.CodeMirror').get(0).CodeMirror.setValue(code);
  //$("input.sagecell_evalButton").click();
  mysagecell.submit();
}
