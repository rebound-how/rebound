![](./banner.png)

# Reliably Application server

Welcome to Reliably. This is the application server which serves the reliably
API used by Reliably services.

## Requirements

This application requires the following to run:

* A modern Linux distribution with systemd
* Python 3.12+
* Access to a PostgreSQL 14+ database
* Docker available to run the plans

## Getting Started

### Install the application

Run following command:

```bash
pip install \
    -U \
    --disable-pip-version-check \
    --prefer-binary \
    --no-cache-dir \
    reliably-app
```

The username and password should have been given to you by Reliably staff
as well. You may save them in your keyring but make sure they are
properly secured.

You may use the same command to update Reliably.

### View the version

Run the following command:

```bash
reliably-server version
```

This may be handy when interacting with Reliably staff.

### View this Readme

Run the following command:

```bash
reliably-server doc show-readme
```

### Initializating a configuration file

Run the following command:

```bash
reliably-server config init --interactive
```

This will populate a `.env` file in the current directory with good default
values. It will prompt you for some additional information.

Feel free to review and edit that file.

### Populating the database

The first task is to ensure your database is properly populated. Once done,
this should be seldom required, only reliably informs you the schema has been
changed.

Run the following command:

```bash
reliably-server db migrate
```

You can ask for the current moigration revision:

```bash
reliably-server db revision
```

If you created two different PostgreSQL users with different roles, you
need to create a new `.env` file (you can simply duplicate the application
one created in the previous section) and change the database credentials
accordingly.

Then run:

```bash
reliably-server db migrate --env-file .migrate.env
```

This will use this configuration to create the database schema.

## Run Reliably

You can run the `reliably-server` process manually or via systemd. We will
focus on first running it manually and explain the systemd supervision in a
following section.

In the directory containing your `.env` file, run the following command:

```bash
reliably-server run
```

By default, Reliably creates a pidfile to track the running process.
You can change the path of the pidfile or also disable the pidfile with
the appropriate command line argument.

## Stop Reliably

You can stop the server with the following command:

```bash
reliably-server stop
```

## Where to go next?

At this stage, Reliably is now running and can be used. Let's see what else
you may need to do.

## Appendices

### Database

#### Version

Reliably only works with a PostgreSQL database and expects a recent version
(at least version 14).

#### Access to a PostgreSQL 14+ database

For quick start, you may run a PostgreSQL locally in a container as follows:

```bash
docker run \
    --name postgres \
    -e POSTGRES_USER=test \
    -e POSTGRES_PASSWORD=secret \
    -e POSTGRES_DB=reliably \
    -p 5432:5432 \
    --rm \
    postgres
```

#### Users and their roles

The `reliably-server` process expects a non-admin user but with the following
privileges:

* `"CONNECT"`, `"TEMPORARY"` on the database
* `"ALL"` on the `public.table`

In addition, to run the migration script that populates and keep the schema
up to date, you need one user with the following privileges:

* `"CREATE"`, `"CONNECT"`, `"TEMPORARY"` on the database
* `"EXECUTE"` on the `function.table`
* `"EXECUTE"` on the `procedure.table`
* `"ALL"` on the `public.sequence`
* `"SELECT"`, `"INSERT"`, `"DELETE"`, `"UPDATE"`, `"TRUNCATE"`, `"TRIGGER"`, `"REFERENCES"` on the `public.table`

We suggest you create two distinct users but you don't have to.


### Supervision

#### Systemd

You may want to ensure it is supervised properly by the system in case it goes
down. If you run on a modern Linux system, you probably have systemd installed.
You can therefore install a systemd unit service that will ensure systemd
takes care of the process.

To do that, run the following command:

```bash
reliably-server system systemd create-unit-service
```

This will generate a `reliably.service` file that can be installed as a system
service following the instructions given by the command.
