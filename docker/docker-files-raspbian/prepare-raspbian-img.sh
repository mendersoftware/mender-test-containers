#!/bin/sh

# Downloads Raspberry Pi OS image and prepares it for testing (create user, enable SSH and add trusted key)
# Downloads also the dependencies (kernel and dtb file) for QEMU emulation

set -e -x

show_help_and_exit() {
  cat << EOF
Usage: $0 raspios-version

Arguments:
    raspios-version    - Official Raspberry Pi OS Bullseye version, for example 2023-05-03
EOF
  exit 1
}

version=""
while [ $# -gt 0 ]; do
  case "$1" in
    -*)
      echo "Error: unsupported option $1"
      show_help_and_exit_error
      ;;
    *)
      version="$1"
      shift
      ;;
  esac
done

if [ -z "$version" ]; then
	show_help_and_exit
fi

currdir=$(pwd)
scriptdir=$(cd `dirname $0` && pwd)
workdir=${currdir}/tmp-work
mkdir -p ${workdir}

raspbian_filename_zip="${version}-raspbian-buster-lite.zip"
raspbian_filename_img="${version}-raspbian-buster-lite.img"
raspbian_mender_filename_img="${version}-raspbian-mender-testing.img"

if [ -f ${currdir}/${raspbian_mender_filename_img} ]; then
    echo "Found testing image in current directory. Exiting"
    exit 0
fi

# Get superuser privileges to be able to mount the SD image
sudo true

cd ${workdir}

raspbian_url="https://downloads.raspberrypi.org/raspios_lite_armhf/images/raspios_lite_armhf-2023-05-03/2023-05-03-raspios-bullseye-armhf-lite.img.xz"
raspbian_filename_zip="2023-05-03-raspios-bullseye-armhf-lite.img.xz"
raspbian_filename_img="2023-05-03-raspios-bullseye-armhf-lite.img"
raspbian_mender_filename_img="2023-05-03-raspios-bullseye-armhf-lite-mender-testing.img"

echo "##### Downloading and extracting..."
wget -q -nc ${raspbian_url}
unxz ${raspbian_filename_zip}
wget -q -nc https://github.com/dhruvvyas90/qemu-rpi-kernel/raw/master/kernel-qemu-5.10.63-bullseye
wget -q -nc https://github.com/dhruvvyas90/qemu-rpi-kernel/raw/master/versatile-pb-bullseye-5.10.63.dtb

echo "##### Preparing image for tests..."
sector_size=$(fdisk -l ${raspbian_filename_img} | grep '^Sector' | cut -d' ' -f4)
boot_start=$(fdisk -l ${raspbian_filename_img} | grep W95 | tr -s ' ' | cut -d ' ' -f2)
boot_offset=$(expr $boot_start \* $sector_size)
rootfs_start=$(fdisk -l ${raspbian_filename_img} | grep Linux | tr -s ' ' | cut -d ' ' -f2)
rootfs_offset=$(expr $rootfs_start \* $sector_size)

# Tweaks for the boot partition
mkdir -p img-boot
sudo mount -o loop,offset=$boot_offset ${raspbian_filename_img} img-boot

sudo touch img-boot/ssh
sudo tee img-boot/userconf.txt > /dev/null << EOF
pi:$(openssl passwd "securepassword")
EOF

sleep 1
sudo umount img-boot
rmdir img-boot

# Tweaks for the rootfs
mkdir -p img-rootfs
sudo mount -o loop,offset=$rootfs_offset ${raspbian_filename_img} img-rootfs

# Raspberry Pi OS comes with this oneshot service to generate SSH keys that requires /dev/hwrng, which although
# existing it is unusable in QEMU. See the sources:
# https://github.com/RPi-Distro/raspberrypi-sys-mods/blob/bullseye/debian/raspberrypi-sys-mods.regenerate_ssh_host_keys.service
# https://github.com/RPi-Distro/raspberrypi-sys-mods/blob/bullseye/usr/lib/raspberrypi-sys-mods/regenerate_ssh_host_keys
sudo sed -i 's|dd|true #dd|' img-rootfs/usr/lib/raspberrypi-sys-mods/regenerate_ssh_host_keys
sudo mkdir img-rootfs/home/pi/.ssh
cat ${scriptdir}/../ssh-keys/key.pub | sudo tee img-rootfs/home/pi/.ssh/authorized_keys

sleep 1
sudo umount img-rootfs
rmdir img-rootfs

echo "##### Copying modified files..."
mv ${raspbian_filename_img} ${currdir}/${raspbian_mender_filename_img}
mv kernel-qemu-5.10.63-bullseye ${currdir}/
mv versatile-pb-bullseye-5.10.63.dtb ${currdir}/

cd ${currdir}
rm -rf ${workdir}

echo "##### Done"

exit 0
