Mender Test Containers
==============================================

This repository contains docker image definitions needed to continuously build and test products for the Mender company.

The following images are defined in this repository and published to the GitLab
container registry as separate image repositories under `$CI_REGISTRY_IMAGE`:

| image name | folder | description |
|---|---|---|
| base-alpine | base-alpine | Base Alpine image with common build tools and AWS CLI |
| base-debian | base-debian | Base Debian image with common build tools and AWS CLI |
| base-ubuntu | base-ubuntu | Base Ubuntu image with common build tools and AWS CLI |
| base-mender-cpp | base-mender-cpp | Debian-based C/C++ development environment for Mender projects |
| aws-k8s-toolbox | aws-k8s-toolbox | Kubernetes and AWS toolbox with kubectl, Helm, kubeconform, eksctl, and yq |
| docker-multiplatform-buildx | docker-multiplatform-buildx | Docker image with git and regctl for multi-platform image management |
| goveralls | goveralls | Go image with goveralls for code coverage reporting |
| gui-e2e-testing | gui-e2e-testing | Playwright-based GUI end-to-end testing with mender-artifact and Docker CLI |
| mender-client-acceptance-testing | mender-client-acceptance-testing | Ubuntu image with Yocto/build tools, Docker, and Python for client acceptance testing |
| mender-dist-packages-builder | mender-dist-packages-building | Multi-architecture cross-compilation image for Mender package building |
| mongodb-backup-runner | mongodb-backup-runner | Debian image with AWS CLI and Azure CLI for MongoDB backup operations |
| python-black | python-black | Alpine Python image for code formatting and linting |
| release-please | release-please | Node.js image with release-please, GitHub CLI, and git-cliff for release management |
| terragrunt-trivy-toolbox | terragrunt-trivy-toolbox | Terraform, Terragrunt, and Trivy for infrastructure deployment and security scanning |

### Usage in GitLab CI

Each image is available as a separate registry repository. Reference them using the
image name as a path component and the branch as the tag:

```
$CI_REGISTRY/Northern.tech/Mender/mender-test-containers/<image-name>:<branch>
```

For example, in a `.gitlab-ci.yml`:

```yaml
build:
  image: $CI_REGISTRY/Northern.tech/Mender/mender-test-containers/aws-k8s-toolbox:master
```

For `mender-dist-packages-builder`, the build matrix variant is encoded in the tag:

```yaml
build:
  image: $CI_REGISTRY/Northern.tech/Mender/mender-test-containers/mender-dist-packages-builder:crosscompile-debian-trixie-amd64-master
```
