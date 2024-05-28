FROM alpine:3.19.1

# Docker image to emulate Raspbian stock image with QEMU. See tutorial at:
# https://github.com/wimvanderbauwhede/limited-systems/wiki/Raspbian-%22stretch%22-for-Raspberry-Pi-3-on-QEMU

EXPOSE 8822

ARG raspbian_version
RUN test -n "${raspbian_version}" || (echo "Argument 'raspbian_version' is mandatory." && exit 1)
ENV version=${raspbian_version}

RUN mkdir /testing

RUN apk add --no-cache qemu-system-arm

COPY ${version}-raspios-bullseye-armhf-lite-mender-testing.img /testing/
COPY kernel-qemu-5.10.63-bullseye /testing/
COPY versatile-pb-bullseye-5.10.63.dtb /testing/

ENTRYPOINT /usr/bin/qemu-system-arm -kernel /testing/kernel-qemu-5.10.63-bullseye \
           -dtb /testing/versatile-pb-bullseye-5.10.63.dtb -m 256 -M versatilepb \
           -cpu arm1176 -nographic -append \
           "rw console=ttyAMA0 root=/dev/sda2 rootfstype=ext4 loglevel=8 rootwait fsck.repair=yes memtest=1" \
           -drive file=/testing/${version}-raspios-bullseye-armhf-lite-mender-testing.img,format=raw \
           -device virtio-net-pci,netdev=unet \
           -netdev user,id=unet,hostfwd=tcp::8822-:22
