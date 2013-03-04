#!/bin/bash

set -e

SVN="/usr/bin/svn"
PYTHON="/usr/bin/python26"
INPUT_DIR="/data/sync/input/src/django/input.mozilla.com/reporter"
VENDOR_DIR="$INPUT_DIR/vendor"

# update locales
pushd locale > /dev/null
$SVN revert -R .
#$SVN up
./compile-mo.sh .
popd > /dev/null

#update vendor
echo -e "Updating vendor..."
cd $VENDOR_DIR
git pull
git submodule sync
git submodule update --init --recursive

# update input.mozilla.org code in src tree
echo -e "Updating reporter..."
cd $INPUT_DIR
git pull origin master 

# sync to www tree, which web servers get, without .git* and .svn*
/usr/bin/rsync -aq --exclude '.git*' --delete /data/sync/input/src/ /data/sync/input/www/

# compress assets
$PYTHON $INPUT_DIR/manage.py compress_assets

# check if static dir exists, make if nto
if [ ! -d $INPUT_DIR/static ]; then
    echo "making static dir"
    mkdir -p $INPUT_DIR/static
fi

# collect static assets to static/
$PYTHON $INPUT_DIR/manage.py collectstatic --noinput --clear

# commit to git for web servers to pull from
cd /data/sync/input/www/
git commit -a -m "push to prod"

issue-multi-command input /data/bin/libget/get-php5-www-git.sh
sleep 60
issue-multi-command input service httpd restart
