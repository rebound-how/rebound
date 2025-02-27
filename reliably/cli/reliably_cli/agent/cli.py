import signal
from typing import Awaitable

import anyio
import trio
import typer
from anyio.abc import CancelScope

from ..config import get_settings
from ..log import console
from . import agent_runner, validate_agent_configuration

cli = typer.Typer()


@cli.command()
def run() -> None:
    try:
        validate_agent_configuration()
    except ValueError:
        raise typer.Exit(1)

    trio.run(_main, agent_runner)


##############################################################################
# Private
##############################################################################
async def signal_handler(scope: CancelScope):
    with anyio.open_signal_receiver(
        signal.SIGINT, signal.SIGTERM, signal.SIGHUP
    ) as signals:
        console.print("Listening for system signals...")
        async for signum in signals:
            console.print(
                f"Signal '{signal.strsignal(signum) or signum}' received"
            )
            if signum == signal.SIGHUP:
                console.print("Reloading configuration")
                get_settings.cache_clear()
                get_settings()
                console.print("Configuration reloaded")
            else:
                scope.cancel()
                return


async def _main(runner: Awaitable) -> None:
    console.print("Agent ready to run")

    async with anyio.create_task_group() as tg:
        tg.start_soon(signal_handler, tg.cancel_scope)
        tg.start_soon(runner, tg.cancel_scope)

    console.print("Agent terminated. Exiting...")
