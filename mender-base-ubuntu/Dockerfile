FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=non-interactive

RUN apt update && \
    apt install -yyq \
    curl jq python3-pip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://downloads.mender.io/repos/debian/gpg | tee /etc/apt/trusted.gpg.d/mender.asc && \
    echo "deb [arch=$(dpkg --print-architecture)] https://downloads.mender.io/repos/workstation-tools ubuntu/noble/stable main" | tee /etc/apt/sources.list.d/mender.list && \
    apt update && \
    apt install --assume-yes --quiet mender-artifact && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mender-artifact --version
