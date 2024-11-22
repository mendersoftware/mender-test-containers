#!/bin/bash

set -e

build_arguments="Arguments: \n\
    --container-tag \n\
    --distro \n\
    --release \n\
    --arch \n\
    --ci-pipeline-id"

if [ "$#" -eq 0 ]; then
    echo -e "No arguments provided.\n$build_arguments"
    exit 1
fi

options=$(getopt --long help,container-tag:,distro:,release:,arch:,ci-pipeline-id: -n "$0" -- "" "$@")
eval set -- "$options"

while [[ $1 != -- ]]; do
    case "$1" in
        --help ) echo -e $build_arguments ; shift 2 ; exit 1 ;;
        --container-tag ) CONTAINER_TAG="$2"; shift 2 ;;
        --distro ) DISTRO="$2"; shift 2 ;;
        --release ) RELEASE="$2"; shift 2 ;;
        --arch ) ARCH="$2"; shift 2 ;;
        --ci-pipeline-id) CI_PIPELINE_ID="$2"; shift 2 ;;
        *) echo Invalid argument $1 ; exit 1;;
    esac
done

required_arguments=true
for var in CONTAINER_TAG DISTRO RELEASE ARCH CI_PIPELINE_ID; do
    if [ -z "${!var}" ]; then
        required_arguments=false
        echo -e "Variable $var not set."
    fi
done
export CONTAINER_TAG DISTRO RELEASE ARCH CI_PIPELINE_ID

if [ $required_arguments == false ]; then
    echo -e "Provide the following arguments:\n$build_arguments"
    exit 1
fi

if [ "$DISTRO" = "raspberrypios" -a "$ARCH" = "armhf" ]; then
    # Move requirements.txt to be in correct build context
    cp requirements.txt armhf/

    # Build an image to boostrap raspian
    docker build \
        --tag mkimage \
        --build-arg RELEASE \
        --file armhf/Dockerfile.bootstrap \
        armhf

    # Run a bootstrap-container and extract the rootfs.tar.xz
    docker run \
        --rm \
        --volume \
        $(pwd)/armhf/output:/copy \
        --entrypoint bash \
        mkimage \
        -c "cp /output/rootfs.tar.xz /copy"
     
    # Build armhf with the boostrapped os
    docker build \
        --cache-from ${CONTAINER_TAG}-master \
        --tag ${CONTAINER_TAG}-${CI_PIPELINE_ID} \
        --platform=linux/arm/v6 \
        --build-arg RELEASE \
        --file armhf/Dockerfile.rpi \
        --push \
        armhf

elif [ "$DISTRO" = "debian" -o "$DISTRO" = "ubuntu" ]; then
    docker build \
        --cache-from ${CONTAINER_TAG}-master \
        --tag ${CONTAINER_TAG}-${CI_PIPELINE_ID} \
        --build-arg DISTRO \
        --build-arg RELEASE \
        --build-arg ARCH \
        --push \
        .

else
    echo "Combination of DISTRO '$DISTRO' and ARCH '$ARCH' is not supported"
    exit 1
fi
