from fastapi import FastAPI
from fastapi.routing import APIRoute

ROUTES = """
/api/v1/user/{user_id}
/api/v1/user
/api/v1/organization
/api/v1/organization/{org_id}/
/api/v1/organization/{org_id}/users
/api/v1/organization/{org_id}/users
/api/v1/organization/{org_id}/users/{user_id}
/api/v1/organization/{org_id}/tokens
/api/v1/organization/{org_id}/tokens
/api/v1/organization/{org_id}/tokens/{token_id}
/api/v1/organization/{org_id}/tokens/{token_id}
/api/v1/organization/{org_id}/deployments
/api/v1/organization/{org_id}/deployments
/api/v1/organization/{org_id}/deployments/{dep_id}
/api/v1/organization/{org_id}/deployments/{dep_id}
/api/v1/organization/{org_id}/plans
/api/v1/organization/{org_id}/plans
/api/v1/organization/{org_id}/plans/{plan_id}
/api/v1/organization/{org_id}/plans/{plan_id}
/api/v1/organization/{org_id}/plans/{plan_id}/status
/api/v1/organization/{org_id}/plans/{plan_id}/executions
/api/v1/organization/{org_id}/experiments
/api/v1/organization/{org_id}/experiments
/api/v1/organization/{org_id}/experiments/import
/api/v1/organization/{org_id}/experiments/all
/api/v1/organization/{org_id}/experiments/summary
/api/v1/organization/{org_id}/experiments/{exp_id}
/api/v1/organization/{org_id}/experiments/{exp_id}
/api/v1/organization/{org_id}/experiments/{exp_id}/raw
/api/v1/organization/{org_id}/experiments/{exp_id}/executions
/api/v1/organization/{org_id}/experiments/{exp_id}/executions
/api/v1/organization/{org_id}/executions
/api/v1/organization/{org_id}/series/executions/per/experiment

/health
/login/with/{provider}
/login/with/github/authorized
/api/me/info
/api/me/tokens
/api/organization/{org_id}/
/api/organization/{org_id}/users
/api/organization/{org_id}/users
/api/organization/{org_id}/users/{user_id}
/api/organization/{org_id}/tokens
/api/organization/{org_id}/tokens
/api/organization/{org_id}/tokens/{token_id}
/api/organization/{org_id}/tokens/{token_id}
/api/organization/{org_id}/deployments
/api/organization/{org_id}/deployments
/api/organization/{org_id}/deployments/{dep_id}
/api/organization/{org_id}/deployments/{dep_id}
/api/organization/{org_id}/plans
/api/organization/{org_id}/plans
/api/organization/{org_id}/plans/{plan_id}
/api/organization/{org_id}/plans/{plan_id}
/api/organization/{org_id}/plans/{plan_id}/status
/api/organization/{org_id}/plans/{plan_id}/executions
/api/organization/{org_id}/experiments
/api/organization/{org_id}/experiments
/api/organization/{org_id}/experiments/import
/api/organization/{org_id}/experiments/all
/api/organization/{org_id}/experiments/summary
/api/organization/{org_id}/experiments/{exp_id}
/api/organization/{org_id}/experiments/{exp_id}
/api/organization/{org_id}/experiments/{exp_id}/raw
/api/organization/{org_id}/experiments/{exp_id}/executions
/api/organization/{org_id}/experiments/{exp_id}/executions
/api/organization/{org_id}/executions
/api/organization/{org_id}/series/executions/per/experiment
"""


def test_load_all_routers(application: FastAPI) -> None:
    EXPECTED_ROUTES = []

    for r in ROUTES.split("\n"):
        r = r.strip()
        if not r:
            continue
        EXPECTED_ROUTES.append(APIRoute(r, lambda: None))

    for r in application.router.routes:
        if isinstance(r, APIRoute):
            for er in EXPECTED_ROUTES[:]:
                if r.path == er.path:
                    EXPECTED_ROUTES.remove(er)
                    break

    assert len(EXPECTED_ROUTES) == 0, print(
        list(r.path for r in EXPECTED_ROUTES)
    )
