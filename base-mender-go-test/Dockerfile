FROM golang:1.26

LABEL REFRESHED_AT=20260702

ENV DEBIAN_FRONTEND=noninteractive

# Common Go compile dependencies (union of deb-requirements.txt across Mender Go repos)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libglib2.0-dev \
        liblzma-dev \
        libssl-dev \
        dbus \
        e2tools && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Test runner that emits JUnit + coverage; actively maintained (pinned; Renovate-tracked)
RUN go install gotest.tools/gotestsum@v1.13.0

# Smoke check: every baked tool must be present at build time
RUN go version && \
    command -v gotestsum && \
    pkg-config --exists glib-2.0 && \
    dpkg -s liblzma-dev libssl-dev e2tools dbus > /dev/null
