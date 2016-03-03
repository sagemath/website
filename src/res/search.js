/*
 * Google Powered Search for Sage (www.sagemath.org)
 * (C) 2008--2016, Harald Schilly, Apache 2.0
 */

"use strict";

google.load("search", "1", {"nooldnames" : true, "language" : "en"});
var searchID = "017384562579735769466:s27byrlaffu";

var nresults = 0;
SageSearch.prototype.OnStart = function(sc, searcher, query) {
//pageTracker._trackPageview('/SEARCH/' + query);
nresults = 0;
}

SageSearch.prototype.OnComplete = function(sc, searcher) {
var stats = document.getElementById("searchstats");
if ( searcher.results && searcher.results.length > 0) {
nresults += searcher.results.length;
stats.innerHTML = "Google found " + nresults + "  results for you!";
} else if (nresults == 0) {
stats.innerHTML = "Still searching or no results found ...";
}
}

var sageSearch;
function OnLoad() {
var urlQuery = window.location.search.split('?')[1];
sageSearch = new SageSearch(urlQuery);
}

/*
google.setOnLoadCallback(function() {
  var customSearchOptions = {};
  var customSearchControl =   new google.search.CustomSearchControl(searchID, customSearchOptions);
  customSearchControl.setResultSetSize(google.search.Search.FILTERED_CSE_RESULTSET);
  var options = new google.search.DrawOptions();
  options.setAutoComplete(true);
  customSearchControl.draw('cse', options);
}, true);
*/

var searchControl = null;

function SageSearch(urlQuery) {
// Create a search control
searchControl = new google.search.SearchControl();
searchControl.setOnKeepCallback(this, SaveSearch, "temporarily pin result on the page");
searchControl.setSearchStartingCallback(this, SageSearch.prototype.OnStart);
searchControl.setSearchCompleteCallback(this, SageSearch.prototype.OnComplete);

var options = new google.search.SearcherOptions();
options.setExpandMode(google.search.SearchControl.EXPAND_MODE_OPEN);
options.setRoot(document.getElementById("searchuser"));
var siteSearch = new google.search.WebSearch();
siteSearch.setUserDefinedLabel("User Help and Support");
siteSearch.setLinkTarget(google.search.Search.LINK_TARGET_BLANK);
siteSearch.setSiteRestriction(searchID, "user");
searchControl.addSearcher(siteSearch, options);
siteSearch.setResultSetSize(google.search.Search.LARGE_RESULTSET);

var options = new google.search.SearcherOptions();
options.setExpandMode(google.search.SearchControl.EXPAND_MODE_OPEN);
options.setRoot(document.getElementById("searchdoc"));
var siteSearch = new google.search.WebSearch();
siteSearch.setUserDefinedLabel("Documentation");
siteSearch.setSiteRestriction(searchID, "doc");
searchControl.addSearcher(siteSearch, options);
siteSearch.setResultSetSize(google.search.Search.LARGE_RESULTSET);

var options = new google.search.SearcherOptions();
options.setExpandMode(google.search.SearchControl.EXPAND_MODE_OPEN);
options.setRoot(document.getElementById("searchgroup"));
var siteSearch = new google.search.WebSearch();
siteSearch.setUserDefinedLabel("Discussion Groups");
siteSearch.setLinkTarget(google.search.Search.LINK_TARGET_BLANK);
siteSearch.setSiteRestriction(searchID, "group");
searchControl.addSearcher(siteSearch, options);

var options = new google.search.SearcherOptions();
options.setExpandMode(google.search.SearchControl.EXPAND_MODE_OPEN);
options.setRoot(document.getElementById("searchpdf"));
var siteSearch = new google.search.WebSearch();
siteSearch.setUserDefinedLabel("PDF Documents");
siteSearch.setSiteRestriction(searchID, "doc");
siteSearch.setLinkTarget(google.search.Search.LINK_TARGET_BLANK);
siteSearch.setQueryAddition("filetype:pdf");
searchControl.addSearcher(siteSearch, options);

var options = new google.search.SearcherOptions();
options.setExpandMode(google.search.SearchControl.EXPAND_MODE_OPEN);
options.setRoot(document.getElementById("searchblog"));
// BlogSearch has no restriction ... :\
// var blogSearch = new google.search.BlogSearch();
var blogSearch = new google.search.WebSearch();
blogSearch.setUserDefinedLabel("Sage Developer Blogs");
blogSearch.setLinkTarget(google.search.Search.LINK_TARGET_BLANK);
//blogSearch.setResultOrder(google.search.Search.ORDER_BY_RELEVANCE);
blogSearch.setSiteRestriction(searchID, "blog");
searchControl.addSearcher(blogSearch, options);

/* no restrictions either
var options = new google.search.SearcherOptions();
options.setExpandMode(google.search.SearchControl.EXPAND_MODE_PARTIAL);
options.setRoot(document.getElementById("searchvideo"));
var videoSearch = new google.search.VideoSearch();
videoSearch.setUserDefinedLabel("Video");
searchControl.addSearcher(videoSearch, options);
*/

var options = new google.search.SearcherOptions();
options.setExpandMode(google.search.SearchControl.EXPAND_MODE_OPEN);
options.setRoot(document.getElementById("searchweb"));
var wwwSearch = new google.search.WebSearch();
wwwSearch.setUserDefinedLabel("World Wide Web");
wwwSearch.setSiteRestriction(searchID);
wwwSearch.setLinkTarget(google.search.Search.LINK_TARGET_BLANK);
searchControl.addSearcher(wwwSearch, options);
// must be after adding? google hello, why?
wwwSearch.setResultSetSize(google.search.Search.LARGE_RESULTSET);

var options = new google.search.SearcherOptions();
options.setExpandMode(google.search.SearchControl.EXPAND_MODE_OPEN);
options.setRoot(document.getElementById("searchdev"));
var devSearch = new google.search.WebSearch();
devSearch.setUserDefinedLabel("Develop & Reference & trac");
devSearch.setSiteRestriction(searchID, "developer");
devSearch.setLinkTarget(google.search.Search.LINK_TARGET_BLANK);
searchControl.addSearcher(devSearch, options);


var drawOptions = new google.search.DrawOptions();
drawOptions.setSearchFormRoot(document.getElementById("googlesearchform"));
//drawOptions.setDrawMode(google.search.SearchControl.DRAW_MODE_TABBED);

// Tell the searcher to draw itself and tell it where to attach
searchControl.draw(document.getElementById("googlesearch"), drawOptions);

// Execute an inital search
if (urlQuery != null) searchControl.execute(urlQuery.split("=").pop());
}


function SaveSearch(result) {
  var node = result.html.cloneNode(true);

  // attach it
  var savedResults = document.getElementById("savedsearch");
  savedResults.appendChild(node);
}

google.setOnLoadCallback(OnLoad);


