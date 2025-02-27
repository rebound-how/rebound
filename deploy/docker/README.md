# Docker compose deployment

## Requirements

This requires a recent version of Docker and Docker Compose available.

The application expects a few sensitivbe information to be set before you
can run it. Edit the `secrets.env` file and make sure this file remain
securely stored.

Other configurations are already set for you in the container image used
by the application and stored in `/home/svc/.config/rebound/reliably.env`. If
you need to change this configuration, you can set environment variables onto
the `app` service and they will override them by taking precedence. You may
also keep your own complete configurtation file and mount it into the container
by overwriting the existing file.

## Run

This compose recipe allows you to run the application fully on your local
environment with the help of `docker`.

To build and run the application, move to the top-level directory of the
repository and run:

```bash
docker compose up --build
```

This will build and run the `app` and `database` services.
The application will listen on port `8090`.

You can then access the application at http://localhost:8090/

Once you have run this the first time, you could even simply run without
re-building the images:

```bash
docker compose up
```

## Shutdown and Cleanup

To cleanup resources:

```bash
docker compose down
```

To remove also the database data:

```bash
docker compose down -v
```
