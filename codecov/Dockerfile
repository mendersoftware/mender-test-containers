FROM alpine:3.24.1

LABEL REFRESHED_AT=20260730

ARG CODECOV_CLI_VERSION=11.3.1

ARG TARGETARCH

RUN apk add --no-cache \
        ca-certificates \
        curl \
        git

RUN case "${TARGETARCH}" in \
        amd64) CODECOV_PLATFORM=alpine ;; \
        arm64) CODECOV_PLATFORM=alpine-arm64 ;; \
        *) echo "unsupported architecture: ${TARGETARCH}" && exit 1 ;; \
    esac && \
    curl -fsSLO "https://cli.codecov.io/v${CODECOV_CLI_VERSION}/${CODECOV_PLATFORM}/codecov" && \
    curl -fsSLO "https://cli.codecov.io/v${CODECOV_CLI_VERSION}/${CODECOV_PLATFORM}/codecov.SHA256SUM" && \
    sha256sum -c codecov.SHA256SUM && \
    chmod +x codecov && \
    mv codecov /usr/local/bin/codecov && \
    rm codecov.SHA256SUM

RUN codecov --version
