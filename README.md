# turbo-chainsaw Description
Dockerized Django App with PostgreSQL Database

Use for fresh starts of tutorials and test projects

## Testing deployment

`docker-compose.dev.yml` uses only your local machine and creates a PostgreSQL DB in a local docker container. 
Note how `db.curiescience.com` is pointing to that local container.

Example:
```
sudo docker compose -f docker-compose.dev.yml up -d --build web
```

`docker-compose.prod.yml` uses a prebuild image from the GitHub Container Registry (ghcr.io) and the FQDN `db.curiescience.com` is resolved via the DNS of the docker host machine.  
In our case it is pointing to another local VM for stageing purposes (via Vagrant and `/etc/hosts`) or to a managed DB server in the cloud with an actual DNS server.

Example:
```
sudo docker compose -f docker-compose.prod.yml pull web
sudo docker compose -f docker-compose.prod.yml up -d
```

## gPAS
- admin interface available under `http:\\localhost:8081\gpas-web`
- for initial setup create new `Domäne` and adjust in `ehr.views`
- test app interfaces available under `http:\\localhost:8000\pseudonymize` and `http:\\localhost:8000\de-pseudonymize`