FROM docker:git

RUN apk add \
      --no-cache \
      curl

#
# Install regclient
# for re-tagging multi-platform images
#
RUN curl -L https://github.com/regclient/regclient/releases/latest/download/regctl-linux-amd64 >/usr/local/bin/regctl \
      && chmod 755 /usr/local/bin/regctl
