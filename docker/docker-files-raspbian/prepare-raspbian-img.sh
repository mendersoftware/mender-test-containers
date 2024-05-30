#!/bin/sh

# Downloads Raspberry Pi OS image and prepares it for testing (create user, enable SSH and add trusted key)

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

raspios_filename_xz="${version}-raspios-bullseye-armhf-lite.img.xz"
raspios_filename_img="${raspios_filename_xz%.xz}"
raspios_mender_filename_img="${raspios_filename_img%.img}-mender-testing.img"

if [ -f ${currdir}/${raspios_mender_filename_img} ]; then
    echo "Found testing image in current directory. Exiting"
    exit 0
fi

# Get superuser privileges to be able to mount the SD image
sudo true

cd ${workdir}

raspios_url="https://downloads.raspberrypi.org/raspios_lite_armhf/images/raspios_lite_armhf-${version}/${version}-raspios-bullseye-armhf-lite.img.xz"

echo "##### Downloading and extracting..."
wget -q -nc ${raspios_url}
unxz ${raspios_filename_xz}

echo "##### Preparing image for tests..."
sector_size=$(fdisk -l ${raspios_filename_img} | grep '^Sector' | cut -d' ' -f4)
boot_start=$(fdisk -l ${raspios_filename_img} | grep W95 | tr -s ' ' | cut -d ' ' -f2)
boot_offset=$(expr $boot_start \* $sector_size)
rootfs_start=$(fdisk -l ${raspios_filename_img} | grep Linux | tr -s ' ' | cut -d ' ' -f2)
rootfs_offset=$(expr $rootfs_start \* $sector_size)

# Tweaks for the boot partition
mkdir -p img-boot
sudo mount -o loop,offset=$boot_offset ${raspios_filename_img} img-boot

sudo touch img-boot/ssh
sudo tee img-boot/userconf.txt > /dev/null << EOF
pi:$(openssl passwd "securepassword")
EOF

sleep 1
sudo umount img-boot
rmdir img-boot

# Tweaks for the rootfs
mkdir -p img-rootfs
sudo mount -o loop,offset=$rootfs_offset ${raspios_filename_img} img-rootfs

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

echo "##### Copying modified image..."
mv ${raspios_filename_img} ${currdir}/${raspios_mender_filename_img}

cd ${currdir}
rm -rf ${workdir}

echo "##### Done"

exit 0
