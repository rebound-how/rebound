import contextlib
import logging
import logging.handlers
import os
import tempfile
import traceback
from datetime import datetime, timezone
from pathlib import Path
from types import FrameType
from typing import Any, Generator
from uuid import UUID

import httpx
import orjson
import typer
from chaoslib import convert_vars, exit as chaos_exit, merge_vars
from chaoslib.control import load_global_controls
from chaoslib.experiment import ensure_experiment_is_valid, run_experiment
from chaoslib.log import configure_logger
from chaoslib.settings import CHAOSTOOLKIT_CONFIG_PATH, load_settings
from chaoslib.types import Dry, Journal, Schedule, Strategy
from ruamel.yaml import YAML

from ..client import api_client, should_verify_tls_cert
from ..config import ensure_config_is_set, get_settings
from ..format import format_as
from ..log import console
from ..types import (
    Environment,
    EnvironmentSecret,
    EnvironmentSecretAsFile,
    FormatOption,
    Plan,
)

cli = typer.Typer(help="Manage and execute Reliably plans from your terminal")


@cli.command()
def get(
    plan_id: UUID,
    format: FormatOption = typer.Option("json", show_choices=True),
) -> None:
    """
    Get a plan and display it
    """
    ensure_config_is_set()
    p = load_plan(plan_id)
    console.print(format_as(p, format))


@cli.command(name="store-context")
def store_context(plan_id: UUID) -> None:
    """
    Store a plan context so the execution has what it needs to operate
    """
    ensure_config_is_set()
    p = load_plan(plan_id)
    store_plan_context(p)


def validate_vars(ctx: typer.Context, value: list[str]) -> dict[str, Any]:
    try:
        return convert_vars(value)
    except ValueError as x:
        raise typer.BadParameter(str(x))


@cli.command()
def execute(
    plan_id: UUID,
    result_file: Path = typer.Option("./result.json", writable=True),
    log_stdout: bool = typer.Option(False, is_flag=True),
    log_file: Path = typer.Option("./run.log", writable=True),
    set_status: bool = typer.Option(False, is_flag=True),
    skip_context: bool = typer.Option(False, is_flag=True),
    load_environment: bool = typer.Option(False, is_flag=True),
    control_file: list[Path] = typer.Option(
        lambda: [], dir_okay=False, readable=True
    ),
    var_file: list[Path] = typer.Option(
        lambda: [], dir_okay=False, readable=True
    ),
    set_exit_code: bool = typer.Option(
        True,
        is_flag=True,
        help=(
            "Exit code reflects the plan status: 0 is completed, 1 is "
            "deviated and 2 is any other status"
        ),
    ),
) -> None:
    """
    Execute a plan
    """
    ensure_config_is_set()

    p = load_plan(plan_id)
    tempdir = tempfile.TemporaryDirectory()

    context = {}
    if not skip_context:
        context = store_plan_context(p, tempdir.name)

    settings = get_settings()

    if settings.service.host.startswith("http://"):
        os.environ["RELIABLY_USE_HTTP"] = "true"
    else:
        os.environ["RELIABLY_USE_HTTP"] = "false"

    if os.getenv("RELIABLY_HOST") is None:
        os.environ["RELIABLY_HOST"] = settings.service.host.replace(
            "https://", ""
        ).replace("http://", "")

    token = settings.service.token.get_secret_value()
    if os.getenv("RELIABLY_TOKEN") is None:
        os.environ["RELIABLY_TOKEN"] = token

    if os.getenv("RELIABLY_PLAN_ID") is None:
        os.environ["RELIABLY_PLAN_ID"] = str(p.id)

    experiment_id = p.definition.experiments[0]
    base_url = f"{settings.service.host}/api/v1/organization"
    base_url = f"{base_url}/{settings.organization.id}"
    experiment_url = f"{base_url}/experiments/{experiment_id}/raw"

    if load_environment:
        load_environment_into_memory(p, tempdir.name)

    with console.status("Executing..."):
        if set_status:
            send_status(p.id, "running")

        with reconfigure_chaostoolkit_logger(log_file, log_stdout):
            try:
                journal = run_chaostoolkit(
                    experiment_url, context, var_file, control_file
                )
            except Exception as x:
                if set_status:
                    send_status(p.id, "error", f"Error: {x}")

                tb = "".join(traceback.format_exception(x))
                console.print(f"running experiment failed: {tb}")

                raise typer.Exit(code=2)

            result_file.absolute().write_bytes(
                orjson.dumps(journal, option=orjson.OPT_INDENT_2)
            )
            show_result_url(journal)

            if set_exit_code:
                if journal.get("deviated"):
                    raise typer.Exit(code=1)
                elif journal.get("status") != "completed":
                    raise typer.Exit(code=2)


