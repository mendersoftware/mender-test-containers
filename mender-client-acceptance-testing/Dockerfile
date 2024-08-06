FROM python:3.12

ENV DEBIAN_FRONTEND=noninteractive

# prepare NFS cache for yocto
RUN mkdir -p /mnt/sstate-cache

RUN uname -r
RUN apt-get update -qq && apt-cache search linux-modules

# OS requirements from master
# linux-modules-$(uname -r | sed 's/gcp/gke/') is a workaround for https://northerntech.atlassian.net/browse/QA-597
RUN apt-get update -qq && apt-get install -yyq wget && \
    wget https://raw.githubusercontent.com/mendersoftware/meta-mender/master/tests/acceptance/requirements_deb.txt && \
    apt-get install -yyq $(cat requirements_deb.txt) && apt-get install -yq linux-modules-$(uname -r | sed 's/gcp/gke/')

# Install Docker Engine as per official instructions. See https://docs.docker.com/engine/install/debian/
RUN for pkg in docker.io docker-doc docker-compose podman-docker containerd runc; do apt-get remove -yyq $pkg; done && \
    apt-get update -qq && \
    apt-get install -yyq ca-certificates curl  && \
    install -m 0755 -d /etc/apt/keyrings  && \
    curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc  && \
    chmod a+r /etc/apt/keyrings/docker.asc  && \
    echo \
            "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian \
            $(. /etc/os-release && echo "$VERSION_CODENAME") stable" > /etc/apt/sources.list.d/docker.list && \
    apt-get update -qq && \
    apt-get install -yyq docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Python 3 requirements from master
RUN wget https://raw.githubusercontent.com/mendersoftware/meta-mender/master/tests/acceptance/requirements_py3.txt && \
    pip install -r requirements_py3.txt && \
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
