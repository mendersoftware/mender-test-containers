FROM debian:13-slim
LABEL REFRESHED_AT=20240613
# image used inside Gitlab CICD Pipelines
# to test terraform with trivy

# Application list
ENV TERRAGRUNT_VERSION=0.59.3
ENV TRIVY_VERSION=0.65.0

# env
ENV BIN_DIR=/opt/builder/bin
ENV USER=builder

# OS dependencies
RUN apt-get update && apt-get install -y \
  git \
  curl \
  wget \
  sed \
  unzip \
  gnupg \
  make \
  apt-transport-https \
  lsb-release \
  && rm -rf /var/lib/apt/lists/*

# workdir
RUN useradd -ms /bin/bash ${USER} -d /opt/${USER}
WORKDIR ${BIN_DIR}

#
# Install terraform
#
RUN wget -O- https://apt.releases.hashicorp.com/gpg | \
  gpg --dearmor | \
  tee /usr/share/keyrings/hashicorp-archive-keyring.gpg > /dev/null

RUN echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] \
  https://apt.releases.hashicorp.com $(lsb_release -cs) main" | \
  tee /etc/apt/sources.list.d/hashicorp.list

RUN apt-get update && \
  apt-get install -y terraform && \
  rm -rf /var/lib/apt/lists/*


#
# Install terragrunt
#
RUN curl -o ${BIN_DIR}/terragrunt -L -s "https://github.com/gruntwork-io/terragrunt/releases/download/v${TERRAGRUNT_VERSION}/terragrunt_linux_amd64" \
  && TERRAGRUNT_BIN="${BIN_DIR}/terragrunt" \
  && chmod +x ${TERRAGRUNT_BIN} \
  && ${TERRAGRUNT_BIN} -version \
  && chown ${USER}. ${TERRAGRUNT_BIN}

#
# Install Trivy
#
RUN wget https://github.com/aquasecurity/trivy/releases/download/v${TRIVY_VERSION}/trivy_${TRIVY_VERSION}_Linux-64bit.deb \
  && dpkg -i trivy_${TRIVY_VERSION}_Linux-64bit.deb

USER ${USER}
ENV PATH="${BIN_DIR}:${PATH}"
