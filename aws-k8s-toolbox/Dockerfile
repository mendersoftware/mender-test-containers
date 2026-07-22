FROM python:slim-trixie
LABEL REFRESHED_AT=20260118
# image used inside Gitlab CICD Pipelines

# Application list
ARG KUBECTL_VERSION=1.36.2
ARG HELM_VERSION=v3.18.6
ARG HELM_UNITTEST_VERSION=1.1.0
ARG KUBECONFORM_VERSION=0.8.0
ARG PLUTO_VERSION=5.24.0
ARG TRIVY_VERSION=0.70.0
ARG YQ_VERSION=4.53.3

# env
ENV BIN_DIR=/opt/builder/bin
ENV USER=builder

# OS depenencies
RUN apt-get update && \
    apt-get -y upgrade && \
    apt-get install -y \
       curl \
       wget \
       git \
       apt-transport-https \
       ca-certificates \
       gnupg \
       jq \
       unzip \
       make \
       uuid-runtime \
       dnsutils \
    && rm -rf /var/lib/apt/lists/*

# workdir
RUN useradd -ms /bin/bash ${USER} -d /opt/${USER}
WORKDIR ${BIN_DIR}
ENV PATH="${BIN_DIR}:${PATH}"

# kubectl
RUN curl -o ${BIN_DIR}/kubectl -L -s "https://dl.k8s.io/release/v${KUBECTL_VERSION}/bin/linux/amd64/kubectl" \
    && KUBECTL_BIN="${BIN_DIR}/kubectl" \
    && chmod +x ${KUBECTL_BIN} \
    && curl -o ${BIN_DIR}/kubectl.sha256 -L -s "https://dl.k8s.io/release/v${KUBECTL_VERSION}/bin/linux/amd64/kubectl.sha256" \
    && echo "$(cat ${KUBECTL_BIN}.sha256) ${KUBECTL_BIN}" | sha256sum --check \
    && echo "INFO - kubectl version: " \
    && ${KUBECTL_BIN} version --client \
    && rm ${BIN_DIR}/kubectl.sha256 \
    && chown ${USER}. ${KUBECTL_BIN}
    
# helm
ENV HELM3_DOWNLOAD_URL=https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3
RUN curl -fsSL -o ${BIN_DIR}/get_helm.sh ${HELM3_DOWNLOAD_URL} \
    && chmod 700 ${BIN_DIR}/get_helm.sh \
    && DESIRED_VERSION=${HELM_VERSION} ${BIN_DIR}/get_helm.sh \
    # test it
    && HELM_BIN_TEMP=$(which helm) \
    && HELM_BIN=${BIN_DIR}/helm \
    && mv ${HELM_BIN_TEMP} ${HELM_BIN} \
    && ${HELM_BIN} version \
    && rm ${BIN_DIR}/get_helm.sh \
    && chown ${USER}. ${HELM_BIN}

# helm-unittest plugin
RUN helm plugin install https://github.com/helm-unittest/helm-unittest --version v${HELM_UNITTEST_VERSION}

# eskctl
RUN ARCH=amd64 \
    ; PLATFORM=$(uname -s)_$ARCH \
    ; curl -sLO "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$PLATFORM.tar.gz" \
    && curl -sL "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_checksums.txt" | grep $PLATFORM | sha256sum --check \
    && tar -xzf eksctl_$PLATFORM.tar.gz -C /tmp && rm eksctl_$PLATFORM.tar.gz \
    && mv /tmp/eksctl ${BIN_DIR}/

# kubeconform install
RUN curl -fsSL -o /tmp/kubeconform.tar.gz https://github.com/yannh/kubeconform/releases/download/v${KUBECONFORM_VERSION}/kubeconform-linux-amd64.tar.gz \
    && tar -xzf /tmp/kubeconform.tar.gz -C ${BIN_DIR} \
    && rm /tmp/kubeconform.tar.gz

# pluto - detect deprecated/removed Kubernetes API versions
RUN curl -fsSL -o /tmp/pluto.tar.gz \
      "https://github.com/FairwindsOps/pluto/releases/download/v${PLUTO_VERSION}/pluto_${PLUTO_VERSION}_linux_amd64.tar.gz" \
    && tar -xzf /tmp/pluto.tar.gz -C ${BIN_DIR} pluto \
    && rm /tmp/pluto.tar.gz \
    && chmod +x ${BIN_DIR}/pluto \
    && ${BIN_DIR}/pluto version

# trivy - misconfiguration scanner and SBOM generator
RUN curl -fsSL -o /tmp/trivy.tar.gz \
      "https://github.com/aquasecurity/trivy/releases/download/v${TRIVY_VERSION}/trivy_${TRIVY_VERSION}_Linux-64bit.tar.gz" \
    && tar -xzf /tmp/trivy.tar.gz -C ${BIN_DIR} trivy \
    && rm /tmp/trivy.tar.gz \
    && ${BIN_DIR}/trivy version

# awscli install
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
    && unzip awscliv2.zip \
    && ./aws/install \
    && aws --version

# yq
RUN wget https://github.com/mikefarah/yq/releases/download/v${YQ_VERSION}/yq_linux_amd64.tar.gz -O - | tar xz \
    && mv ./yq_linux_amd64 ./yq

#USER ${USER}
