#!/usr/bin/env python
# After the website has been built successfully, it is in the "www" subdirectory.
# This script synchronizes this build with the Git repository at GitHub.
# From there, the website is served.

set -e

# assuming, this directory is beneath the /www directory and cd-ing there
cd `dirname "$0"`

if [ ! -d "www.git" ]; then
  mkdir www.git
  cd www.git
  git init --bare
  git remote add github git@github.com:sagemath/sagemath.github.io.git
  cd ..
fi

cd www
GIT='git --git-dir=../www.git --work-tree=.'
# now getting the info from the repository to only see the new chances
$GIT fetch github
$GIT checkout -B master
$GIT reset --soft github/master # <- non destructive
$GIT add -A -- .
$GIT commit -m "auto publish `date -u --rfc-3339=seconds`"
$GIT push github master -f

