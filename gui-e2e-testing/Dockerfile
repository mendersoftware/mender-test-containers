FROM alpine:3.23.3 AS mender-artifact-get
ARG TARGETARCH
ARG MENDER_ARTIFACT_VERSION=4.4.0-1+ubuntu+noble
RUN apk --no-cache add dpkg zstd
RUN deb_filename=mender-artifact_${MENDER_ARTIFACT_VERSION}_${TARGETARCH}.deb && \
    wget "https://downloads.mender.io/repos/workstation-tools/pool/main/m/mender-artifact/${deb_filename}" \
    --output-document=/mender-artifact.deb && dpkg-deb --extract /mender-artifact.deb /

FROM mcr.microsoft.com/playwright:v1.59.1

ARG DOCKER_VERSION=29.1
RUN install -m 0755 -d /etc/apt/keyrings && \
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc && \
    chmod a+r /etc/apt/keyrings/docker.asc && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] \
      https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" \
      > /etc/apt/sources.list.d/docker.list && \
    apt-get update && \
    DOCKER_PKG_VERSION=$(apt-cache madison docker-ce-cli | awk -F'|' '/'"${DOCKER_VERSION}"'/ {gsub(/ /, "", $2); print $2; exit}') && \
    apt-get install -y --no-install-recommends docker-ce-cli=${DOCKER_PKG_VERSION} docker-buildx-plugin docker-compose-plugin && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /e2e
ENV CI=1
ADD https://dgsbl4vditpls.cloudfront.net/mender-demo-artifact.mender ./
ADD https://raw.githubusercontent.com/mendersoftware/gui/master/tests/e2e_tests/package.json ./
ADD https://raw.githubusercontent.com/mendersoftware/gui/master/tests/e2e_tests/package-lock.json ./
COPY --from=mender-artifact-get /usr/bin/mender-artifact /usr/bin/mender-artifact
RUN npm ci && npx playwright install chromium
