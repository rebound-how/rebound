import asyncio
import io
import logging
from base64 import b64decode, b64encode
from typing import Tuple, cast
from urllib.parse import urlparse

import httpx
import orjson
from pydantic import BaseModel, HttpUrl, SecretStr
from ruamel.yaml import YAML

from reliably_app import deployment
from reliably_app.config import get_settings
from reliably_app.plan import schemas
from reliably_app.plan.errors import PlanFailedError

__all__ = ["delete_plan", "execute_plan"]


logger = logging.getLogger("reliably_app")
DEFAULT_WORKFLOW = b"""name: Execute a Reliably Plan

on:

jobs:
  execute-reliably-plan:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: reliablyhq/actions/plan@main
"""


class GitHubContext(BaseModel):
    token: SecretStr
    api_host: HttpUrl
    dir_url: HttpUrl
    repo: str
    env_name: str | None = None
    workflow_id: str | None = None
    ref: str
    actor: str | None
    schedule: str | None
    plan_base_dir: str
    content_base_url: str
    email: str
    experiment_url: str
    reliably_host: str


async def execute_plan(
    plan: schemas.Plan, dep: deployment.schemas.Deployment, org_id: str
) -> None:
    context = prepare_context(plan, dep, org_id)

    workflow_id = await configure_workflow(plan, context)
    if workflow_id and context.schedule is None:
        await trigger_workflow(plan, context, workflow_id)


async def delete_plan(
    plan: schemas.Plan, dep: deployment.schemas.Deployment, org_id: str
) -> None:
    logger.info(f"Deleting plan {str(plan.id)} from Reliably")

    context = prepare_context(plan, dep, org_id)

    await delete_workflow(plan, context)


async def suspend_plan(
    plan: schemas.Plan,
    dep: deployment.schemas.Deployment,
) -> None:
    plan_id = str(plan.id)
    git = prepare_context(plan, dep, str(plan.org_id))
    workflow_id = f"reliably-plan-{plan_id}.yaml"

    url = (
        f"{str(git.api_host).rstrip('/')}/repos/{git.repo}/actions"
        f"/workflows/{workflow_id}/disable"
    )
    logger.debug(f"Pausing GitHub workflow at {url}")

    async with httpx.AsyncClient(http2=True) as h:
        r = await h.put(
            url,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {git.token.get_secret_value()}",
            },
        )
        if r.status_code == 204:
            logger.info(f"Plan {plan_id} triggered")
        else:
            msg = r.json()
            logger.error(
                f"Failed to pause workflow {workflow_id}: "
                f"{r.status_code} - {msg}"
            )
            raise PlanFailedError(plan_id, msg.get("message", str(msg)))


async def resume_plan(
    plan: schemas.Plan,
    dep: deployment.schemas.Deployment,
) -> None:
    plan_id = str(plan.id)
    git = prepare_context(plan, dep, str(plan.org_id))
    workflow_id = f"reliably-plan-{plan_id}.yaml"

    url = (
        f"{str(git.api_host).rstrip('/')}/repos/{git.repo}/actions"
        f"/workflows/{workflow_id}/enable"
    )
    logger.debug(f"Resuming GitHub workflow at {url}")

    async with httpx.AsyncClient(http2=True) as h:
        r = await h.put(
            url,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {git.token.get_secret_value()}",
            },
        )
        if r.status_code == 204:
            logger.info(f"Plan {plan_id} triggered")
        else:
            msg = r.json()
            logger.error(
                f"Failed to resume workflow {workflow_id}: "
                f"{r.status_code} - {msg}"
            )
            raise PlanFailedError(plan_id, msg.get("message", str(msg)))


