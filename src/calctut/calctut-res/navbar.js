var navbarjs = {
   currentTab:         0,
   activeTab:          0,
   destX:              null,
   destW:              null,
   t:                  null,
   b:                  null,
   c:                  null,
   d:                  6, //resolution/posdiff
   posdiff:	       null,
   speed:              15, 
   animInterval:       null,
   slideObj:           null,
   aHeight:            0,
   stopAnimation:      false,
   
   init: function() {
      
      var ul        = document.getElementById("navbar");
      if(ul == null) { /*alert("error: navbar missing");*/ return false;}
      var liArr     = ul.getElementsByTagName("li");
      var aArr      = ul.getElementsByTagName("a");
      
      for(var i = 0, li; li = liArr[i]; i++) {
      if(aArr[i] === null) continue;
	 aArr[i].onclick = function(e) {
            navbarjs.stopAnimation = true;
            return true;
         }
         liArr[i].onmouseover = aArr[i].onfocus = function(e) {
            var pos       = 0;
            var elem      = this.nodeName == "LI" ? this : this.parentNode;
            while(elem.previousSibling) {
               elem       = elem.previousSibling;
               if(elem.tagName && elem.tagName == "LI") pos++;
            }
            navbarjs.initSlide(pos, true);
         }
      };
      
      ul.onmouseout = function(e) {
         if (navbarjs.stopAnimation) return;
         navbarjs.initSlide(navbarjs.currentTab, false);
      };
      
      if (document.location.href.charAt(document.location.href.length-1) == "/") {
         navbarjs.activeTab = navbarjs.currentTab = aArr.length-1;
         aArr[aArr.length-1].setAttribute("class", "active");
      } else {
      for(var i = 0; i < aArr.length; i++) {
         //alert(aArr[i].href.substring(0,aArr[i].href.length-5));
         if(document.location.href.indexOf(aArr[i].href.substring(0,aArr[i].href.length-5))>=0) {
            navbarjs.activeTab = navbarjs.currentTab = i;
            aArr[i].setAttribute("class", "active");
            break;
         }
      }
     };
     if (navbarjs.slideObj == null) { 
      navbarjs.slideObj  = ul.parentNode.appendChild(document.createElement("div"));
     }
      with(navbarjs.slideObj) {
         appendChild(document.createTextNode(String.fromCharCode(160)));
         id              = "animated-tab";
         style.top       = (ul.offsetTop  + liArr[navbarjs.activeTab].offsetTop  + aArr[navbarjs.activeTab].offsetTop) + "px";
         style.left      = (ul.offsetLeft + liArr[navbarjs.activeTab].offsetLeft + aArr[navbarjs.activeTab].offsetLeft) +  "px";
         style.width     = aArr[navbarjs.activeTab].offsetWidth + "px";
      };
      
      navbarjs.aHeight   = ul.offsetTop + liArr[navbarjs.activeTab].offsetTop + aArr[navbarjs.activeTab].offsetTop;
       
      var intervalMethod   = function() { navbarjs.slideIt(); }
      navbarjs.animInterval = setInterval(intervalMethod,navbarjs.speed);

      navbarjs.initSlide(navbarjs.currentTab, true);
   },

   cleanUp: function() {
      clearInterval(navbarjs.animInterval);
      navbarjs.animInterval = null;
   },
   
   initSlide: function(pos, force) {
      if(!force && pos == navbarjs.activeTab) return;
      navbarjs.activeTab = pos;
      var newposdiff =  Math.abs(navbarjs.currentTab - navbarjs.activeTab);
      if (newposdiff > 0) { navbarjs.posdiff = newposdiff; }
      navbarjs.initAnim();
   },
   
   initAnim: function() {      
      var ul           = document.getElementById("navbar");
      var liArr        = ul.getElementsByTagName("li");
      var aArr         = ul.getElementsByTagName("a");

      navbarjs.destX    = parseInt(liArr[navbarjs.activeTab].offsetLeft + liArr[navbarjs.activeTab].getElementsByTagName("a")[0].offsetLeft + ul.offsetLeft);
      navbarjs.destW    = parseInt(liArr[navbarjs.activeTab].getElementsByTagName("a")[0].offsetWidth);
      navbarjs.t        = 0;
      navbarjs.b        = navbarjs.slideObj.offsetLeft;
      navbarjs.c        = navbarjs.destX - navbarjs.b;

      navbarjs.bW       = navbarjs.slideObj.offsetWidth;
      navbarjs.cW       = navbarjs.destW - navbarjs.bW;
      
      
      navbarjs.slideObj.style.top = (ul.offsetTop + liArr[navbarjs.activeTab].offsetTop + aArr[navbarjs.activeTab].offsetTop) + "px";
   },
   
   slideIt:function() {
      var ul           = document.getElementById("navbar");
      var liArr        = ul.getElementsByTagName("li");
      var aArr         = ul.getElementsByTagName("a");
      
      // Has the browser text size changed?
      if(navbarjs.aHeight 
         != ul.offsetTop + liArr[navbarjs.activeTab].offsetTop + aArr[navbarjs.activeTab].offsetTop) {
         navbarjs.initAnim();
         navbarjs.aHeight 
            = ul.offsetTop + liArr[navbarjs.activeTab].offsetTop + aArr[navbarjs.activeTab].offsetTop;
      };
      var x;
      var w;
      var anisteps = navbarjs.d * navbarjs.posdiff + 3;
      if(navbarjs.t++ < anisteps) {
         x = navbarjs.animate(navbarjs.t,navbarjs.b,navbarjs.c,anisteps);
         w = navbarjs.animate(navbarjs.t,navbarjs.bW,navbarjs.cW,anisteps);

         navbarjs.slideObj.style.left     = parseInt(x) + "px";
         navbarjs.slideObj.style.width    = parseInt(w) + "px";
      } else {
         navbarjs.slideObj.style.left     = navbarjs.destX + "px";
         navbarjs.slideObj.style.width    = navbarjs.destW + "px";
      }
   },

   animate: function(t,b,c,d) {
      if ((t/=d/2) < 1) return c/2*t*t + b;
      return -c/2 * ((--t)*(t-2) - 1) + b;
   }
};

//window.onload = navbarjs.init;
//window.onunload = navbarjs.cleanUp;
