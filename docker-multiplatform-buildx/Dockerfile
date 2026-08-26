FROM docker:git

RUN apk add \
      --no-cache \
      curl

#
# Install regclient
# for re-tagging multi-platform images
#
RUN curl --fail --silent --show-error --location \
      --output /usr/local/bin/regctl \
      https://github.com/regclient/regclient/releases/latest/download/regctl-linux-amd64 \
      && chmod 755 /usr/local/bin/regctl \
      && regctl version
