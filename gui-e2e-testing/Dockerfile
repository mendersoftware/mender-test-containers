FROM alpine:3.21.2 as mender-artifact-get
ARG TARGETARCH
# TODO: update to mender-artifact 4.0.0 after the release
ARG MENDER_ARTIFACT_VERSION=4.0.0-build5-1+ubuntu+noble
RUN apk --no-cache add dpkg zstd
RUN deb_filename=mender-artifact_${MENDER_ARTIFACT_VERSION}_${TARGETARCH}.deb && \
    wget "https://downloads.mender.io/repos/debian/pool/main/m/mender-artifact/${deb_filename}" \
    --output-document=/mender-artifact.deb && dpkg-deb --extract /mender-artifact.deb /

FROM mcr.microsoft.com/playwright:v1.50.1
WORKDIR /e2e
ENV CI=1
ADD https://dgsbl4vditpls.cloudfront.net/mender-demo-artifact.mender ./
ADD https://raw.githubusercontent.com/mendersoftware/gui/master/tests/e2e_tests/package.json ./
ADD https://raw.githubusercontent.com/mendersoftware/gui/master/tests/e2e_tests/package-lock.json ./
COPY --from=mender-artifact-get /usr/bin/mender-artifact /usr/bin/mender-artifact
RUN npm ci && npx playwright install