###############################################################################
# Private functions
###############################################################################
def prepare_context(
    plan: schemas.Plan, dep: deployment.schemas.Deployment, org_id: str
) -> GitHubContext:
    settings = get_settings()
    plan_id = str(plan.id)

    reliably_host = settings.RELIABLY_DOMAIN
    reliably_host = reliably_host.replace("https://", "")
    exp_id = plan.definition.experiments[0]
    experiment_url = (
        f"https://{reliably_host}/api/v1"
        f"/organization/{org_id}"
        f"/experiments/{exp_id}/raw"
    )

    gh_provider = cast(
        deployment.schemas.DeploymentGitHubDefinition, dep.definition
    )

    gh_env_name = None
    gh_repo = ""
    gh_schedule = None
    gh_token = None
    if plan.definition.schedule.type == "cron":
        gh_schedule = plan.definition.schedule.pattern

    repo_parts = urlparse(str(gh_provider.repo))
    gh_env_name = plan.definition.environment.name  # type: ignore
    gh_repo = str(repo_parts.path).strip("/")
    gh_actor = gh_provider.username
    gh_token = gh_provider.clear_token

    if not gh_token:
        raise PlanFailedError(
            plan_id, "you must specify a token in the deployment"
        )

    gh_api_url = f"{str(repo_parts.scheme)}://api.{str(repo_parts.netloc)}"
    gh_ref = gh_provider.ref

    if not gh_repo:
        raise PlanFailedError(plan_id, "you must specify a repository")

    email = f"{gh_actor}@users.noreply.github.com"
    plan_base_dir = f"{gh_provider.base_dir}/{plan_id}"
    base_url = f"{gh_api_url}/repos/{gh_repo}/contents"

    gh_host = gh_api_url.replace("api.", "")
    dir_url = f"{gh_host}/{gh_repo}/tree/{gh_ref}/{plan_base_dir}"

    return GitHubContext(
        token=gh_token,
        repo=gh_repo,
        dir_url=dir_url,
        api_host=gh_api_url,
        ref=gh_ref,
        actor=gh_actor,
        schedule=gh_schedule,
        email=email,
        env_name=gh_env_name,
        content_base_url=base_url,
        plan_base_dir=plan_base_dir,
        experiment_url=experiment_url,
        reliably_host=reliably_host,
    )


async def configure_workflow(
    plan: schemas.Plan, git: GitHubContext
) -> str | None:
    plan_id = str(plan.id)
    org_id = str(plan.org_id)

    yaml = YAML(typ="safe", pure=True)
    w, w_sha = await get_repository_workflow(git, plan_id)
    workflow = yaml.load(w)

    workflow["name"] = f"Reliably Plan {plan_id}"

    if workflow["on"] is None:
        workflow["on"] = {}

    if git.schedule:
        workflow["on"]["schedule"] = [{"cron": git.schedule}]
    else:
        workflow["on"].setdefault("workflow_dispatch", {})

    for job in workflow["jobs"].values():
        if git.env_name:
            job["environment"] = git.env_name

        for step in job["steps"]:
            uses = step.get("uses")
            if uses and uses.startswith("reliablyhq/actions/plan"):
                step_with = step.setdefault("with", {})
                step_with["working-dir"] = git.plan_base_dir
                step_with["reliably-host"] = git.reliably_host
                step_with["plan-id"] = plan_id
                step_with["org-id"] = org_id
                step_with["reliably-experiment-extra"] = orjson.dumps(
                    [
                        {
                            "type": "url",
                            "provider": "github",
                            "topic": "commit",
                            "value": str(git.dir_url).rstrip("/"),
                        }
                    ]
                ).decode("utf-8")

                if "reliably-service-token" not in step_with:
                    at = r"${{ secrets.RELIABLY_SERVICE_TOKEN }}"  # nosec B105
                    step_with["reliably-service-token"] = at

                if "github-token" not in step_with:
                    gh_token = r"${{ secrets.GITHUB_TOKEN }}"  # nosec B105
                    step_with["github-token"] = gh_token

    yaml.default_flow_style = False
    with io.StringIO() as s:
        yaml.dump(workflow, s)
        content = s.getvalue().encode("utf-8")

    async with httpx.AsyncClient(http2=True) as h:
        gh_workflow_id = f"reliably-plan-{plan_id}.yaml"
        url = f"{git.content_base_url}/.github/workflows/{gh_workflow_id}"

        logger.info(f"Trying to add workflow plan at '{url}'")

        r = await h.put(
            url,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {git.token.get_secret_value()}",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            json={
                "message": f"Add workflow for Plan {plan_id}",
                "committer": {"name": git.actor, "email": git.email},
                "content": b64encode(content).decode("utf-8"),
                "sha": w_sha,
            },
        )
        # no changes to the plan so we need to manually trigger the dispatch
        if r.status_code == 200:
            logger.debug(f"Triggering workflow {gh_workflow_id}")
            r = await h.post(
                f"{url}/dispatches",
                headers={
                    "Accept": "application/vnd.github+json",
                    "Authorization": f"Bearer {git.token.get_secret_value()}",
                    "X-GitHub-Api-Version": "2022-11-28",
                },
                json={
                    "ref": git.ref,
                },
            )
            return gh_workflow_id
        elif r.status_code == 201:
            logger.debug(
                f"Workflow {gh_workflow_id} added to repository {git.repo}"
            )
            return gh_workflow_id
        else:
            msg = r.json()
            logger.error(
                f"Failed to schedule plan {plan_id}: {r.status_code} - {msg}"
            )
            raise PlanFailedError(plan_id, msg.get("message", str(msg)))


