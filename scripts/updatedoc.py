#!/usr/bin/env python

###########################################################################
# Copyright (c) 2010--2011 Minh Van Nguyen <nguyenminh2@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# http://www.gnu.org/licenses/
###########################################################################

# README
#
# Updating the online Sage standard documentation and the downloadable
# compressed tarballs. Run this script as follows:
#
# $ ./updatedoc.py /path/to/SAGE_ROOT/
#
# where /path/to/SAGE_ROOT/ refers to the SAGE_ROOT of a pre-compiled Sage
# version. The above command will generate both the HTML and PDF versions of
# the Sage standard documentation using the following commands:
#
# $ ./sage -docbuild --no-pdf-links all html
# $ ./sage -docbuild all pdf
#
# The generated documentation will then be wrapped up into a tarball named
# sage-x.y.z-doc.tar.bz2. The bzip2 compressed tarball containing the
# generated documentation is assumed to follow this directory structure:
#
# sage-x.y.z-doc/
# +- html/
# |  +- en/
# |  |  +- a_tour_of_sage/
# |  |  +- bordeaux_2008/
# |  |  +- constructions/
# |  |  +- developer/
# |  |  +- installation/
# |  |  +- numerical_sage/
# |  |  +- reference/
# |  |  +- _sources/
# |  |  +- _static/
# |  |  +- tutorial/
# |  |  +- website/
# |  |  +- genindex-all.html
# |  |  +- genindex.html
# |  |  +- index.html
# |  |  +- search.html
# |  |  +- objects.inv
# |  |  +- searchindex.js
# |  +- fr/
# |     +- a_tour_of_sage/
# |     +- tutorial
# +- pdf/
#    +- en/
#    |  +- a_tour_of_sage.pdf
#    |  +- bordeaux_2008.pdf
#    |  +- constructions.pdf
#    |  +- developer.pdf
#    |  +- installation.pdf
#    |  +- numerical_sage.pdf
#    |  +- reference.pdf
#    |  +- SageTutorial.pdf
#    +- fr/
#       +- a_tour_of_sage.pdf
#       +- tutorial-fr.pdf
#
# Finally, this script uses the tarball sage-x.y.z-doc.tar.bz2 to update the
# documentation on the Sage website.

from subprocess import PIPE, Popen

import os
import re
import sys

DEV_DIR = "/home/sagemath/www2-dev"
DOC_DIR = "/home/sagemath/www-files/doc"
DOC_NAME = os.path.join(DEV_DIR, "www/help.html")
DOCBUILD = os.path.join(DEV_DIR, "builddoc.sh")
SAGE_ROOT = None
SAGE_SAGE = None
SAGE_VERSION = None

def delete_previous_doc(target_dir):
    """
    Delete the previous version of the Sage standard documentation.

    INPUT:

    - target_dir -- the directory where the previous version of the
      documentation lives. This is the same as the directory where the new
      version will be located.

    OUTPUT:

    Remove the previous version of the Sage standard documentation from the
    specified directory.
    """
    print("Delete previous version of documentation...")
    sys.stdout.flush()
    os.chdir(target_dir)
    os.system("rm -rf sage-*-doc")
    os.system("rm -rf doc-bz2")
    os.system("rm -rf doc-zip")
    os.system("rm html pdf")

