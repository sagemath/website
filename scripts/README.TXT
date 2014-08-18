README FOR SAGEMATH.ORG WEB ADMINISTRATORS
##########################################

Redesign started April 2008 by Harald Schilly.

!!! It is very important to read this file, otherwise you trigger bugs
    in some browsers !!!


Webserver: Apache 2
===================

The .htaccess file has more information. Two modules are needed in
addition to the default ones:

* mod_headers --- to enable client side caching, reduces traffic and
  load time. Really good for all those documentation pages!

* mod_includes --- SSI (apache server side includes). The idea is to
  include HTML snippets inside other files. Read .htaccess file, which
  defines that all files with the execution bit set are processed.


Layout
======

Ideas: separate HTML content, files and helping tools like
scripts/graphsc source files/hg root

/---.hg root, README, scripts
|
|
+---/www       only this is published!
|   /.htaccess controls apache!
|   |
|   +---/res /inc and /pix for js and css resources, .shtml SSI includes and pictures
|   |
|   +---/library   subdir for the library stuff
|   +---/de        german (future)
|   +---[symlinks] to www-files (external and independent directory), documentation, ...
|
|
+---/graphics (or others)  store other stuff, non public


Editing and publishing
======================

0. Edit files.

1. CHECK IF IT WORKS: to avoid broken pages cd to
   ./sandbox/... subdirectory (e.g. if tidyall.sh corrected something
   wrongly)

2. Run script "go_live.sh" to update live pages in one single step.


Workflow
--------

1. Check edited files in the ./www directory. There you can work
   without changing the real site. This is mapped to
   sagemath.org/sandbox and kept 'private' and excluded in the
   robots.txt file.


New release procedure
---------------------

1. New binary/source files go into ~/www-files/...

2. Run the script ./mirror-index.py to update the index pages of the
   mirror pages. Note: These changes are immediately visible at
   sagemath.org/mirror but that URL is *not* published anywhere!

3. Edit www/inc/variables.shtml *PRIOR* to running the mirror script
   to reflect new version numbers.

4. Call the mirror script ~/mirror to rsync to other servers. Note:
   the script mirror_manager will update the website by itself.


New SPKGs procedure
-------------------
1. If optional or experimental: new SPKGs go into ~/www-files/spkg/...

2. Then run the ~/www-files/spkg/gen_html script to create the mirror pages.

# no longer true: we have this /upstream thing now
#2. If updating new standard packages, use the .tar ball of the Sage source distribution
#   and run the export script. (done automatically when doing a new release)

3. If necessary (security issue), run the ~/mirror script with parameter t:
   $ ~/mirror t
   to create a new timestamp to invalidate older mirrors.


mirror_manager.py
-----------------

Read the header of the script for more information. This script
generates the www/inc/mirrorselector.shtml page to list all active and
up-to-date mirrors. It is called periodically by crontab (every 10
Minutes) to edit this or stop the script in case of broken download
pages.

1. $ crontab -e
   Place a "#" in front the of the schedule line.

2. Restore the www/inc/mirrorselector.shtml page from Mercurial (hg
   revert). File should still be under version control.

3. To manually run the script, call ./mirror_manager_wrapper.sh


Updating Mercurial repositories at http://hg.sagemath.org
---------------------------------------------------------

1. Extract a Sage binary tarball.

2. Navigate to the SAGE_ROOT of the resulting directory.

3. Now issue this command:

   /home/sagemath/bin/sage-pushall

   This script uses Sage. If the above command doesn't work, open the
   script in a text editor. Change all occurrences of "sage" to

   SAGE_ROOT/sage

   Save your changes and issue the command

   /home/sagemath/bin/sage-pushall

   After the script finish running, change all instances of
   "SAGE_ROOT/sage" in the script back to "sage".


Publications database
---------------------

Make sure you have pybtex installed in your local Python environment. So far,
the standard procedure is not to install pybtex system-wide on sagemath.
Instead, you should build/install your own version of Sage. Then clone the
pubparse utility available from

http://bitbucket.org/mvngu/pubparse

and use the version of Python shipped with Sage to install pybtex. Run the
publication parser thus:

