FROM python:3.12.5-slim-bookworm AS python-source

FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

# prepare NFS cache for yocto
RUN mkdir -p /mnt/sstate-cache

# OS requirements from master
RUN apt-get update -qq && apt-get install -yyq wget && \
    wget https://raw.githubusercontent.com/mendersoftware/meta-mender/master/tests/acceptance/requirements_deb.txt && \
    apt-get install -yyq $(cat requirements_deb.txt) && \
    rm requirements_deb.txt

# Install kernel modules for KVM.
RUN apt-get install -yq linux-modules-$(uname -r)

# Install Docker Engine as per official instructions. See https://docs.docker.com/engine/install/ubuntu/
RUN for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc; do \
        apt-get remove -yyq $pkg; done && \
    apt-get update -qq && \
    apt-get install -yyq ca-certificates curl  && \
    install -m 0755 -d /etc/apt/keyrings  && \
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc  && \
    chmod a+r /etc/apt/keyrings/docker.asc && \
    echo \
        "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
        $(. /etc/os-release && echo "$VERSION_CODENAME") stable" > /etc/apt/sources.list.d/docker.list && \
    apt-get update -qq && \
    apt-get install -yyq docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Python requirements from master
# Use a local instalation of Python to avoid collisions with Debian native packages. See PEP 668.
COPY --from=python-source /usr/local /usr/local
RUN wget https://raw.githubusercontent.com/mendersoftware/meta-mender/master/tests/acceptance/requirements_py3.txt && \
    pip install --requirement requirements_py3.txt && \
    rm requirements_py3.txt

# Locales
RUN locale-gen --purge en_US.UTF-8
ENV LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8 LANGUAGE=en_US.UTF-8

# mender user
RUN useradd -m -u 1010 mender && usermod -a -G kvm mender && usermod -a -G docker mender
RUN mkdir -p /home/mender/.ssh && echo "mender ALL=(ALL:ALL) NOPASSWD:ALL" >> /etc/sudoers && sed -i -e 's/^\( *Defaults *requiretty *\)$/# \1/' /etc/sudoers && chown -R mender:mender /home/mender

# debugfs
RUN cp /sbin/debugfs /usr/bin/

# enable sysstat monitoring suite for Debian/Ubuntu
RUN sed -i 's/false/true/g' /etc/default/sysstat
