FROM alpine:3.20.3

# Docker image to emulate Rasperry Pi OS bullseye image with QEMU. See:
# https://github.com/dhruvvyas90/qemu-rpi-kernel/

EXPOSE 8822

ARG raspios_version
RUN test -n "${raspios_version}" || (echo "Argument 'raspios_version' is mandatory." && exit 1)
ENV version=${raspios_version}

RUN mkdir /testing

RUN apk add --no-cache qemu-system-arm

COPY ${version}-raspios-bullseye-armhf-lite-mender-testing.img /testing/

RUN wget -q -nc -P /testing \
    https://github.com/dhruvvyas90/qemu-rpi-kernel/raw/master/kernel-qemu-5.10.63-bullseye \
    https://github.com/dhruvvyas90/qemu-rpi-kernel/raw/master/versatile-pb-bullseye-5.10.63.dtb

ENTRYPOINT /usr/bin/qemu-system-arm -kernel /testing/kernel-qemu-5.10.63-bullseye \
           -dtb /testing/versatile-pb-bullseye-5.10.63.dtb -m 256 -M versatilepb \
           -cpu arm1176 -nographic -append \
           "rw console=ttyAMA0 root=/dev/sda2 rootfstype=ext4 loglevel=8 rootwait fsck.repair=yes memtest=1" \
           -drive file=/testing/${version}-raspios-bullseye-armhf-lite-mender-testing.img,format=raw \
           -device virtio-net-pci,netdev=unet \
           -netdev user,id=unet,hostfwd=tcp::8822-:22