###############################################################################
# Private functions
###############################################################################
def load_plan(plan_id: UUID) -> Plan:
    with console.status("Fetching plan..."):
        with api_client() as client:
            r = client.get(f"/plans/{str(plan_id)}")
            if r.status_code == 404:
                console.print("plan not found")
                raise typer.Exit(code=1)
            elif r.status_code == 401:
                console.print("not authorized. please verify your token or org")
                raise typer.Exit(code=1)
            elif r.status_code > 399:
                console.print(f"unexpected error: {r.status_code}: {r.json()}")
                raise typer.Exit(code=1)

            return Plan.model_validate(r.json())


def store_plan_context(plan: Plan, target_dir: str) -> dict[str, Any]:
    global_controls = {}

    with console.status("Storing context..."):
        with api_client() as client:
            for int_id in plan.definition.integrations:
                r = client.get(f"/integrations/{int_id}")
                if r.status_code > 399:
                    console.print(
                        f"Plan references integration {int_id} which does "
                        "not exist"
                    )
                    continue

                control = r.json()
                env_id = control.get("environment_id")
                if env_id:
                    load_environment(env_id, target_dir)

                r = client.get(f"/integrations/{int_id}/control")
                control = r.json()
                if control:
                    ctrl_name = control.pop("name")
                    provider = control.get("provider", {})
                    if "secrets" in provider and provider["secrets"] is None:
                        del provider["secrets"]
                    if (
                        "arguments" in provider
                        and provider["arguments"] is None
                    ):
                        del provider["arguments"]
                    ctrl = {ctrl_name: control}
                    global_controls.update(ctrl)

    return global_controls


def load_environment_into_memory(plan: Plan, target_dir: str) -> None:
    with console.status("Loading environment..."):
        if not plan.definition.environment:
            return None

        if not plan.definition.environment.id:
            return None

        env_id = str(plan.definition.environment.id)
        load_environment(env_id, target_dir)


def load_environment(environment_id: str, target_dir: str) -> None:
    with api_client() as client:
        r = client.get(f"/environments/{environment_id}/clear")
        env = Environment.model_validate(r.json())
        if env:
            path_mapping = {}
            for s in env.secrets:
                if isinstance(s, EnvironmentSecretAsFile):
                    new_path = Path(target_dir, s.path.lstrip("/"))
                    new_path.parent.mkdir(mode=0o710, parents=True)
                    new_path.write_text(s.value.get_secret_value())
                    new_path.chmod(0o770)

                    path_mapping[s.path] = str(new_path)

            for e in env.envvars:
                if e.value in path_mapping:
                    os.environ[e.var_name] = path_mapping[e.value]
                else:
                    os.environ[e.var_name] = e.value

            for s in env.secrets:
                if isinstance(s, EnvironmentSecret):
                    v = s.value.get_secret_value()
                    if v in path_mapping:
                        os.environ[s.var_name] = path_mapping[v]
                    else:
                        os.environ[s.var_name] = v


def send_status(plan_id: UUID, status: str, error: str | None = None) -> None:
    with api_client() as client:
        payload = {"status": status, "error": error}
        r = client.put(f"/plans/{str(plan_id)}/status", json=payload)
        if r.status_code == 404:
            console.print("plan not found")
            raise typer.Exit(code=1)
        elif r.status_code == 401:
            console.print("not authorized. please verify your token or org")
            raise typer.Exit(code=1)
        elif r.status_code > 399:
            console.print(f"unexpected error: {r.status_code}: {r.json()}")
            raise typer.Exit(code=1)


