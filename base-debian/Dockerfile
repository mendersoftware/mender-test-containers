FROM debian:trixie-20260202-slim

LABEL REFRESHED_AT=20260211

# Don't slow down aws cli commands with connections to IMDS: we're not in AWS
ENV AWS_EC2_METADATA_DISABLED=true

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        wget \
        git \
        bash \
        jq \
        build-essential \
        make \
        gettext-base \
        unzip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install AWS CLI v2
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-$(uname -m).zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install && \
    rm -rf awscliv2.zip aws

RUN curl --version && \
    wget --version && \
    git --version && \
    bash --version && \
    jq --version && \
    make --version && \
    aws --version
