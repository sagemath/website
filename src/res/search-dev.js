/*
 * Google Powered Search for Sage (www.sagemath.org)
 * (C) 2008, Harald Schilly, ALL RIGHTS RESERVED
 */

google.load("search", "1", {"nooldnames" : true, "language" : "en"});
var searchID = "017384562579735769466:tzjtyn4wync";

var searchControl = null;
var nresults = 0;

SageSearch.prototype.OnStart = function(sc, searcher, query) {
//pageTracker._trackPageview('/SEARCH-DEV/' + query);
nresults = 0;
}

SageSearch.prototype.OnComplete = function(sc, searcher) {
var stats = document.getElementById("searchstats");
if ( searcher.results && searcher.results.length > 0) {
nresults += searcher.results.length;
stats.innerHTML = "Google found " + nresults + "  results for you!";

//var options = new google.search.SearcherOptions();
//searchControl.addSearcher(searcher, options);
//alert(searcher.title);
searcher.setUserDefinedClassSuffix("result");

} else if (nresults == 0) {
stats.innerHTML = "Google found nothing :(";
} 
}

var sageSearch;
function OnLoad() {
var urlQuery = window.location.search.split('?')[1];
sageSearch = new SageSearch(urlQuery);
}


function SageSearch(urlQuery) {
// Create a search control
searchControl = new google.search.SearchControl();
searchControl.setOnKeepCallback(this, SaveSearch, "temporarily pin result on the page");
searchControl.setSearchStartingCallback(this, SageSearch.prototype.OnStart);
searchControl.setSearchCompleteCallback(this, SageSearch.prototype.OnComplete);

//pairs of Title/Refinement Key
var labels = [
["Python","python"],
["Cython","cython"],
["Maxima","maxima"],
["Pari","pari"],
["GAP","gap"],
["GMP","gmp"],
["linbox","linbox"],
["matplotlib","matplotlib"],
["NTL","ntl"],
["NumSciPy","scipy"],
["polybori","polybori"],
["Singular","singular"],
["sympy","sympy"],
["MMA", "mathematica"],
["Magma","magma"],
["Matlab","matlab"]
];

for(var i=0; i<labels.length; i++) {
var title = labels[i][0];
var key   = labels[i][1];

var options = new google.search.SearcherOptions();
var search = new google.search.WebSearch();
search.setUserDefinedLabel(title);
search.setLinkTarget(google.search.Search.LINK_TARGET_BLANK);
search.setSiteRestriction(searchID,key);
searchControl.addSearcher(search, options);
search.setResultSetSize(google.search.Search.LARGE_RESULTSET);
}

var drawOptions = new google.search.DrawOptions();
drawOptions.setSearchFormRoot(document.getElementById("googlesearchform"));
drawOptions.setDrawMode(google.search.SearchControl.DRAW_MODE_TABBED);

// Tell the searcher to draw itself and tell it where to attach
searchControl.draw(document.getElementById("searchdevel"), drawOptions);

// Execute an inital search
if (urlQuery != null) searchControl.execute(urlQuery.split("=")[1]);
}


function SaveSearch(result) {
var node = result.html.cloneNode(true);

// attach it
var savedResults = document.getElementById("savedsearch");
savedResults.appendChild(node);
}

google.setOnLoadCallback(OnLoad);


