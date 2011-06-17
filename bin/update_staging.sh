#!/bin/bash

# Update script for staging server. Takes care of updating code repo, vendor
# dir, and running DB migrations.

HERE=`dirname $0`
GIT=`which git`
SVN=`which svn`
PYTHON=`which python2.6`

pushd "$HERE/../" > /dev/null

# update locales
pushd locale > /dev/null
$SVN revert -R .
$SVN up
./compile-mo.sh .
popd > /dev/null

# pull actual code
$GIT pull -q origin master
$GIT submodule update --init

# pull vendor repo
pushd vendor > /dev/null
$GIT fetch origin
NEWCODE=$($GIT diff origin/master)
$GIT pull -q origin master
$GIT submodule update --init
popd > /dev/null

if [ -n "$NEWCODE" ]
then
        # Run database migrations.
        $PYTHON vendor/src/schematic/schematic migrations/
        $PYTHON vendor/src/schematic/schematic migrations/sites

        # Pull in highcharts.src.js - our lawyers make us do this.
        $PYTHON manage.py cron get_highcharts
        # Minify assets.
        $PYTHON manage.py compress_assets
fi

# Fix mobile and desktop site domains in database. Bug 608581.
$PYTHON ./manage.py cron set_domains input.stage.mozilla.com m.input.stage.mozilla.com
popd > /dev/null
