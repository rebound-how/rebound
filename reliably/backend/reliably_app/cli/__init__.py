import asyncio
import base64
import hashlib
import importlib.resources
import logging
import os
import secrets
import shutil
import socket
import string
from contextlib import contextmanager
from importlib.metadata import metadata
from ipaddress import IPv4Address
from pathlib import Path
from typing import Generator, Tuple
from urllib.parse import urlparse

import alembic.command
import docker
import docker.errors
import orjson
from docker.models.containers import Container
from platformdirs import user_config_path
from sqlalchemy.engine import make_url
import typer
import uvicorn
from alembic.config import Config as AlembicConfig
from pydantic import SecretStr
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm, Prompt

from reliably_app import account, hasher, crypto
from reliably_app.__version__ import __version__
from reliably_app.cli.pidfile import pidfile, terminate_running_server
from reliably_app.config import get_settings, Settings
from reliably_app.database import (
    AsyncSession,
    create_db_engine,
    check_db_ready,
    get_current_revision,
)
from reliably_app.log import configure_logging, setup_logger_config, console
from reliably_app.main import init_app


logger = logging.getLogger("reliably_app")

cli = typer.Typer(no_args_is_help=True)
db = typer.Typer(no_args_is_help=True)
config = typer.Typer(no_args_is_help=True)
doc = typer.Typer(no_args_is_help=True)
system = typer.Typer(no_args_is_help=True)
systemd = typer.Typer(no_args_is_help=True)
user = typer.Typer(no_args_is_help=True)

config_path = user_config_path("rebound")
config_path.mkdir(exist_ok=True, parents=True)
config_file = config_path / Path("reliably.env")


@cli.command()
def run(
    env_file: Path = typer.Option(
        config_file, help="Path to the application .env file"
    ),
    host: str = typer.Option(
        os.getenv("RELIABLY_APP_HOST", "0.0.0.0"),
        help="IP to bind to",  # nosec
    ),
    port: int = typer.Option(
        int(os.getenv("RELIABLY_APP_PORT", 8090)), help="Port to bind to"
    ),
    pid_file_path: Path = typer.Option(
        Path(f"/run/user/{os.getuid()}/reliably.pid"),
        help="Pidfile to track the process",
    ),
    pid_file: bool = typer.Option(
        True,
        is_flag=True,
        help="Enable/disable the pidfile",
    ),
    tls_key: Path | None = typer.Option(
        None,
        help="TLS key file",
    ),
    tls_cert: Path | None = typer.Option(
        None,
        help="TLS certificate file",
    ),
) -> None:
    """
    Run the application and server until a signal is received
    (SIGINT, SIGTERM...)
    """
    try:
        with ensure_env_file(env_file, host, port) as env_file:
            env_file = env_file.absolute()

            settings = get_settings(env_file)
            configure_logging(settings)

            logger.info(f"Using settings {env_file}")

            with db_server(settings, env_file) as (db_is_present, _):
                if not db_is_present:
                    logger.fatal(
                        "Failed to access a database server. "
                        "Please ensure you have one started or configured "
                        "correctly in the settings"
                    )
                    raise typer.Exit(1)

                logger.info("Found a database we can connect to")

                rev = db_schema_revision(settings)
                if rev is None:
                    logger.warning(
                        "Database schema was not populated it seems. "
                        "Updating now..."
                    )
                    db_migrate_schema(env_file)
                    rev = db_schema_revision(settings)

                logger.info(f"Database schema revision {rev}")

                with pidfile(pid_file_path, pid_file):
                    app = init_app(settings)

                    uvicorn.run(
                        app,
                        host=str(IPv4Address(host)),
                        port=port,
                        ws="none",
                        proxy_headers=True,
                        date_header=False,
                        server_header=False,
                        access_log=True,
                        log_config=None,
                        forwarded_allow_ips="*",
                        ssl_keyfile=tls_key,
                        ssl_certfile=tls_cert,
                    )
    except IOError as x:
        console.print(str(x))


@cli.command()
def stop(
    pid_file_path: Path = typer.Option(
        Path(f"/run/user/{os.getuid()}/reliably.pid"),
        help="Pidfile tracking the process",
    ),
) -> None:
    console.print("Terminating process...")
    terminate_running_server(pid_file_path)


@cli.command(help="Display the current version")
def version() -> None:
    console.print(__version__)