async def trigger_workflow(
    plan: schemas.Plan, git: GitHubContext, workflow_id: str
) -> None:
    # GH needs to fully make the plan visible to trigger it
    # it's unfortunate but eventual consistency is what we have
    await asyncio.sleep(1)

    plan_id = str(plan.id)

    url = (
        f"{str(git.api_host).rstrip('/')}/repos/{git.repo}/actions"
        f"/workflows/{workflow_id}/dispatches"
    )
    logger.debug(f"Calling GitHub workflow at {url}")

    async with httpx.AsyncClient(http2=True) as h:
        r = await h.post(
            url,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {git.token.get_secret_value()}",
            },
            json={"ref": git.ref, "inputs": {}},
        )
        if r.status_code == 204:
            logger.info(f"Plan {plan_id} triggered")
        else:
            msg = r.json()
            logger.error(
                f"Failed to trigger workflow {workflow_id}: "
                f"{r.status_code} - {msg}"
            )
            raise PlanFailedError(plan_id, msg.get("message", str(msg)))


async def delete_workflow(plan: schemas.Plan, git: GitHubContext) -> None:
    plan_id = str(plan.id)
    workflow_id = f"reliably-plan-{plan_id}.yaml"
    url = f"{git.content_base_url}/.github/workflows/{workflow_id}"
    logger.debug(f"Calling GitHub workflow at {url}")

    async with httpx.AsyncClient(http2=True) as h:
        r = await h.get(
            url,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {git.token.get_secret_value()}",
            },
        )
        if r.status_code == 401:
            logger.warning(
                f"GitHub credentials are not valid for plan {plan_id}."
                f"Let's assume the user deleted the token directly."
                "Nothing we can do."
            )
            return None
        elif r.status_code == 404:
            logger.warning(
                f"Workflow '{workflow_id}' does not exist in "
                f"repository {git.repo}"
            )
            return None
        elif r.status_code > 399:
            raise PlanFailedError(
                str(plan.id),
                f"Failed to retrieve GitHub workflow '{workflow_id}' "
                f"in repository {git.repo} "
                f"{r.status_code} => {r.text}",
            )

        content = r.json()
        sha = content["sha"]

        r = await h.request(
            "DELETE",
            url,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {git.token.get_secret_value()}",
            },
            json={
                "message": f"Remove workflow as Plan {plan_id} was deleted",
                "committer": {"name": git.actor, "email": git.email},
                "sha": sha,
                "branch": git.ref,
            },
        )
        if r.status_code > 399:
            raise PlanFailedError(
                str(plan.id),
                f"Failed to remove GitHub workflow '{workflow_id}' "
                f"from repository {git.repo} "
                f"{r.status_code} => {r.text}",
            )


async def get_repository_workflow(
    git: GitHubContext, plan_id: str, default: bytes = DEFAULT_WORKFLOW
) -> Tuple[bytes, str | None]:
    async with httpx.AsyncClient(http2=True, timeout=60) as h:
        url = f"{git.content_base_url}/.github/workflows/reliably-plan-{plan_id}.yaml"  # noqa
        r = await h.get(
            url,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {git.token.get_secret_value()}",
            },
        )

        if r.status_code == 200:
            payload = r.json()
            sha = payload["sha"]
            if payload["encoding"] == "base64":
                return b64decode(payload["content"]), sha

        url = f"{git.content_base_url}/.github/workflows/reliably-plan.yaml"
        r = await h.get(
            url,
            headers={
                "Accept": "application/vnd.github.raw",
                "Authorization": f"Bearer {git.token.get_secret_value()}",
            },
        )

        if r.status_code == 404:
            return default, None

        if r.status_code > 399:
            logger.warning(
                f"Failed to fetch from {url}: {r.status_code} - {r.text}"
            )
            return default, None

        logger.debug(f"Using workflow from {url}")
        return r.text.encode("utf-8"), None