$ sage/sage -python publications_parser.py

Minh Van Nguyen has been managing the publications database this way since
early 2010. His local Sage/pybtex installation is available at

http://sage.math.washington.edu/home/mvngu/apps/pubparse/

To update the publications list on the Sage website, first he update the
relevant BibTeX files in his local pubparse installation. Then run the script
publications_parser.py as shown above. After ensuring that the resulting 
HTML files are OK, he would then copy the .bib and HTML files over
to the Sage website. Put BibTeX files under 

www/files/

and HTML files under

www/


updatedoc.py
------------

This script automates updating the online and downloadable documentation.
See the script for more information about its usage.


update_components.py
--------------------

This script automates updating the page containing the list of components
that Sage uses. See the script for more information about its usage.


MOTD: Message of the day
------------------------

It's displayed on the main page, above the graphic buttons. Edit
./www/inc/motd.shtml as appropriate.


Slashdotting & co.
------------------

If a high volume of requests happen and the server is unresponsive,
this is probably due to open downloads. In this case, remove the first
mirror entry (sage.math) from the list of mirrors! Then, all the
traffic is distributed only to the mirrors and the main website stays
alive.

For this, edit the file ./mirror_manager.py and replace "True" by
"False" in the Mirror entries list as last argument.


Development map
===============

If you want to edit or update the development map, do this:

1. Edit www/res/contributors.xml --- see the header of that file for
   the syntax to use.

2. Put optional pictures into www/pix.

3. GEOCODE: run ./geocode.py in the base directory. First it builds a
   cache of locations to lat-long translations in
   www/res/geocode.xml. Then it edits the developer-map.html file (the
   table for javascript disabled and search engines).

4. IMPORTANT: Always run "./tidyall.sh developer-map.html" after step
   3 to homogenize the HTML code. this reduces the diffs down to the
   relevant part.

5. Edit the devcloud div tag inside the developer-map.html, only if it
   collapes to <div .../> and not <div ...></div>  <--- should be fixed.

6. Publish after checking the page in the /sandbox/ subdir with go_live.sh


.htaccess
=========

A whole universe of its own... Just for reference, these are the lines
to redirect the entire page (from lite.... to www. ...).

# this redirects everything to the new page
RewriteEngine On
RewriteCond %{HTTP_HOST} ^lite.sagemath.org$ [NC]
RewriteRule ^(.*)$ http://sagemath.org/$1 [R=301,L]


Funny html pages
================

They are authentication tokens for

* https://www.google.com/webmasters

* https://siteexplorer.search.yahoo.com/mysites
(add your own tokens for your own accounts ...)


sitemap.xml
===========

Just some entry points, doesn't need to be more since we are static
http://sitemaps.org


/www/mirror
===========

This is a stripped down version to broadcast across other mirror
sites. It consists of index files and symlinks to the directories.
Index it by running ./mirror-index.py. rsync has to follow them and
treat them as real files.

ssh --rsh=ssh -axHKL --delete -r -v www2/mirror/ was@sage.math.washington.edu:www/sage/ 1>.mirror.log 2>.mirror.errors
-K copy directory
-L symlinks are real


google code snippet for conversion tracker - only when doing advertising!
-------------------------------------------------------------------------
<!-- Google Code for download page Conversion Page -->
<script language="JavaScript" type="text/javascript">
//<![CDATA[
 <!--
 var google_conversion_id = 1040133199;
 var google_conversion_language = "en_US";
 var google_conversion_format = "1";
 var google_conversion_color = "ffffff";
 if (0.00) {
  var google_conversion_value = 0.00;
 }
 var google_conversion_label = "5ZyMCPHCVRDP2PzvAw";
 //-->
 //]]>
</script>
<script language="JavaScript"
       src="http://www.googleadservices.com/pagead/conversion.js"
       type="text/javascript">
</script>
<noscript><img height="1" width="1" border="0" alt="" src= "http://www.googleadservices.com/pagead/conversion/1040133199/?value=0.00&amp;label=5ZyMCPHCVRDP2PzvAw&amp;script=0" /></noscript>
