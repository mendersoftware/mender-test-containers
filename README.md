Mender Test Containers
==============================================

This repository contains docker image definitions needed to continuously build and test products for the Mender company.

The images in here are used in the following situations:

| docker tag | folder | usage example |
|---|---|---|
| raspbian_latest | docker | [this repo](https://github.com/mendersoftware/mender-test-containers/blob/master/container_props.py) for use in [mender-binary-delta](https://github.com/mendersoftware/mender-binary-delta/blob/master/.gitmodules) |
| acceptance-testing | backend-acceptance-testing | [deviceauth](https://github.com/mendersoftware/deviceauth/blob/master/tests/docker-compose-acceptance.yml) |
| gui-e2e-testing | gui-e2e-testing | [gui](https://github.com/mendersoftware/gui/blob/master/tests/e2e_tests/docker-compose.e2e-tests.yml) |
| backend-integration-testing | backend-integration-testing | [integration](https://github.com/mendersoftware/integration/blob/master/backend-tests/docker/docker-compose.backend-tests.yml) for use in [Mender QA](https://github.com/mendersoftware/mender-qa/blob/master/gitlab-pipeline/stage/test.yml) |
| mender-client-acceptance-testing | mender-client-acceptance-testing | [Mender QA](https://github.com/mendersoftware/mender-qa/blob/master/.gitlab-ci.yml) |
| aws-k8s-v1 | aws-k8s-toolbox | [Mender Helm](https://github.com/mendersoftware/mender-helm/blob/master/.gitlab-ci.yml) |
| mender-dist-packages-builder-{DISTRO}-{RELEASE}-{ARCH} | mender-dist-packages-building    | [mender-dist-packages](https://github.com/mendersoftware/mender-dist-packages/blob/master/.gitlab-ci.yml) |
| goveralls | goveralls | [workflows](https://github.com/mendersoftware/workflows/blob/master/.gitlab-ci.yml) |