def update_doc(current_dir, target_dir, doc_tarball, filename, sage_version):
    """
    Update the website with the current version of the Sage standard
    documentation.

    INPUT:

    - current_dir -- the current directory where the bzip2 compressed
      tarball of the new documentation is located.

    - target_dir -- the directory where the new version of the documentation
      is to be located. This is the same directory as where the previous
      version of the documentation was located.

    - doc_tarball -- the file containing the bzip2 compressed tarball of the
      new documentation. The name of this tarball is assumed to follow the
      general format sage-x.y.z-doc.tar.bz2.

    - filename -- the name of the HTML file containing links to HTML and
      PDF versions of the standard documentation.

    - sage_version -- like 5.11, used for the specific subdirectory

    OUTPUT:

    Update the website with the new version of the documentation.
    """
    print("Copy over new version of documentation...")
    sys.stdout.flush()
    os.chdir(current_dir)
    os.system("tar -jxf " + doc_tarball + " -C " + target_dir)
    docdir = doc_tarball.split(".tar.bz2")[0]

    os.chdir(os.path.join(current_dir, "www"))
    # update links for English documentation
    os.system("rm pdf")
    os.system("ln -s " + os.path.join(target_dir, docdir, "pdf/") + " pdf")
    # update links for French documentation
    os.chdir(os.path.join(current_dir, "www/fr"))
    os.system("rm html pdf")
    os.system("ln -s " + os.path.join(target_dir, docdir, "html/fr/") + " html")
    os.system("ln -s " + os.path.join(target_dir, docdir, "pdf/fr/") + " pdf")
    # update links for German documentation
    os.chdir(os.path.join(current_dir, "www/de"))
    os.system("rm html pdf")
    os.system("ln -s " + os.path.join(target_dir, docdir, "html/de/") + " html")
    os.system("ln -s " + os.path.join(target_dir, docdir, "pdf/de/") + " pdf")
    # update links for Russian documentation
    os.chdir(os.path.join(current_dir, "www/ru"))
    os.system("rm html pdf")
    os.system("ln -s " + os.path.join(target_dir, docdir, "html/ru/") + " html")
    os.system("ln -s " + os.path.join(target_dir, docdir, "pdf/ru/") + " pdf")

    os.chdir(target_dir)
    os.system("ln -s " + os.path.join(docdir, "html/en") + " html")
    os.system("ln -s " + os.path.join(docdir, "pdf") + " pdf")
    bz2dir = os.path.join(target_dir, "doc-bz2")
    zipdir = os.path.join(target_dir, "doc-zip")
    os.system("mkdir " + bz2dir)
    os.system("mkdir " + zipdir)

    os.chdir(docdir)
    os.system("cp -rf html " + docdir + "-html")
    os.system("cp -rf pdf " + docdir + "-pdf")
    os.system("tar -jcf " + docdir + "-html.tar.bz2 " + docdir + "-html")
    os.system("tar -jcf " + docdir + "-pdf.tar.bz2 " + docdir + "-pdf")
    os.system("zip -rq " + docdir + "-html.zip " + docdir + "-html")
    os.system("zip -rq " + docdir + "-pdf.zip " + docdir + "-pdf")
    os.system("mv " + docdir + "*.bz2 " + bz2dir)
    os.system("mv " + docdir + "*.zip " + zipdir)
    os.system("rm -rf " + docdir + "-html")
    os.system("rm -rf " + docdir + "-pdf")
    os.chdir(target_dir)
    os.system("tar -jcf " + docdir + ".tar.bz2 " + docdir)
    os.system("zip -rq " + docdir + ".zip " + docdir)
    os.system("mv " + docdir + ".tar.bz2 " + bz2dir)
    os.system("mv " + docdir + ".zip " + zipdir)

    print("Update %s" % filename)
    sys.stdout.flush()
    # get size in MB of compressed documentation, exact to 1 decimal digit
    os.chdir(bz2dir)
    n = os.path.getsize(docdir + ".tar.bz2")
    n = str(n / (1024.0 * 1024.0))
    bz2doc_size = n[:n.find(".") + 2]
    n = os.path.getsize(docdir + "-html.tar.bz2")
    n = str(n / (1024.0 * 1024.0))
    bz2dochtml_size = n[:n.find(".") + 2]
    n = os.path.getsize(docdir + "-pdf.tar.bz2")
    n = str(n / (1024.0 * 1024.0))
    bz2docpdf_size = n[:n.find(".") + 2]
    os.chdir(zipdir)
    n = os.path.getsize(docdir + ".zip")
    n = str(n / (1024.0 * 1024.0))
    zipdoc_size = n[:n.find(".") + 2]
    n = os.path.getsize(docdir + "-html.zip")
    n = str(n / (1024.0 * 1024.0))
    zipdochtml_size = n[:n.find(".") + 2]
    n = os.path.getsize(docdir + "-pdf.zip")
    n = str(n / (1024.0 * 1024.0))
    zipdocpdf_size = n[:n.find(".") + 2]

    # update HTML file with new compressed documentation paths and sizes
    re_start_doc = re.compile(r"START_TOKEN_DOC")
    re_end_doc = re.compile(r"END_TOKEN_DOC")
    htmlfile = open(filename, "r")
    htmlcontent = ""
    line = htmlfile.readline()
    # get everything before the table of compressed documentation
    while not re_start_doc.search(line):
        htmlcontent = "".join([htmlcontent, line])
        line = htmlfile.readline()
    # include the stub that delimits the beginning of the compressed doc
    htmlcontent = "".join([htmlcontent, line, "\n"])
    # Ignore everything between the start of the table of compressed doc and
    # the end of that list. We do this because we want to insert a new table
    # of compressed doc in between the stubs that delimit the start and end of
    # the table of compressed doc.
    while not re_end_doc.search(line):
        line = htmlfile.readline()
    htmlcontent = "".join([htmlcontent, "<table cellpadding=\"6\">\n"])
    htmlcontent = "".join([htmlcontent, "  <tr bgcolor=\"#b8b9f9\">\n"])
    htmlcontent = "".join([htmlcontent, "    <th>Format</th>\n"])
    htmlcontent = "".join([htmlcontent, "    <th>Packed as .zip</th>\n"])
    htmlcontent = "".join([htmlcontent, "    <th>Packed as .tar.bz2</th>\n"])
    htmlcontent = "".join([htmlcontent, "  </tr>\n\n"])
    htmlcontent = "".join([htmlcontent, "  <tr bgcolor=\"#dfdfff\">\n"])
    htmlcontent = "".join([htmlcontent, "    <td>HTML</td>\n"])
    htmlcontent = "".join([
            htmlcontent, "    <td><a href=\"./doc-zip/",
            docdir, "-html.zip\">download</a> (",
            str(zipdochtml_size), " MB)</td>\n"])
    htmlcontent = "".join([
            htmlcontent, "    <td><a href=\"./doc-bz2/",
            docdir, "-html.tar.bz2\">download</a> (",
            str(bz2dochtml_size), " MB)</td>\n"])
    htmlcontent = "".join([htmlcontent, "   </tr>\n\n"])
    htmlcontent = "".join([htmlcontent, "  <tr bgcolor=\"#dfdfff\">\n"])
    htmlcontent = "".join([htmlcontent, "    <td>PDF</td>\n"])
    htmlcontent = "".join([
            htmlcontent, "    <td><a href=\"./doc-zip/",
            docdir, "-pdf.zip\">download</a> (",
            str(zipdocpdf_size), " MB)</td>\n"])
    htmlcontent = "".join([
            htmlcontent, "    <td><a href=\"./doc-bz2/",
            docdir, "-pdf.tar.bz2\">download</a> (",
            str(bz2docpdf_size), " MB)</td>\n"])
    htmlcontent = "".join([htmlcontent, "  </tr>\n\n"])
    htmlcontent = "".join([htmlcontent, "  <tr bgcolor=\"#dfdfff\">\n"])
    htmlcontent = "".join([htmlcontent, "    <td>HTML+PDF</td>\n"])
    htmlcontent = "".join([
            htmlcontent, "    <td><a href=\"./doc-zip/",
            docdir, ".zip\">download</a> (",
            str(zipdoc_size), " MB)</td>\n"])
    htmlcontent = "".join([
            htmlcontent, "    <td><a href=\"./doc-bz2/",
            docdir, ".tar.bz2\">download</a> (",
            str(bz2doc_size), " MB)</td>\n"])
    htmlcontent = "".join([htmlcontent, "  </tr>\n"])
    htmlcontent = "".join([htmlcontent, "</table>\n"])
    # Process the rest of the HTML file.
    # Get everything from here to the end of the file. This also include the
    # stub that delimits the end of the table of compressed doc.
    try:
        # When the end of the file is reached, this will raise a StopIteration
        # exception.
        while True:
            htmlcontent = "".join([htmlcontent, line])
            line = htmlfile.next()
    except StopIteration:
        # We have reached the end of the file. We don't need to do
        # anything further, apart from closing the file.
        pass
    finally:
        htmlfile.close()
    # Replace the current publications page with another page that contains
    # updated lists of publications. This overwrites the current publications
    # page.
    outfile = open(filename, "w")
    outfile.write(htmlcontent)
    outfile.close()

