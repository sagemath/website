var calctut = {
	pages: 	  ["index.html", "limits.html", "continuity.html", "onesided.html", "inflimits.html", "slantasymp.html", "tangent.html", "derivative.html", "differentiability.html", "diffrules.html"],
	titles:   ["Introduction", "Limits", "Continuity", "One-Sided Limits", "Limits at Infinity", "Supplement: Slant Asymptotes", "Tangent Lines", "The Definition of the Derivative", "Differentiability", "Differentiation Rules"],
	id: 	  null,
	index: 	  -1,
	start:	  -1,
	end:	  -1,
	lines:    false,
	fsize:    0,
	twoyears: null,
	redir:    null,
	
	initCalc: function() {
		calctut.pages[-1] = "review.html";
		calctut.titles[-1] = "Review";
		calctut.id = [];
		for(var i = 0; i < calctut.pages.length; i ++) {
			calctut.id[i] = calctut.pages[i].substring(0, calctut.pages[i].lastIndexOf("."));
		}
		if(calctut.index == -1) {
			calctut.refreshIndex();
		}
		calctut.updateTitle();
		calctut.twoyears = new Date();
		calctut.twoyears.setFullYear(calctut.twoyears.getFullYear()+2);
	},
	
	refreshIndex: function() {
		var curpage = location.href.substring(location.href.lastIndexOf("\/")+1);
		for(var i = 0; i < calctut.pages.length; i ++) {
			if(curpage == calctut.pages[i]) {
			   calctut.index = i;
			}
		}
	},
	
	updateTitle: function() {
		document.title = "Sage Calculus Tutorial - "+calctut.titles[calctut.index];
	},
	
	pageLoad: function() {
		calctut.checkCookie();
		calctut.writeCookieLastVisited();
		calctut.updateLineNumbers();
		if(calctut.fsize && calctut.fsize !== 0) {
			var sign = Math.abs(calctut.fsize)/calctut.fsize;
			for(var i = 0; i < Math.abs(calctut.fsize); i ++) {
				changeFontSize(sign, sign*2, false);
			}
		}
		calctut.goToCurrentNav();
		calctut.hideExplanations();
		calctut.populateDropdown();
	},
	
	checkCookie: function() {
		var namestart, nameend;
		var arr = ["lines", "fsize"];
		var value;
		for(var i = 0; i < arr.length; i ++) {
			var index = document.cookie.indexOf(arr[i]);
			if(index != -1) {
				namestart = (document.cookie.indexOf("=", index) + 1);
				nameend = document.cookie.indexOf(";", index);
				if(nameend == -1) {
					nameend = document.cookie.length;
				}
				value = document.cookie.substring(namestart, nameend);
				switch (i) {
				case 0:
					calctut.lines = value == "true";
					break;
				case 1:
					calctut.fsize = value;
					break;
				default:
					break;
				}
			}
		}
	},
	
	writeCookieLines: function() {
		document.cookie = "lines="+calctut.lines+"; expires="+calctut.twoyears.toString();
	},
	
	writeCookieFSize: function() {
		if(calctut.fsize > 5) {
			calctut.fsize = 5;
		} else if(calctut.fsize < -2) {
			calctut.fsize = -2;
		}
		document.cookie = "fsize="+calctut.fsize+"; expires="+calctut.twoyears.toString();
	},
	
	writeCookieLastVisited: function() {
		document.cookie = "lastvisited="+calctut.pages[calctut.index]+"; expires="+calctut.twoyears.toString();
	},
	
	goToCurrentNav: function() {
	    return;
	    /*
		var pos = calctut.end-calctut.index;
		if(calctut.index < 0) {
			pos = 1;
		}
		navbarjs.initSlide(pos, true);
		navbarjs.currentTab = pos;
		*/
	},
	
	hideExplanations: function() {
		for(var i = 1; true; i ++) {
			d = document.getElementById("explain"+i);
			if(!d) {
				break;
			}
		   d.style.display = 'none';
		}
	},
	
	populateDropdown: function() {
		var select = document.getElementById("tutgoto");
		var x = new Option();
		x.text = "Go to...";
		x.value = "-1";
		var y = new Option();
		y.text = "Review";
		y.value = "-1";
		//Even though select.add(x, null); would be standards-compliant, IE doesn't support it. Hm...
		//One more reason to use Firefox, I guess.
		try {
		   select.add(x, null);
		   select.add(y, null);
		} catch(err) {
		   select.add(x);
		   select.add(y);
		}
		for(var i = 0; i < calctut.pages.length; i ++) {
		   var opt = new Option();
		   if(i > 0) {
			  var num = i+"";
			  if(num.length == 1)
				  num = "0"+num;
			  opt.text = num+"-"+calctut.titles[i];
		   } else {
			  opt.text = calctut.titles[i];
		   }
		   opt.value = ""+i;
		   try {
			  select.add(opt, null);
		   } catch(err) {
			  select.add(opt);
		   }
		}
		select.selectedIndex = calctut.index+2;
	},
	
	toggleLineNumbers: function() {
		calctut.lines = !calctut.lines;
		calctut.writeCookieLines();
		calctut.updateLineNumbers();
	},
	
	fontPlus: function() {
		calctut.fsize ++;
		calctut.writeCookieFSize();
	},
	
	fontMinus: function() {
		calctut.fsize --;
		calctut.writeCookieFSize();
	},
	
	updateLineNumbers: function() {
		var pres = document.getElementsByTagName('pre');
		var tutcodes = new Array();
		for(var i = 0; i < pres.length; i ++) {
			if(pres[i].className == 'tutcode')
				tutcodes.push(pres[i]);
		}
		for(var i = 0; i < tutcodes.length; i ++) {
			var s = tutcodes[i].innerHTML.split('\n');
			var html = '';
			for(var a = 0; a < s.length; a ++) {
				if(s[a] == '' && a+1 == s.length) {
					break;
				}
				if(calctut.lines) {
					s[a] = (a+1)+') '+s[a];
				} else if(s[a].indexOf(")") == (a+1).toString().length) {
					s[a] = s[a].substring((a+1).toString().length+2);
				} else {
					i = -1;
					break;
				}
				html += s[a]+'\r\n';
			}
			if(i == -1) {
				break;
			}
			tutcodes[i].innerHTML = html;
		}
	},
	
	dropdownSelect: function () {
		var select = document.getElementById("tutgoto");
		if(select.selectedIndex > 0) {
			document.location.href = calctut.pages[select.selectedIndex-2];
		}
	},
	
	generateNav: function() {
		if(calctut.id == null) {
		   calctut.initCalc();
		}
		calctut.start = calctut.index;
		calctut.end = calctut.index;
		if(calctut.index+1 < calctut.pages.length) {
		   document.write("<li id=\""+calctut.id[calctut.index+1]+"\"><a href=\""+calctut.pages[calctut.index+1]+"\" title=\"\">Next ("+calctut.titles[calctut.index+1]+")<\/a><\/li>");
		   calctut.end = calctut.index+1;
		}
		if(calctut.index >= -1)
		   document.write("<li id=\""+calctut.id[calctut.index]+"\"><a href=\""+calctut.pages[calctut.index]+"\" title=\"\">"+calctut.titles[calctut.index]+"<\/a><\/li>");
		if(calctut.index >= 0) {
		   document.write("<li id=\""+calctut.id[calctut.index-1]+"\"><a href=\""+calctut.pages[calctut.index-1]+"\" title=\"\">Previous ("+calctut.titles[calctut.index-1]+")<\/a><\/li>");
		   calctut.start = calctut.index-1;
		}
	},
	
	toggle: function(no) {
		var disp = document.getElementById("explain"+no).style.display == 'none';
		if(disp) {
		   document.getElementById("explain"+no).style.display = '';
		} else {
		   document.getElementById("explain"+no).style.display = 'none';
		}
	},
	
	ansToggle: function(no, text) {
		var ans = document.getElementById("answer"+no);
		if(ans.innerHTML == "Toggle answer") {
			ans.innerHTML = text;
		}
		else {
			ans.innerHTML = "Toggle answer";
		}
	},
    
	writePreviousPage: function() {
		if(calctut.index-1 >= 0) {
			document.write("<td><a class=\"noresize\" href=\""+calctut.pages[calctut.index-1]+"\">Previous ("+calctut.titles[calctut.index-1]+")<\/a><\/td>");
		} else {
			document.write("<td>&nbsp;<\/td>");
		}
	},
    
	writeNextPage: function() {
		if(calctut.index+1 < calctut.pages.length) {
			document.write("<td><a class=\"noresize\" href=\""+calctut.pages[calctut.index+1]+"\">Next ("+calctut.titles[calctut.index+1]+")<\/a><\/td>");
		} else {
			document.write("<td>&nbsp;<\/td>");
		}
	},
	
	doLastVisited: function() {
		calctut.initCalc();
		var namestart, nameend, address, title = "";
		var index = document.cookie.indexOf("lastvisited");
		if(index != -1) {
			namestart = (document.cookie.indexOf("=", index) + 1);
			nameend = document.cookie.indexOf(";", index);
			if(nameend == -1)
				nameend = document.cookie.length;
			address = document.cookie.substring(namestart, nameend);
		} else {
			address = calctut.pages[0];
		}
		for(var i = -1; i < calctut.pages.length; i ++) {
			if(calctut.pages[i] == address) {
				title = calctut.titles[i];
			}
		}
		document.write("<br /><br />Redirecting to <em>"+title+"<\/em>");
		calctut.redir = address;
	},
	
	redirect: function() {
		document.location.href = calctut.redir;
	}
};

