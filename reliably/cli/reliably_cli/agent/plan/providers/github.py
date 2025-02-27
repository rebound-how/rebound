import os

import httpx
from anyio.abc import CancelScope

from reliably_cli.config import get_settings
from reliably_cli.log import console
from reliably_cli.types import Plan

from . import set_plan_status

__all__ = ["schedule_plan"]


async def schedule_plan(plan: Plan) -> None:
    settings = get_settings()
    gh_provider = settings.plan.providers.github
    plan_id = str(plan.id)

    gh_token = os.getenv(
        "GITHUB_TOKEN",
        gh_provider.token.get_secret_value() if gh_provider.token else None,
    )

    if not gh_token:
        raise RuntimeError(
            "you must specify a suitable GitHub token, either in "
            "the Reliably configuration file or via the "
            "GITHUB_TOKEN environment variable"
        )

    gh_workflow_id = gh_provider.workflow_id
    gh_api_url = os.getenv("GITHUB_API_URL", gh_provider.api_url)
    gh_repo = os.getenv("GITHUB_REPOSITORY", gh_provider.repo)
    gh_ref = os.getenv("GITHUB_REF_NAME", gh_provider.ref)

    gh_attrs = {
        "reliably.plan_id": plan_id,
        "reliably.deployment_type": "github",
        "reliably.gh_actor": os.getenv("GITHUB_ACTOR", ""),
        "reliably.gh_event_name": os.getenv("GITHUB_EVENT_NAME", ""),
        "reliably.gh_job_id": os.getenv("GITHUB_JOB", ""),
        "reliably.gh_ref": gh_ref,
        "reliably.gh_ref_type": os.getenv("GITHUB_REF_TYPE", ""),
        "reliably.gh_repo": gh_repo,
        "reliably.gh_run_id": os.getenv("GITHUB_RUN_ID", ""),
        "reliably.gh_sha": os.getenv("GITHUB_SHA", ""),
    }
    # avoid empty attributes
    for k, v in list(gh_attrs.items()):
        if v == "":
            gh_attrs.pop(k)

    with CancelScope(shield=True) as scope:
        try:
            console.print(f"Schedule plan {plan.id} on GitHub")

            exp_id = plan.definition.experiments[0]
            experiment_url = (
                f"{settings.service.host}/api/v1"
                f"/organization/{settings.organization.id}"
                f"/experiments/{exp_id}/raw"
            )
            console.print(f"Scheduling experiment {experiment_url}")

            url = (
                f"{gh_api_url}/repos/{gh_repo}/actions"
                f"/workflows/{gh_workflow_id}/dispatches"
            )

            console.print(f"Calling GitHub workflow at {url}")
            async with httpx.AsyncClient() as h:
                r = await h.post(
                    url,
                    headers={
                        "Accept": "application/vnd.github+json",
                        "Authorization": f"Bearer {gh_token}",
                    },
                    json={
                        "ref": gh_ref,
                        "inputs": {
                            "experiment-url": experiment_url,
                            "environment-name": "myenv",
                        },
                    },
                )
                if r.status_code == 204:
                    console.print(f"Plan {plan_id} scheduled")
                else:
                    console.print(
                        f"Failed to schedule plan {plan_id}: "
                        f"{r.status_code} - {r.json()}"
                    )
        except Exception as x:
            await set_plan_status(plan_id, "creation error", str(x))
            console.print(f"Failed to schedule plan {plan_id}", exc_info=True)
            raise
        finally:
            await set_plan_status(plan_id, "created")

            scope.cancel()
