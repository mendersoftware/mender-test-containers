# Base matches the acceptance job's current image (docker CLI + dind entrypoint)
FROM docker:27-dind

LABEL REFRESHED_AT=20260630

# Acceptance test system packages (was: apk add ... in mender-cli/.gitlab-ci.yml).
# `apk upgrade` keeps freshly-installed packages from diverging from base ones.
RUN apk upgrade --no-cache && \
    apk add --no-cache \
        bash cmake curl dpkg e2fsprogs-extra g++ gcompat git iptables jq \
        libffi-dev make openssh-client py3-pip python3-dev zstd screen \
        openssl-dev openssl-libs-static

# Pre-compile uamqp (the flakiest step: builds a C wheel from source at runtime today)
RUN CFLAGS="-Wno-error=incompatible-pointer-types" CMAKE_POLICY_VERSION_MINIMUM=3.5 \
        pip install uamqp --break-system-packages

# Smoke check: the baked tools and the compiled uamqp must be importable at build time
RUN docker --version && \
    python3 -c "import uamqp; print('uamqp', uamqp.__version__)" && \
    cmake --version && g++ --version
