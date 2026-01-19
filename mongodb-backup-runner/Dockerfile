FROM debian:bookworm
LABEL REFRESHED_AT=20260118
# image used inside Gitlab CICD Pipelines
# specifically, sre-tools mongodb backup pipelines

ENV RELEASE_NAME bookworm

# OS depenencies
RUN apt-get update && \
    apt-get -y upgrade && \
    apt-get install -y \
       awscli \
       curl \
       jq \
       ca-certificates \
       apt-transport-https \
       lsb-release \
       gnupg

RUN mkdir -p /etc/apt/keyrings \
      && curl -sLS "https://packages.microsoft.com/keys/microsoft.asc" \
        | gpg --dearmor \
        | tee /etc/apt/keyrings/microsoft.gpg > /dev/null \
      && chmod go+r /etc/apt/keyrings/microsoft.gpg \
      && echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/microsoft.gpg] https://packages.microsoft.com/repos/azure-cli/ ${RELEASE_NAME} main" \
        | tee /etc/apt/sources.list.d/azure-cli.list

RUN apt-get update && \
    apt-get install -y \
       azure-cli \
    && rm -rf /var/lib/apt/lists/*
