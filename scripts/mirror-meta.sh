#!/usr/bin/env bash
# Goes through the mirror files and generates
# meta files like torrents for files >2MB
# in the subdirectory 'meta'
# depends on ctorrent (debian package)

# set -e

if [ ! -n "$1" ]; then
   echo '$1 variable not set, must be the directory where to index, e.g. ~/files'
   exit 1
fi

# *ONLY* relative to itself for this torrent.helper file path!
cd `dirname "$0"`
TORRENT_HELPER=`readlink -f ../www/torrent.helper`

FILES=`readlink -f $1`
echo "FILES: $FILES"

if [ ! -d $FILES ] ; then
  echo files/ does not exist
  exit 1
fi

# from now on we switch to the target $FILES directory
cd $FILES
FINDCMD='find  . -type f -size +2M -follow -not -name "*spkg*" -not -name "*zsync" | grep -v -e "\./doc/.*"'

function metatorrent () {
    OUTPUT=$1
    # $2 is the title
    ENDING=$3
    # collect all metalinks in one file
    [[ -e $OUTPUT ]] && rm -f $OUTPUT
    touch $OUTPUT
    # intro
    for line in `cat index.html`; do
      if [[ "$line" =~ "TOK1" ]] ; then
        break
      fi
      echo "$line" >> $OUTPUT
    done 
    # write content
    echo "<h1>$2 for <a href='https://www.sagemath.org/'>SageMath</a></h1>" >> $OUTPUT
    echo '<div><strong>Read more <a href="https://wiki.sagemath.org/DownloadAndInstallationGuide">in the Download Guide</a></strong></div>' >> $OUTPUT
    echo '<div><table>' >> $OUTPUT
    for f in `eval $FINDCMD`; do
     f=${f:2}
     METADIR=`dirname $f`/meta
     FILE=`basename $f`
     METAFILE=$METADIR/`basename $f`.$ENDING
     echo '<tr><td>'${METADIR%/meta}'</td><td>' >> $OUTPUT
     echo '<a onClick="pageTracker._trackEvent('MirrorDL', '`dirname $f`', '`basename $f`.$ENDING', 1)"' >> $OUTPUT
     echo ' href="./'$METAFILE'">'$FILE'</a></td></tr>' >> $OUTPUT
    done
    echo '</table></div>' >> $OUTPUT
    # end of index file
    # outro
    writeout=False
    for line in `cat index.html`; do
      if [[ "$line" =~ "TOK2" ]] ; then
        writeout=True
      fi
      if [[ "$writeout" = True ]]; then
        echo "$line" >> $OUTPUT
      fi
    done 
    
    # publish it
    echo published $OUTPUT file to `dirname "./$OUTPUT"`
    echo cp -f $OUTPUT ./$OUTPUT
}

# metatorrent metalinks.html Metalinks    metalink
metatorrent torrents.html  BitTorrents  torrent

######################

# comment in torrent file
COMMENT="Sage Mathematical Software System: http://www.sagemath.org/"

# now the 'real' work
ROOT=`pwd`
ROOTLEN=`expr ${#ROOT} + 1`
# searches for all files, which are above a certain size, and also which are not
# spkges or part of the documentation

for f in `eval $FINDCMD`; do
# echo $f
 f=${f:2} #removes find's ./ in the beginning
 DIR=`dirname $f`
 METADIR=`dirname $f`/meta
 FILE=`basename $f`
 TORFILE=$METADIR/`basename $f`.torrent

 if [ ! -d $METADIR ]; then
   mkdir $METADIR
 fi
 
 # -s tests, if file exists and has size >0
 if [ ! -s $TORFILE ]
 then
   pushd $METADIR
   cd ..
     #ctorrent -t -u "udp://tracker.openbittorrent.com:80" -l 1025000 -s meta/$FILE.torrent $FILE 
     P=`pwd`
     RELDIR=${P:$ROOTLEN}
     echo $RELDIR
     WEBSEEDS=""
     while read line; do
       # TODO: the trailing $FILE is just for µtorrent. all others work well with the trailing / !!!
       WEBSEEDS=$WEBSEEDS,${line}${RELDIR}/$FILE
     done < $TORRENT_HELPER
     # substring deletes, if matched, see http://tldp.org/LDP/abs/html/string-manipulation.html
     WEBSEEDS=${WEBSEEDS#,} # delete , at the start
     WEBSEEDS=${WEBSEEDS%,} # delete , at the end
     mktorrent -v  \
             -a "udp://tracker.opentrackr.org:1337/announce" \
             -a "udp://tracker.coppersurfer.tk:6969/announce"  \
             -l 20 -c "$COMMENT" -w $WEBSEEDS          \
             -o meta/$FILE.torrent $FILE
   popd
 fi

 #if [ ! -s $METADIR/$FILE.metalink ]
 #then
 #  ~/bin/metalink --alldigests $f < ../metalink.helper > $METADIR/$FILE.metalink

 #  # insert link to torrent file
 #  # finds first line with <url> in xml, inserts a torrent file, then copies back the tmp file
 #  # fixes <file name="path .. filename"> tag by removing the subdir
 #  insert='<url type="bittorrent" preference="100">http://sagemath.org/mirror/'$TORFILE'</url>'
 #  first_url=True
 #  first_name=True
 #  while read line; do
 #    if [[ $first_name == True && "$line" =~ "<file name=" ]] ; then
 #      # assuming this string:
 #      # <file name="linux/32bit/sage-4.1.1-linux-Fedora_release_10_Cambridge-i686-Linux.tar.gz">
 #      # wrong
 #      # t=$(( ${#DIR} + 13 ))
 #      #echo ${line:0:12}${line:$t}
 #      echo '<file name="'$FILE'">'
 #      first_name=False
 #    else 
 #      echo "$line"
 #    fi

 #    if [[ $first_url == True && "$line" =~ "<url" ]] ; then
 #      echo $insert
 #      first_url=False
 #    fi
 #  done < $METADIR/$FILE.metalink > $METADIR/tmp
 #  mv -f $METADIR/tmp $METADIR/$FILE.metalink
 #fi 

done
