#!/usr/bin/python3
# Copyright 2019 Northern.tech AS
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        https://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import logging
import os.path
import pytest
import subprocess
import urllib

from .helpers import *


class TestContainerDidNotboot(Exception):
    pass


def do_setup_test_container(request, setup_test_container_props, mender_version):
    # This should be parametrized in the mother project.
    image = setup_test_container_props.image_name

    if setup_test_container_props.append_mender_version:
        image = "%s:%s" % (image, mender_version)

    cmd = "docker run --rm --network host --privileged -tid %s" % image
    logging.debug("setup_test_container: %s", cmd)
    output = subprocess.check_output(cmd, shell=True)

    global docker_container_id
    docker_container_id = output.decode("utf-8").split("\n")[0]
    setup_test_container_props.container_id = docker_container_id

    def finalizer():
        cmd = "docker stop {}".format(docker_container_id)
        logging.debug("setup_test_container: %s", cmd)
        subprocess.check_output(cmd, shell=True)

    request.addfinalizer(finalizer)

    ready = wait_for_container_boot(docker_container_id)
    if not ready:
        raise TestContainerDidNotboot

    return setup_test_container_props


@pytest.fixture(scope="class")
def setup_test_container(request, setup_test_container_props, mender_version):
    return do_setup_test_container(request, setup_test_container_props, mender_version)


@pytest.fixture(scope="function")
def setup_test_container_f(request, setup_test_container_props, mender_version):
    return do_setup_test_container(request, setup_test_container_props, mender_version)


@pytest.fixture(scope="class")
def setup_tester_ssh_connection(setup_test_container):
    yield new_tester_ssh_connection(setup_test_container)


@pytest.fixture(scope="function")
def setup_tester_ssh_connection_f(setup_test_container_f):
    yield new_tester_ssh_connection(setup_test_container_f)


# Requires the user to implement mender_deb_version fixture
@pytest.fixture(scope="class")
def setup_mender_configured(
    setup_test_container, setup_tester_ssh_connection, mender_deb_version
):
    if (
        setup_tester_ssh_connection.run(
            "test -x /usr/bin/mender-update", warn=True
        ).exited
        == 0
        or setup_tester_ssh_connection.run("test -x /usr/bin/mender", warn=True).exited
        == 0
    ):
        # If mender is already present, do nothing.
        return

    if version_is_minimum(mender_deb_version, "4.0.0"):
        pkgs_to_install = ["mender-auth", "mender-update"]
        url = "https://downloads.mender.io/repos/debian/pool/main/m/mender-client4/"
    else:
        pkgs_to_install = ["mender-client"]
        url = "https://downloads.mender.io/repos/debian/pool/main/m/mender-client/"

    for pkg in pkgs_to_install:
        pkg_url = url + f"{pkg}_{mender_deb_version}-1%2Bdebian%2Bbullseye_armhf.deb"
        filename = urllib.parse.unquote(os.path.basename(pkg_url))
        # Install deb package and missing dependencies
        setup_tester_ssh_connection.run(f"wget {pkg_url}")
        result = setup_tester_ssh_connection.sudo(
            f"DEBIAN_FRONTEND=noninteractive dpkg --install {filename}", warn=True
        )
        if result.exited != 0:
            setup_tester_ssh_connection.sudo("apt-get update")
            setup_tester_ssh_connection.sudo(
                "apt-get --fix-broken --assume-yes install"
            )

    # Verify that the packages were installed
    for pkg in pkgs_to_install:
        setup_tester_ssh_connection.run(f"dpkg --status {pkg}")

    output = setup_tester_ssh_connection.run("uname -m").stdout.strip()
    if output == "x86_64":
        device_type = "generic-x86_64"
    elif output.startswith("arm"):
        device_type = "generic-armv6"
    else:
        raise KeyError(f"{output} is not a recognized machine type")

    setup_tester_ssh_connection.sudo("mkdir -p /var/lib/mender")
    setup_tester_ssh_connection.run(
        f"echo device_type={device_type} | sudo tee /var/lib/mender/device_type"
    )
