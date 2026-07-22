FROM python:slim-trixie
LABEL REFRESHED_AT=20260717
# image used inside Gitlab CICD Pipelines and by the staging-db-cleanup k8s cronjob

# Application list
ARG KUBECTL_VERSION=1.36.2
ARG MONGOSH_VERSION=2.9.2

# env
ENV BIN_DIR=/opt/builder/bin
ENV USER=builder

# OS depenencies
RUN apt-get update && \
    apt-get -y upgrade && \
    apt-get install -y \
       curl \
       apt-transport-https \
       ca-certificates \
       gnupg \
       jq \
       unzip \
    && rm -rf /var/lib/apt/lists/*

# workdir
RUN useradd -ms /bin/bash ${USER} -d /opt/${USER}
WORKDIR ${BIN_DIR}
ENV PATH="${BIN_DIR}:${PATH}"

# kubectl
RUN curl -o ${BIN_DIR}/kubectl -L -s "https://dl.k8s.io/release/v${KUBECTL_VERSION}/bin/linux/amd64/kubectl" \
    && KUBECTL_BIN="${BIN_DIR}/kubectl" \
    && chmod +x ${KUBECTL_BIN} \
    && curl -o ${BIN_DIR}/kubectl.sha256 -L -s "https://dl.k8s.io/release/v${KUBECTL_VERSION}/bin/linux/amd64/kubectl.sha256" \
    && echo "$(cat ${KUBECTL_BIN}.sha256) ${KUBECTL_BIN}" | sha256sum --check \
    && echo "INFO - kubectl version: " \
    && ${KUBECTL_BIN} version --client \
    && rm ${BIN_DIR}/kubectl.sha256 \
    && chown ${USER}. ${KUBECTL_BIN}

# awscli install
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
    && unzip awscliv2.zip \
    && ./aws/install \
    && rm -rf awscliv2.zip aws \
    && aws --version

# mongosh - MongoDB's official apt repo (bookworm packages, compatible with this
# trixie-based image - trixie packages aren't published by MongoDB yet)
RUN curl -fsSL https://pgp.mongodb.com/server-8.0.asc \
      | gpg --dearmor -o /usr/share/keyrings/mongodb-server-8.0.gpg \
    && echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-8.0.gpg ] https://repo.mongodb.org/apt/debian bookworm/mongodb-org/8.0 main" \
      | tee /etc/apt/sources.list.d/mongodb-org-8.0.list \
    && apt-get update \
    && apt-get install -y mongodb-mongosh=${MONGOSH_VERSION} \
    && rm -rf /var/lib/apt/lists/* \
    && mongosh --version

#USER ${USER}
