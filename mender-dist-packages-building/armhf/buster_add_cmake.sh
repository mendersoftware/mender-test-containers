#!/bin/bash

set -e

# v3.21 is the oldest version that we can build from source in QEMU armhf. See:
# https://gitlab.kitware.com/cmake/cmake/-/issues/22328
CMAKE_VERSION="v3.21.6"
_CMAKE_VERSION=$(echo "$CMAKE_VERSION" | sed 's/v//')

# Remove buster's upstream cmake
apt-get remove --assume-yes cmake cmake-data

# Build cmake from source
wget https://github.com/Kitware/CMake/releases/download/$CMAKE_VERSION/cmake-$_CMAKE_VERSION.tar.gz
tar -xf cmake-$_CMAKE_VERSION.tar.gz
cd cmake-$_CMAKE_VERSION
./bootstrap --parallel=$(nproc --all)
make --jobs=$(nproc --all)
make install
cd ..
rm -rf cmake-$_CMAKE_VERSION
