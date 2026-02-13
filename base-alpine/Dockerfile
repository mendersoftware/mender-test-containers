FROM alpine:3.22.1

LABEL REFRESHED_AT=20260211

# Don't slow down aws cli commands with connections to IMDS: we're not in AWS
ENV AWS_EC2_METADATA_DISABLED=true

RUN apk add --no-cache \
        ca-certificates \
        curl \
        wget \
        git \
        bash \
        jq \
        build-base \
        make \
        findutils \
        coreutils \
        gettext \
        aws-cli

RUN curl --version && \
    wget --version && \
    git --version && \
    bash --version && \
    jq --version && \
    make --version && \
    aws --version
