FROM golang:1.26

LABEL REFRESHED_AT=20260615

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

# JUnit test-report formatter (pinned; Renovate-tracked)
RUN go install github.com/jstemmer/go-junit-report@v1.0.0

# Smoke check: every baked tool must be present at build time
RUN go version && \
    command -v go-junit-report && \
    pkg-config --exists glib-2.0 && \
    dpkg -s liblzma-dev libssl-dev e2tools dbus > /dev/null
