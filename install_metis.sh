#!/bin/bash

ROOT="$(git rev-parse --show-toplevel)"
PREFIX="${ROOT}/metis"
BUILD_DIR="$(mktemp -d -p "/tmp/$(whoami)")"

mkdir -p "$BUILD_DIR"

pushd "$BUILD_DIR" || exit

git clone https://github.com/KarypisLab/GKlib.git
pushd GKlib || exit
make config prefix=$PREFIX
make -j install
popd || exit

git clone https://github.com/KarypisLab/METIS.git
pushd METIS || exit
make config prefix=$PREFIX
make -j install
popd || exit

popd || exit
