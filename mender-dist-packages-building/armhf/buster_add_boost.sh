#!/bin/bash

set -e

BOOST_VERSION="1.84.0"
_BOOST_VERSION=$(echo "$BOOST_VERSION" | sed 's/\./_/g')

# Build boost log from source
wget https://boostorg.jfrog.io/artifactory/main/release/$BOOST_VERSION/source/boost_$_BOOST_VERSION.tar.bz2
tar --bzip2 -xf boost_$_BOOST_VERSION.tar.bz2 
cd boost_$_BOOST_VERSION
export BOOST_ROOT=/usr/local/boost_$_BOOST_VERSION
./bootstrap.sh  --with-libraries=[log]
./b2 install --with-log link=static
