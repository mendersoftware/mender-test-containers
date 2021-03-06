Mender Test Containers
==============================================

This repository contains docker image definitions needed to continously build and test products for the Mender company.

The images in here are used in the following situations:

| docker tag | folder | usage example |
|---|---|---|
| raspbian_latest | docker | [this repo](https://github.com/mendersoftware/mender-test-containers/blob/master/container_props.py) for use in [mender-binary-delta](https://github.com/mendersoftware/mender-binary-delta/blob/master/.gitmodules) |
| acceptance-testing | backend-acceptance-testing | [deviceauth](https://github.com/mendersoftware/deviceauth/blob/master/tests/docker-compose-acceptance.yml) |
| mender-client-acceptance-testing | mender-client-acceptance-testing | [Mender QA](https://github.com/mendersoftware/mender-qa/blob/master/.gitlab-ci.yml) |