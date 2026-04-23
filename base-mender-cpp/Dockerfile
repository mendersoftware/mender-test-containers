FROM debian:13

ARG MENDER_ARTIFACT_VERSION=4.4.0
ENV DEBIAN_FRONTEND=non-interactive

RUN apt update && \
    apt install -yyq \
    ccache clang cmake git g++ make pkg-config lcov \
    liblmdb++-dev libboost-dev libboost-log-dev libssl-dev libarchive-dev libdbus-1-dev \
    curl dbus stunnel4 tinyproxy-bin netcat-openbsd wget zstd xz-utils && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN wget "https://downloads.mender.io/repos/workstation-tools/pool/main/m/mender-artifact/mender-artifact_${MENDER_ARTIFACT_VERSION}-1%2bdebian%2btrixie_amd64.deb" \
      --output-document mender-artifact.deb && \
    apt-get update && \
    apt install --assume-yes --quiet ./mender-artifact.deb && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mender-artifact --version