@db.command()
def migrate(
    env_file: Path = typer.Option(
        config_file, help="Path to the application .env file"
    ),
    revision: str = "head",
    verbose: bool = typer.Option(False, is_flag=True),
) -> None:
    """
    Perform a database migration from its current revision
    """
    if verbose:
        logging.config.dictConfig(setup_logger_config(app_log_to_stdout=True))

    from reliably_app import migrations

    with ensure_env_file(env_file) as env_file:
        env_file = env_file.absolute()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            progress.add_task(description="Processing...", total=None)

            c = AlembicConfig()
            d = Path(migrations.__file__).parent.resolve().absolute()

            c.set_main_option("script_location", str(d))
            c.set_main_option("prepend_sys_path", str(d.parent.absolute()))
            c.set_main_option("env_file", str(env_file.resolve().absolute()))

            alembic.command.upgrade(c, revision)


@db.command()
def revision(
    env_file: Path = typer.Option(
        config_file, help="Path to the application .env file"
    ),
) -> None:
    """
    Print the current database migration revision
    """
    import alembic.command
    from alembic.config import Config as AlembicConfig

    from reliably_app import migrations

    with ensure_env_file(env_file) as env_file:
        env_file = env_file.absolute()

        c = AlembicConfig()
        d = Path(migrations.__file__).parent.resolve().absolute()
        c.set_main_option("script_location", str(d))
        c.set_main_option("prepend_sys_path", str(d.parent.absolute()))
        c.set_main_option("env_file", str(env_file.resolve().absolute()))

        alembic.command.current(c)


@db.command()
def generate(
    message: str = typer.Option("--message", "-m"),
    env_file: Path = typer.Option(
        config_file, help="Path to the application .env file"
    ),
    verbose: bool = typer.Option(False, is_flag=True),
) -> None:
    """
    Generate a new revision
    """
    if verbose:
        logging.config.dictConfig(setup_logger_config(app_log_to_stdout=True))

    import alembic.command
    from alembic.config import Config as AlembicConfig

    from reliably_app import migrations

    with ensure_env_file(env_file) as env_file:
        env_file = env_file.absolute()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            progress.add_task(description="Generating...", total=None)

            c = AlembicConfig()
            d = Path(migrations.__file__).parent.resolve().absolute()
            c.set_main_option("script_location", str(d))
            c.set_main_option("prepend_sys_path", str(d.parent.absolute()))
            c.set_main_option("env_file", str(env_file.resolve().absolute()))

            alembic.command.revision(c, message=message, autogenerate=True)


cli.add_typer(db, name="db", help="Database commands")


@config.command()
def show(
    clear_secrets: bool = typer.Option(
        False, is_flag=True, help="Show secret values in clear text"
    ),
) -> None:
    """
    Show current settings
    """
    settings = get_settings(config_file)
    for k, v in settings.model_dump().items():
        if isinstance(v, SecretStr):
            if clear_secrets:
                v = v.get_secret_value()
        elif isinstance(v, Path):
            v = str(v)
        else:
            v = orjson.dumps(v).decode("utf-8")
        console.print("{0}={1}".format(k, v))


