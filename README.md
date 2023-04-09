# Sisyphus

[![Docker Build](https://github.com/ugur99/sisyphus/actions/workflows/docker-image.yml/badge.svg?branch=main)](https://github.com/ugur99/sisyphus/actions/workflows/docker-image.yml) [![Vulnerability Scanning](https://github.com/ugur99/sisyphus/actions/workflows/scan.yml/badge.svg?branch=main)](https://github.com/ugur99/sisyphus/actions/workflows/scan.yml)

Sisyphus is designed as a project to provide a simple solution for managing authentication/authorization of many kubernetes clusters. 

## Disclaimer

**X509 Client Certificates may not be the best practice for authenticating clusters, please refer to [Official Document](https://kubernetes.io/docs/reference/access-authn-authz/authentication/) for other practices.**

## How it Works?
You can simply give three variables: user names (can be given multiple names with using commas), group name (should be predefined) and target cluster name.

![kubeconfiggenerator](src/image/kubeconfiggenerator.png)

We can list the users and related cluster/rolegroup informations. 

![clusteruserlist](src/image/clusteruserlist.png)