def usage():
    """
    Print the usage information for this script.
    """
    print "".join(["Usage: ", sys.argv[0], " /path/to/SAGE_ROOT/"])
    sys.stdout.flush()


##############################
# the script starts here
##############################

if __name__ == "__main__":
    # sanity checks
    if len(sys.argv) != 2:
        usage()
        sys.exit(1)
    SAGE_ROOT = os.path.abspath(sys.argv[1])
    if not os.path.isdir(SAGE_ROOT):
        print("Invalid SAGE_ROOT. Exiting...")
        sys.stdout.flush()
        sys.exit(1)
    SAGE_SAGE = os.path.join(SAGE_ROOT, "sage")
    if not os.path.isfile(SAGE_SAGE):
        print("Invalid Sage start up script %s. Exiting..." % SAGE_SAGE)
        sys.stdout.flush()
        sys.exit(1)
    # get Sage's version number
    # Assume that the following shell command would output a string as
    # follows:
    #
    # $ Sage Version x.y.z, Release Date: yyyy-mm-dd
    sh = Popen("%s --version" % SAGE_SAGE, shell=True, stdout=PIPE)
    s = sh.communicate()[0].strip()
    if sh.returncode != 0:
        print("Error running %s. Exiting..." % SAGE_SAGE)
        sys.stdout.flush()
        sys.exit(1)
    s = s.split()[2]
    SAGE_VERSION = s.split(",")[0]
    # build HTML and PDF versions of standard documentation
    if not os.path.isfile(DOCBUILD):
        print("Documentation build script %s not found. Exiting..." % DOCBUILD)
        sys.stdout.flush()
        sys.exit(1)
    sh = Popen("%s %s %s" % (DOCBUILD, SAGE_ROOT, SAGE_VERSION), shell=True)
    sh.communicate()
    if sh.returncode == 1:
        print("Error building documentation. Exiting...")
        sys.stdout.flush()
        sys.exit(1)
    # update website with built documentation
    Popen(
        "cp %s/sage-%s-doc.tar.bz2 %s" % (SAGE_ROOT, SAGE_VERSION, DEV_DIR),
        shell=True).communicate()
    delete_previous_doc(DOC_DIR)
    update_doc(
        DEV_DIR,
        DOC_DIR,
        "sage-%s-doc.tar.bz2" % SAGE_VERSION,
        DOC_NAME,
        SAGE_VERSION)
