FROM ubuntu:26.04

ARG QEMU_VERSION="11.0.3"

ENV DEBIAN_FRONTEND=noninteractive
ENV PIP_BREAK_SYSTEM_PACKAGES=1

# prepare NFS cache for yocto
RUN mkdir -p /mnt/sstate-cache

# install pyyaml via pip to workardound a later conflict if installed via OS package (awscli depends on python3-yaml)
RUN apt-get update -qq && apt-get install -yyq python3-pip && pip3 install --ignore-installed --upgrade pip && pip3 install pyyaml

# Get OS requirements from master
RUN apt-get install -yyq wget && \
    wget https://raw.githubusercontent.com/mendersoftware/meta-mender/master/tests/acceptance/requirements_deb.txt && \
    apt-get install -yyq $(cat requirements_deb.txt) xz-utils && \
    apt-get remove -yyq docker docker.io containerd runc && apt-get install -yyq ca-certificates curl gnupg lsb-release unzip && \
    mkdir -p /etc/apt/keyrings && curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null && \
    apt-get update -qq && apt-get install -yyq docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Ubuntu 26.04 defaults to sudo-rs, which ignores 'sudo -E' (used by mender-qa
# to preserve WORKSPACE etc. when dropping to the mender user). Use classic sudo.
RUN update-alternatives --set sudo /usr/bin/sudo.ws

# QA-1690: qemu >= 8.2.1 breaks buffered writes to the emulated NOR flash,
# turning the UBIFS data partition read-only on vexpress-qemu-flash. Build the
# current release with a one-line fix (see the patch file) into /usr/local/bin.
COPY qemu-pflash-count0-fix.patch /tmp/
RUN apt-get install -yq ninja-build pkg-config libglib2.0-dev libpixman-1-dev \
        libslirp-dev libfdt-dev python3-venv && \
    wget -qO- https://download.qemu.org/qemu-${QEMU_VERSION}.tar.xz | tar xJ && \
    cd qemu-${QEMU_VERSION} && \
    patch -p1 --fuzz=0 < /tmp/qemu-pflash-count0-fix.patch && \
    ./configure --target-list=arm-softmmu --enable-slirp --disable-docs --disable-tools && \
    make -j$(nproc) && make install && \
    cd .. && rm -rf qemu-${QEMU_VERSION}

RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-$(uname -m).zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install && \
    rm -rf awscliv2.zip aws

# Locales
RUN locale-gen --purge en_US.UTF-8
ENV LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8 LANGUAGE=en_US.UTF-8

# Python 3 requirements from master
RUN wget https://raw.githubusercontent.com/mendersoftware/meta-mender/master/tests/acceptance/requirements_py3.txt && \
    pip3 install -r requirements_py3.txt --ignore-installed && \
    rm requirements_py3.txt

# mender user dir
RUN useradd -m -u 1010 mender && usermod -a -G kvm mender && usermod -a -G docker mender

# Prepare mender user
RUN mkdir -p /home/mender/.ssh && echo "mender ALL=(ALL:ALL) NOPASSWD:ALL" >> /etc/sudoers && sed -i -e 's/^\( *Defaults *requiretty *\)$/# \1/' /etc/sudoers && chown -R mender:mender /home/mender

# debugfs
RUN cp /sbin/debugfs /usr/bin/ || echo "debugfs not in /sbin/"

# enable sysstat monitoring suite for Debian/Ubuntu
RUN sed -i 's/false/true/g' /etc/default/sysstat
