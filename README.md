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

## Keycloak auth
- `mozilla-django-oidc` library is an OpenID Connect adapter
- Keycloak (v23.0.6) server is running on an own container and mapped into the docker network (see `OIDC_HOST = http://host.docker.internal:8080`)
- fresh setup: create new client in keycloak, enter `client_id` and `client_secret` in `settings.py`
- manually add a user (important, email, first_name, last_name required as it is required in the Django `User` model) within the keycloak admin console `\admin`, credentials: `admin` `admin`
- use the registration flow to create a new user
- in `users.auth` the Authenitcation Backend is customized to synchronize the keycloak users with the app database