@config.command()
def init(
    env_file: Path = typer.Option(
        config_file, help="Path to the configuration file to write"
    ),
    interactive: bool = typer.Option(
        False, help="Let the command fill some of the configuration's value"
    ),
) -> None:
    """
    Create a new .env with default settings
    """
    if env_file.exists():
        raise typer.BadParameter(
            f"File {env_file} already exists and will not be overriden"
        )

    with importlib.resources.path("reliably_app.cli", "default.local.env") as p:
        if not p.absolute().is_file():
            console.print("Failed to locate profile template")
            raise typer.Exit(1)

        template = p.absolute().read_text()

        template = template.replace("<session_secret_key>", secrets.token_hex())
        template = template.replace(
            "<db_secret_key>",
            base64.b64encode(secrets.token_bytes(32)).decode("utf-8"),
        )

        if interactive:
            domain = Prompt.ask(
                "What's the domain serving the Reliably application?",
                console=console,
                default="localhost:8090",
                show_default=True,
            )
            template = template.replace("<domain>", domain)

            choice_service_host = f"http://{domain}"
            service_host = Prompt.ask(
                "What's the URL to communicate back from plans?",
                console=console,
                default=choice_service_host,
                show_default=True,
            )
            if service_host == choice_service_host:
                template = template.replace("<cli_service_host>", "")
                template = template.replace("<cli_host>", "")
            else:
                template = template.replace(
                    "# CLI_RELIABLY_SERVICE_HOST=<cli_service_host>",
                    f"CLI_RELIABLY_SERVICE_HOST={service_host}",
                )
                parsed = urlparse(service_host)
                template = template.replace(
                    "# CLI_RELIABLY_HOST=<cli_host>",
                    f"CLI_RELIABLY_HOST={parsed.netloc}",
                )

            manageddb = Confirm.ask(
                "Should we manage the database (requires Docker)?",
                console=console,
            )

            if manageddb:
                template = template.replace("#DATABASE_MODE", "DATABASE_MODE")
                template = template.replace("<dbuser>", "demo")
                template = template.replace("<dbpassword>", "demo")
                template = template.replace("<dbaddress>", "localhost")
                template = template.replace("<dbport>", "5432")
                template = template.replace("<dbname>", "reliably")
            else:
                dbuser = Prompt.ask(
                    "What's the database username?",
                    console=console,
                    default="demo",
                    show_default=True,
                )
                template = template.replace("<dbuser>", dbuser)

                dbpassword = Prompt.ask(
                    "What's the database user's password?",
                    console=console,
                    default="demo",
                    show_default=True,
                )
                template = template.replace("<dbpassword>", dbpassword)

                dbaddress = Prompt.ask(
                    "What's the database hostname or address?",
                    console=console,
                    default="localhost",
                    show_default=True,
                )
                template = template.replace("<dbaddress>", dbaddress)

                dbport = Prompt.ask(
                    "What's the database port?",
                    console=console,
                    default="5432",
                    show_default=True,
                )
                template = template.replace("<dbport>", dbport)

                dbname = Prompt.ask(
                    "What's the database name?",
                    console=console,
                    default="reliably",
                    show_default=True,
                )
                template = template.replace("<dbname>", dbname)

            defaultorg = Prompt.ask(
                "Provide the name of a default Reliably organization to create",
                console=console,
                default="Hello",
                show_default=True,
            )
            template = template.replace("<defaultorg>", defaultorg)

            if not Confirm.ask(f"Do you want to create {env_file}?"):
                raise typer.Exit(0)

        env_file.write_text(template)


cli.add_typer(config, name="config", help="Configuration managment")


@doc.command()
def show_readme() -> None:
    """
    Show application's basic readme
    """
    p = metadata("reliably-app")
    d = Markdown(p["description"], code_theme="github-dark")

    with console.pager():
        console.print(d)


cli.add_typer(doc, name="doc", help="Show basic documentation")


@systemd.command()
def create_unit_service(
    working_directory: Path = typer.Option(
        help="Directory where to launch Reliably from"
    ),
    env_file: Path = typer.Option(
        Path(".env"), help="Env file path, relative to the working directory"
    ),
    host: str = typer.Option("0.0.0.0", help="IP to bind to"),  # nosec
    port: int = typer.Option(8090, help="Port to bind to"),
    user_id: int = typer.Option(
        os.getuid(), help="The user ID to run the process as"
    ),
    group_id: int = typer.Option(
        os.getgid(), help="The group ID to run the process into"
    ),
) -> None:
    """
    Install systemd files
    """
    bin_path = shutil.which("reliably-server")
    if not bin_path:
        raise RuntimeError("failed to locate 'reliably-server' in your PATH")

    with importlib.resources.path("reliably_app.cli", "reliably.service") as p:
        unit = p.read_text()

        unit = unit.replace(
            "<reliably-working-directory>", str(working_directory.absolute())
        )
        unit = unit.replace("<reliably-env-file>", str(env_file))
        unit = unit.replace("<reliably-absolute-path>", bin_path)
        unit = unit.replace("<reliably-user>", str(user_id))
        unit = unit.replace("<reliably-group>", str(group_id))
        unit = unit.replace("<host>", host)
        unit = unit.replace("<port>", str(port))

        Path("reliably.service").write_text(unit)

        console.print(
            """
1. Create a link to the reliably.service file in /etc/systemd/system
           
    sudo cp reliably.service /etc/systemd/system/reliably.service

2. Enable this service:

    sudo systemctl enable reliably.service

3. Reload all unit:

    sudo systemctl daemon-reload

4. Start the service:

     sudo systemctl start reliably.service

4. Check its status:

    systemctl status reliably.service

5. Tail its logs:

    journalctl -fexu reliably.service

The service is configured to restart on failures and run after you log out.

You can stop the service as follows:

     sudo systemctl stop reliably.service

And disable the service like this:

    sudo systemctl disable reliably.service
        """  # noqa E501
        )


system.add_typer(systemd, name="systemd", help="Systemd management")
cli.add_typer(system, name="system", help="System information and commands")


