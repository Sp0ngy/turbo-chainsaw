## Continuous Deployment a la Patrick Dreker (CodeCamp:N)

Multi stage docker build:
- seperate package build in own docker
- then copy the built artefact to the new docker image

### Compose Updater
`workloads/compose-updater` watches for newly build docker images in the respective repository.
[compose-updater](https://github.com/virtualzone/compose-updater)

- own docker container which pulls regularly registry
- can handle only static tags, no semver tags
- advance stage webhook can be used to trigger process (ArgoCD or FluxCD)

### Labeling
The labeling is done in the Github via a tag, e.g. `turbo-chainsaw:develop` or `turbo-chainsaw:prod`.
The pipeline checks for this label and pulls a newly available image.

### Haproxy
- haproxy was installed