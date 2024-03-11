ARG DISTRO=debian
ARG RELEASE=buster
FROM $DISTRO:$RELEASE

COPY requirements.txt .
RUN export DEBIAN_FRONTEND=noninteractive && \
    apt-get update && \
	apt-get install -y $(cat requirements.txt)

ARG ARCH=amd64
ARG DISTRO=debian
ARG RELEASE=buster

RUN if [ "${DISTRO}" = "ubuntu" -a "${ARCH}" != "amd64" ]; then \
        sed -i 's/^deb/deb [arch=amd64]/' /etc/apt/sources.list && \
        touch /etc/apt/sources.list.d/ports.list && \
        echo "deb [arch=$ARCH] http://ports.ubuntu.com/ubuntu-ports/ $RELEASE main restricted universe multiverse" > /etc/apt/sources.list.d/ports.list && \
        echo "deb [arch=$ARCH] http://ports.ubuntu.com/ubuntu-ports/ $RELEASE-updates main restricted universe multiverse" >> /etc/apt/sources.list.d/ports.list && \
        echo "deb [arch=$ARCH] http://ports.ubuntu.com/ubuntu-ports/ $RELEASE-backports main restricted universe multiverse" >> /etc/apt/sources.list.d/ports.list && \
        echo "deb [arch=$ARCH] http://ports.ubuntu.com/ubuntu-ports/ $RELEASE-security main restricted universe multiverse" >> /etc/apt/sources.list.d/ports.list; \
    fi

RUN dpkg --add-architecture ${ARCH} && \
    apt-get update

RUN if ! [ "${DISTRO}" = "debian" -a "${ARCH}" = "armhf" ]; then \
        apt-get install -y \
        pkg-config \
        liblzma-dev:${ARCH} \
        libssl-dev:${ARCH} \
        libglib2.0-dev:${ARCH} \
        libmount-dev:${ARCH} \
        libc-dev:${ARCH} \
        libc6-dev:${ARCH} \
        linux-libc-dev:${ARCH} \
        ; \
    fi

RUN if [ "${ARCH}" = "arm64" ]; then \
        apt-get install -y gcc-aarch64-linux-gnu; \
    fi

RUN if [ "${ARCH}" = "armhf" -a "${DISTRO}" != "debian" ]; then \
        apt-get install -y gcc-arm-linux-gnueabihf; \
    fi