def run_chaostoolkit(
    experiment_url: str,
    context: dict[str, Any],
    var_files: list[Path],
    control_files: list[Path],
) -> Journal:
    logger = logging.getLogger("chaostoolkit")

    logger.info("#" * 80)

    rewire_exit_signal_from_ctk()

    logger.info(f"Starting Reliably experiment: {experiment_url}")

    settings = {
        "runtime": {
            "hypothesis": {"strategy": "default"},
            "rollbacks": {"strategy": "always"},
        },
        "controls": {},
    }
    settings_path = os.getenv(
        "CHAOSTOOLKIT_CONFIG_PATH", CHAOSTOOLKIT_CONFIG_PATH
    )
    if os.path.isfile(settings_path):
        s = load_settings(settings_path)
        if s:
            settings = s
            rt = s.setdefault("runtime", {})
            rt.setdefault(
                "hypothesis",
                {"strategy": "default", "fail_fast": False, "freq": 1.0},
            )
            rt.setdefault("rollbacks", {"strategy": "always"})

    if "controls" not in settings:
        settings["controls"] = {}
    settings["controls"].update(context)

    experiment_vars = merge_vars({}, [str(f.absolute()) for f in var_files])

    load_global_controls(settings, [str(f.absolute()) for f in control_files])
    experiment = load_experiment(experiment_url)
    ensure_experiment_is_valid(experiment)

    rt = settings["runtime"]
    x_runtime = experiment.get("runtime")

    if x_runtime:
        is_dry = Dry.from_string(x_runtime.get("dry", ""))
        if is_dry:
            experiment["dry"] = is_dry

        rt["rollbacks"]["strategy"] = (
            x_runtime.get("rollbacks", {}).get("strategy") or "always"
        )
        x_runtime_hypo = x_runtime.get("hypothesis", {})
        rt["hypothesis"]["strategy"] = (
            x_runtime_hypo.get("strategy") or "default"
        )
        if rt["hypothesis"]["strategy"] in (
            "continuously",
            "during-method-only",
        ):
            rt["hypothesis"]["freq"] = float(x_runtime_hypo.get("freq") or 1.0)
            rt["hypothesis"]["fail_fast"] = (
                x_runtime_hypo.get("fail_fast") or False
            )

    dry_strategy = os.getenv("RELIABLY_CLI_DRY_STRATEGY")
    if dry_strategy is not None:
        experiment["dry"] = Dry.from_string(dry_strategy)

    rollback_strategy = os.getenv("RELIABLY_CLI_ROLLBACK_STRATEGY")
    hypothesis_strategy = os.getenv("RELIABLY_CLI_HYPOTHESIS_STRATEGY")

    if rollback_strategy is not None:
        rt["rollbacks"]["strategy"] = rollback_strategy

    if hypothesis_strategy is not None:
        rt["hypothesis"]["strategy"] = hypothesis_strategy

    if rt["hypothesis"]["strategy"] in ("continuously", "during-method-only"):
        hypothesis_freq = os.getenv("RELIABLY_CLI_HYPOTHESIS_STRATEGY_FREQ")
        if hypothesis_freq is not None:
            rt["hypothesis"]["freq"] = float(hypothesis_freq)

        hypothesis_fail_fast = os.getenv(
            "RELIABLY_CLI_HYPOTHESIS_STRATEGY_FAIL_FAST"
        )
        if hypothesis_fail_fast is not None:
            if hypothesis_fail_fast in ("t", "1", "true", "TRUE", "True"):
                rt["hypothesis"]["fail_fast"] = True
            else:
                rt["hypothesis"]["fail_fast"] = False

    schedule = Schedule(
        continuous_hypothesis_frequency=rt["hypothesis"].get("freq", 1),
        fail_fast=rt["hypothesis"].get("fail_fast", False),
    )
    ssh_strategy = Strategy.from_string(rt["hypothesis"]["strategy"])

    journal = run_experiment(
        experiment,
        settings=settings,
        strategy=ssh_strategy,
        schedule=schedule,
        experiment_vars=experiment_vars,
    )

    return journal


@contextlib.contextmanager
def reconfigure_chaostoolkit_logger(
    log_file: Path,
    log_stdout: bool,
) -> Generator[logging.Logger, None, None]:
    from chaosreliably import attach_log_stream_handler

    configure_logger(verbose=True)
    ctk_logger = logging.getLogger("chaostoolkit")

    for handler in list(ctk_logger.handlers):
        ctk_logger.removeHandler(handler)

    fmt = UTCFormatter(
        fmt="[%(asctime)s %(levelname)s] [%(module)s:%(lineno)d] %(message)s",
    )

    handler = logging.FileHandler(log_file.absolute())
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(fmt)
    ctk_logger.addHandler(handler)

    if log_stdout:
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(fmt)
        ctk_logger.addHandler(handler)

    with attach_log_stream_handler(ctk_logger, fmt):
        yield ctk_logger


class UTCFormatter(logging.Formatter):
    def formatTime(
        self, record: logging.LogRecord, datefmt: str | None = None
    ) -> str:
        return datetime.fromtimestamp(
            record.created, tz=timezone.utc
        ).isoformat()


def show_result_url(journal: Journal) -> None:
    for x in journal.get("experiment", {}).get("extensions", []):
        if x["name"] == "reliably":
            url = x.get("execution_url")
            if url:
                console.print(f"Check results at {url}")


def load_experiment(url: str) -> dict[str, Any]:
    token = os.getenv("RELIABLY_TOKEN")
    with httpx.Client(http2=True, verify=should_verify_tls_cert()) as c:
        r = c.get(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/json, application/x-yaml",
            },
        )

        if r.status_code != 200:
            console.print(f"failed to fetch experiment at {url}")
            raise typer.Exit(code=1)

        if r.headers["content-type"] == "application/json":
            return r.json()
        elif r.headers["content-type"] in ("text/yaml", "application/x-yaml"):
            yaml = YAML(typ="safe")
            return yaml.load(r.content.decode("utf-8"))

        console.print("unrecognized experiment format")
        raise typer.Exit(code=1)


def _new_terminate_now(signum: int, frame: FrameType = None) -> None:
    logger = logging.getLogger("chaostoolkit")
    logger.critical("Caught SIGTERM, signaling to the experiment it must end")

    raise SystemExit(30)


def rewire_exit_signal_from_ctk() -> None:
    if os.getenv("RELIABLY_CATCH_SIGTERM_BEFORE_CHAOSTOOLKIT") == "1":
        logger = logging.getLogger("chaostoolkit")
        logger.info("Re-wiring SIGTERM handler to Reliably")

        chaos_exit._terminate_now = _new_terminate_now