@user.command()
def reset_password(
    email: str,
    password: str = typer.Option(
        None, help="Password to use. If not set, autogenerate a password"
    ),
    env_file: Path = typer.Option(
        Path(".env"), help="Path to the configuration file"
    ),
) -> None:
    if not password:
        alphabet = string.ascii_letters + string.digits + "-+_!@#$%^&*.,?"
        password = "".join(secrets.choice(alphabet) for i in range(12))

    async def update() -> None:
        settings = get_settings(env_file.absolute())
        engine = create_db_engine(settings)

        async with AsyncSession(bind=engine) as db:
            if await account.crud.get_user_by_email(db, email) is None:
                console.print("Unknown user")
                raise typer.Exit(1)

            await account.crud.reset_password(db, email, hasher.hash(password))

    asyncio.run(update())

    console.print(f"New password: {password}")


cli.add_typer(user, name="user", help="Users management")


###############################################################################
# Private functions
###############################################################################
@contextmanager
def db_server(
    settings: Settings, env_file: Path
) -> Generator[Tuple[bool, Container | None], None, None]:
    db_url = str(settings.DATABASE_URL)

    if settings.DATABASE_MODE == "extern":
        if check_db_ready(db_url) is False:
            logger.error("Failed to connect to database")
            yield (False, None)
            return None

        yield (True, None)
        return None

    client = docker.from_env()

    url = make_url(db_url)
    container_name = "reliably-db"

    container: Container | None = None

    try:
        container = client.containers.get(container_name)
        if container.status == "exited":
            container.start()

            if check_db_ready(db_url) is False:
                logger.error("Failed to start database container")
                yield (False, None)
                return None

        logger.info(
            f"Using database container [yellow]{container_name}",
            extra={"markup": True},
        )
        yield (True, container)
    except docker.errors.NotFound:
        logger.info(
            "Starting the database server on "
            f"[cyan]{url.host}:{url.port}[/cyan]",
            extra={"markup": True},
        )

        second = 1000000000

        container = client.containers.run(
            image="postgres:17",
            auto_remove=True,
            environment=dict(
                POSTGRES_PASSWORD=url.password,
                POSTGRES_USER=url.username,
                POSTGRES_DB=url.database,
            ),
            name=container_name,
            ports={"5432/tcp": ("127.0.0.1", url.port)},
            detach=True,
            remove=False,
            healthcheck={
                "test": ["CMD-SHELL", "pg_isready", "-d", url.database],
                "interval": 3 * second,
                "timeout": 6 * second,
                "retries": 5,
                "start_period": 6 * second,
            },
        )

        if check_db_ready(db_url) is False:
            logger.error("Failed to start database container")
            yield (False, None)
            return None

        logger.info("Database container started")

        migrate(env_file=env_file, verbose=False)

        yield (True, container)
    except Exception:
        if container:
            logger.info("Stopping database container")
            container.stop()


@contextmanager
def ensure_env_file(
    env_file: Path, host: str = "localhost", port: int = 8090
) -> Generator[Path, None, None]:
    if env_file.exists():
        yield env_file
        return None

    if config_file.exists():
        yield config_file
        return None

    with importlib.resources.path("reliably_app.cli", "default.local.env") as p:
        env = p.read_text()

    # listening address
    hostname = socket.gethostname()
    env = env.replace("<domain>", f"http://{hostname}:{port}")

    # db configuration
    env = env.replace("<dbuser>", "demo")
    env = env.replace("<dbpassword>", "demo")
    env = env.replace("<dbaddress>", "localhost")
    env = env.replace("<dbport>", "5433")
    env = env.replace("<dbname>", "reliably")

    # cryptography settings
    env = env.replace("<db_secret_key>", crypto.generate_key())

    # http session settings
    env = env.replace("<session_secret_key>", hashlib.sha256().hexdigest())

    # reliably org settings
    env = env.replace("<defaultorg>", "Hello")

    config_file.write_text(env)

    logger.info(f"Created new settings and saved them in {config_file}")

    yield config_file


def db_migrate_schema(env_file: Path, revision: str = "head") -> None:
    from reliably_app import migrations

    c = AlembicConfig()
    d = Path(migrations.__file__).parent.resolve().absolute()
    c.set_main_option("script_location", str(d))
    c.set_main_option("prepend_sys_path", str(d.parent.absolute()))
    c.set_main_option("env_file", str(env_file))

    alembic.command.upgrade(c, revision)


def db_schema_revision(settings: Settings) -> str | None:
    db_url = str(settings.DATABASE_URL)
    return get_current_revision(db_url)


if __name__ == "__main__":
    cli()
