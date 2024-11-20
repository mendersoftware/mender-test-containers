ARG DISTRO=debian
ARG RELEASE=bookworm
FROM $DISTRO:$RELEASE

COPY requirements.txt .
RUN export DEBIAN_FRONTEND=noninteractive && \
    apt-get update && \
	apt-get install -y $(cat requirements.txt)

ARG ARCH=amd64
ARG DISTRO=debian
ARG RELEASE=bookworm

RUN if [ "${DISTRO}" = "ubuntu" -a "${ARCH}" != "amd64" ]; then \
        # Unlike Debian, Ubuntu has separate repositories for the Primary Architectures (amd64, i386)
        # and the Ports (arm64, armhf, among others). The following commands will set the deafult
        # sources to only be used for native packages (amd64) and then add ports.ubuntu.com repos
        # for the foreign architecture. See:
        # https://wiki.ubuntu.com/UbuntuDevelopment/PackageArchive#Ports
        #
        # Newer Ubuntu distros use deb822 format in ubuntu.sources,
        # otherwise use the old one-line format in sources.list
        if [ -f "/etc/apt/sources.list.d/ubuntu.sources" ]; then \
            sed -i '/Types: deb/a Architectures: amd64' /etc/apt/sources.list.d/ubuntu.sources; \
        else \
            sed -i 's/^deb/deb [arch=amd64]/' /etc/apt/sources.list; \
        fi; \
        # Now add the repositories for the foreign architecture
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
