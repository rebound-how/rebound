---
layout: ~/layouts/DocsLayout.astro
title: Install & Run the Reliably Platform
description: Install the Reliably Platform and run it on your local machine
---

The Reliably Platform is the heart of your resilience strategy. It helps you
create, schedule and orchestrate your reliability experiments and policies.

## Install

The Reliably Platform is installed as a regular Python package. It requires
Python 3.12 at the minimum (it might work with lower down to 3.10 but this is
isn't supported officially).

### Using `pip`

Install it as follows:

```bash
python3 -m pip install --user reliably-app[full]
```

This will install the `reliably-server` binary in your `$HOME/.local/bin`
directory.

To ensure that everything is working, you can use `reliably-server version` in a
new window:

```bash
reliably-server version
```

### Using `uv`

Install it as follows:

```bash
uv tool install --python-preference only-managed --python "3.12" reliably-app[full]
```

This will install the `reliably-server` binary in your `$HOME/.local/bin`
directory.

To ensure that everything is working, you can use `reliably-server version` in a
new window:

```bash
reliably-server version
```

## Dependencies

The Reliably Platform has few dependencies beside the Python packages installed
by the command above.

### Required

The only required dependency is a PostgreSQL 15+ database. If you do not have
access to one, you may simply run a container such as:

```bash
docker run -d --name reliably-server-db \
    -p 5432:5432 \
    -e POSTGRES_PASSWORD=demo \
    -e POSTGRES_USER=demo \
    -e POSTGRES_DB=demo \
    postgres:17
```

You may want to adjust the parameters to suit your needs.

### Optional

#### uv

Reliably Plans can be deployed and managed locally. To use this target,
make sure [uv](https://docs.astral.sh/uv/) is available on the machine.

#### Docker

Reliably Plans can be deployed inside Docker container. To use this target,
make sure Docker is available on the machine.

#### Kubernetes

Reliably Plans can be deployed as Kubernetes jobs. To use this target,
make sure Kubernetes and that you have enough RBAC permissions.

## Configure

The Reliably Platform requires some information before it can start. The
platform looks for settings in a file found in
`$HOME/.config/rebound/reliably.env`.

You can initialize the file by running the following command:

```bash
reliably-server config init --interactive
What's the domain serving the Reliably application? (localhost:8090): 
What's the URL to communicate back from plans? (http://localhost:8090): 
Should we manage the database (requires Docker)? [y/n]: n
What's the database username? (demo): 
What's the database user's password? (demo): 
What's the database hostname or address? (localhost): 
What's the database port? (5432): 
What's the database name? (reliably): 
Provide the name of a default Reliably organization to create (Hello): 
Do you want to create ~/.config/rebound/reliably.env? [y/n]: y
```

This will be enough for you to start the server. However, you may want to
explore the file to see other options.

### Data

Reliably stores its data into a PostgreSQL database. Upon starting the
platform for the first time, the schema will be created and populated with
all the required tables.

You may use the `reliably db` commands to manage the database. For instance,
to see which revision of the schema you are currently runnning:

```bash
reliably-server db revision
```

Reliably always keeps the schema up to date when it starts and applies the
migration that is required if it has changed.

## Run

The Reliably Platform is a single Python application that is run as follows:

```bash
reliably-server run
```

## What's next?

- [Follow or Quick Tour](/docs/guides/tour/) guide to
  explore the Platform capabilities.
