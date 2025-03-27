# Install Reliably Platform

!!! info

    The Reliably platform is lightweight in terms of requirements. It only
    requires access to a PostgreSQL 17+ database server. Beyond that, the required
    dependencies are related to your deployment target. For the rest of this page,
    __we will assume the most minimal setup__. You can check our dedicated [guides]
    for more installation options.

## Dependencies

!!! abstract inline end "MacOS and Windows"

    Reliably has not been thoroughly tested on Windows and MacOSX. Feel free
    to [open a discussion](https://github.com/orgs/rebound-how/discussions) if
    you run into challenges on these platforms. For the purpose of this
    page we will assume you are installing on a Linux host.

Reliably has few expectations when it comes to running:

* a Python 3.12+ environment
* a PostgreSQL 17+ database

### Python Environment

Reliably expects at least Python 3.12 to be installed. If you do not have that
version available on your machine, we suggest you follow the next steps.

First, install the [uv](https://docs.astral.sh/uv/) Python package manager.
Then install a Python 3.12 distribution as follows:

```console
uv python install 3.12
```

If your machine already comes with Python 3.12, we still recommend you use `uv`
and assume this is the case for the rest of the guide.

### PostgreSQL Database

On most Linux distribution, PostgreSQL can be installed via the distribution
package manager. We take a different route here by deploying a local instance
via Docker.

```console
docker pull postgres:17
```

## Install the Platform

You can install the Reliably Platform with:

```console
uv tool install --python python3.12 reliably-platform[full]
```

This will install the full stack and dependencies so you can also execute
plans from the same machine without any extra requirements.

## Check the Platform is installed

Let's see if the installation ran smoothly:

```bash
reliably-server --help
```

This should output the following:

```text
                                                                                                                            
 Usage: reliably-server [OPTIONS] COMMAND [ARGS]...                                                                         
                                                                                                                            
╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --install-completion          Install completion for the current shell.                                                  │
│ --show-completion             Show completion for the current shell, to copy it or customize the installation.           │
│ --help                        Show this message and exit.                                                                │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ run       Run the application and server until a signal is received (SIGINT, SIGTERM...)                                 │
│ stop                                                                                                                     │
│ version   Display the current version                                                                                    │
│ db        Database commands                                                                                              │
│ config    Configuration managment                                                                                        │
│ doc       Show basic documentation                                                                                       │
│ system    System information and commands                                                                                │
│ user      Users management                                                                                               │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

```

## Initialize the Platform Settings

Reliably uses a simple [.env](https://12factor.net/) file located in the default
configuration directory `$HOME/.config/rebound/reliably.env`.

Initialize the settings file with the next command:

```console
reliably-server config init --interactive
```

This should output a questionnaire like this:

```text
What's the domain serving the Reliably application? (localhost:8090): 
What's the URL to communicate back from plans? (https://localhost:8090): 
Should we manage the database (requires Docker)? [y/n]: y
Provide the name of a default Reliably organization to create (Hello): 
Do you want to create /tmp/rebound.env? [y/n]: y
```

## Run the Platform

You are now ready to start the platform using the newly created settings:

```console
reliably-server run
```

This should output such as:

```bash
[03/20/25 21:42:37] INFO     Using settings ~/.config/rebound/reliably.env.env
                    INFO     Starting the database server on localhost:5432
[03/20/25 21:42:39] INFO     Database container started  # (1)!
[03/20/25 21:42:40] INFO     Found a database we can connect to
                    INFO     Database schema revision c9a5def34d2a  # (2)!
[03/20/25 21:42:41] INFO     Started server process [93117]
                    INFO     Waiting for application startup.
                    INFO     Application startup complete.
                    INFO     Uvicorn running on http://0.0.0.0:8090 (Press CTRL+C to quit)  # (3)!
```

1. We configured the platform to manage the database, via Docker. You can see the server running with `docker inspect reliably-db`
2. The platform automatically upgrades the database to the most recent schema
3. You are now ready to go!

## Create an Account

Create an account by visiting the platform
[register](http://localhost:8090/login/?register=true) page.

<p align=center><img src="/assets/images/guides/register.png" alt="A screenshot of the page showing the registration form." /></p>

## What's next?

- [Go through the quick tour of the Platform main features](../tour.md)
