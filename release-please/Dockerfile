FROM node:22
LABEL REFRESHED_AT=20241112
# image used inside Gitlab CICD Pipelines

# release-please
RUN npm install -g release-please

# github cli
RUN mkdir -p -m 755 /etc/apt/keyrings \
    && wget -qO- https://cli.github.com/packages/githubcli-archive-keyring.gpg | tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null \
    && chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null
RUN apt-get update && \
    apt-get -y upgrade && \
    apt-get install -y \
       gh \
       jq \
    && rm -rf /var/lib/apt/lists/*

# git-cliff
# pin to 2.8.0 as 2.9.0 has breaking changes
# https://northerntech.atlassian.net/browse/QA-1148
RUN npm install -g git-cliff@2.8.0
