import asyncio
import os

import httpx
import orjson


ENVIRONMENT = {
    "name": "myenv94",
    "envvars": [
        {
            "var_name": "DEMO_VAR",
            "value": "hi"
        },
        {
            "var_name": "GH_REPO",
            "value": "Lawouach/ctkgh"
        }
    ],
    "secrets": [
        {
            "var_name": "GITHUB_TOKEN",
            "value": os.getenv("GITHUB_TOKEN"),
            "key": "gh_token"
        }
    ]
}

ENVIRONMENT9 = {
    "name": "k8s-aws",
    "envvars": [
        {
            "var_name": "AWS_REGION",
            "value": "eu-central-1"
        },
        {
            "var_name": "KUBECONFIG",
            "value": "/home/svc/.kube/config"
        },
        {
            "var_name": "OTEL_EXPORTER_OTLP_TRACES_ENDPOINT",
            "value": os.getenv("OTEL_EXPORTER_OTLP_TRACES_ENDPOINT"),
            "key": "otel_endpoint"
        }
    ],
    "secrets": [
        {
            "key": "kubeconfig",
            "value": open(os.path.expanduser("~/.kube/config")).read(),
            "path": "/home/svc/.kube/config"
        },
        {
            "var_name": "AWS_SECRET_ACCESS_KEY",
            "value": os.getenv("AWS_SECRET_ACCESS_KEY"),
            "key": "aws_secret_key"
        },
        {
            "var_name": "AWS_ACCESS_KEY_ID",
            "value": os.getenv("AWS_ACCESS_KEY_ID"),
            "key": "aws_key_id"
        },
        {
            "var_name": "AWS_ROLE_ARN",
            "value": os.getenv("AWS_ROLE_ARN"),
            "key": "aws_role_arn"
        },
        {
            "var_name": "OTEL_EXPORTER_OTLP_TRACES_HEADERS",
            "value": os.getenv("OTEL_EXPORTER_OTLP_TRACES_HEADERS"),
            "key": "otel_headers"
        }
    ]
}

DEPLOYMENT = {
    "name": "cloud2",
    "definition": {
        "type": "reliably_cloud"
    }
}

PLAN = {
    "environment": {
        "provider": "reliably_cloud",
        "id": ""
    },
    "deployment": {
        "deployment_id": ""
    },
    "schedule": {
        "type": "now"
    },
    "experiments": [],
    "integrations": [],
}

INTEGRATION_SLACK = {
    "name": "communication with team A1",
    "provider": "slack",
    "environment": {
        "name": "slack",
        "envvars": [{
            "var_name": "SLACK_CHANNEL",
            "value": "#demo"
        }],
        "secrets": [{
            "key": "slack-token",
            "var_name": "SLACK_BOT_TOKEN",
            "value": os.getenv("SLACK_TOKEN")
        }]
    }
}

INTEGRATION_OTEL = {
    "name": "send traces",
    "provider": "opentelemetry",
    "environment": {
        "name": "otel",
        "envvars": [{
            "var_name": "OTEL_VENDOR",
            "value": "honeycomb",
        },
        {
            "var_name": "OTEL_EXPORTER_OTLP_TRACES_ENDPOINT",
            "value": os.getenv("OTEL_EXPORTER_OTLP_TRACES_ENDPOINT"),
        }],
        "secrets": [{
            "key": "otel-headers",
            "var_name": "OTEL_EXPORTER_OTLP_TRACES_HEADERS",
            "value": os.getenv("OTEL_EXPORTER_OTLP_TRACES_HEADERS"),
        }]
    }
}

EXPERIMENT_6 = {
    "experiment": orjson.dumps({"version": "1.0.0",
        "title": "DEMO: Terminate pods",
        "description": "n/a",
        "contributions": {
            "security": "low",
            "performance": "none",
            "availability": "high",
            "quality": "none"
        },
        "tags": ["demo"],
        "method": [
            {
                "type": "action",
                "name": "terminate-pod",
                "provider": {
                    "type": "python",
                    "module": "chaosk8s.pod.actions",
                    "func": "terminate_pods",
                    "arguments": {
                        "label_selector": "app=consumer"
                    }
                }
            }
        ]
    }).decode('utf-8'),
}

EXPERIMENT = {
    "experiment": orjson.dumps({
        "version": "1.0.0",
        "title": "DEMO: Teams can sustain a healthy capacity towards closing PRs",
        "description": "n/a",
        "contributions": {
            "security": "low",
            "performance": "none",
            "availability": "low",
            "quality": "high",
        },
        "tags": ["demo"],
        "secrets": {
            "github": {
                "token": {
                    "type": "env",
                    "key": "GITHUB_TOKEN"
                }
            },
        },
        "configuration": {
            "reliably_gh_repo": {
                "type": "env",
                "key": "GH_REPO"
            },
            "reliably_gh_base": "main",
            "reliably_gh_window": "7d",
            "reliably_gh_target": 98
        },
        "method": [],
        "steady-state-hypothesis": {
            "title": "Compute a ratio of closed PRs over a specific period of time",
            "probes": [
                {
                    "type": "probe",
                    "name": "compute-pr-closing-ratio",
                    "tolerance": {
                        "type": "probe",
                        "name": "verifiy-closed-prs-ratio",
                        "provider": {
                            "type": "python",
                            "module": "chaosreliably.activities.gh.tolerances",
                            "func": "ratio_above",
                            "arguments": {
                                "target": "${reliably_gh_target}",
                            },
                        },
                    },
                    "provider": {
                        "type": "python",
                        "module": "chaosreliably.activities.gh.probes",
                        "func": "closed_pr_ratio",
                        "arguments": {
                            "repo": "${reliably_gh_repo}",
                            "base": "${reliably_gh_base}",
                            "window": "${reliably_gh_window}",
                        },
                    },
                },
            ],
        }
    }).decode('utf-8')
}


EXPERIMENT9 = {
    "experiment": orjson.dumps({
        "version": "1.0.0",
        "title": "Temporarily losing capacity does not impact our availability",
        "description": "Evaluate the impact of randomly losing a bit of capacity in the a service. This may inform us if we need to increase or decrease it.",
        "contributions": {
            "availability": "high",
            "security": "none",
            "performance": "none"
        },
        "controls": [
            {
                "name": "opentelemetry",
                "provider": {
                    "type": "python",
                    "module": "chaostracing.oltp",
                    "arguments": {
                        "trace_httpx": True,
                        "trace_requests": True,
                        "trace_botocore": True
                    }
                }
            }
        ],
        "steady-state-hypothesis": {
            "title": "no errors were triggered by a brief loss of capacity",
            "probes": [
                {
                    "type": "probe",
                    "name": "check-endpoint-did-not-respond-with-an-http-error",
                    "tolerance": True,
                    "provider": {
                        "type": "python",
                        "module": "chaosreliably.activities.load.probes",
                        "func": "load_test_result_field_should_be",
                        "arguments": {
                            "result_filepath": "./load-test-results.json",
                            "field": "num_failures",
                            "expect": 0
                        }
                    }
                }
            ]
        },
        "method": [
            {
            "type": "action",
            "name": "inject-traffic-into-endpoint",
            "background": True,
            "provider": {
                "type": "python",
                "module": "chaosreliably.activities.load.actions",
                "func": "inject_gradual_traffic_into_endpoint",
                "arguments": {
                "endpoint": "http://k8s-default-lbdemo-5e83034386-2032033383.eu-central-1.elb.amazonaws.com/consumer/data",
                "step_duration": 5,
                "step_additional_vu": 1,
                "vu_per_second_rate": 1,
                "test_duration": 30,
                "results_json_filepath": "./load-test-results.json"
                }
            }
            },
            {
                "type": "action",
                "name": "terminate-service-pod",
                "provider": {
                    "type": "python",
                    "module": "chaosk8s.pod.actions",
                    "func": "terminate_pods",
                    "arguments": {
                        "label_selector": "app=consumer"
                    }
                },
                "pauses": {
                "before": 10
                }
            }
        ]
    }).decode("utf-8")
}


async def run():
    token = os.getenv("RELIABLY_TOKEN")
    org = os.getenv("RELIABLY_ORG")
    host = os.getenv("RELIABLY_HOST", "https://app.reliably.dev")

    async with httpx.AsyncClient(http2=True, timeout=30) as client:
        client.base_url = httpx.URL(f"{host}/api/v1/organization/{org}")
        client.headers = httpx.Headers(
            {
                "Accept": "application/json; charset=utf-8",
                "Authorization": f"Bearer {token}",
            }
        )

        r = await client.post("/environments", json=ENVIRONMENT)
        if r.status_code > 399:
            print("Environment: ", r.status_code, r.json())
            return
        env_id = r.json()["id"]

        r = await client.post("/deployments", json=DEPLOYMENT)
        if r.status_code > 399:
            print("Deployment: ", r.status_code, r.json())
            return
        dep_id = r.json()["id"]

        r = await client.post("/integrations", json=INTEGRATION_SLACK)
        if r.status_code > 399:
            print("Integration: ", r.status_code, r.json())
            return
        slack_integration_id = r.json()["id"]

        r = await client.post("/integrations", json=INTEGRATION_OTEL)
        if r.status_code > 399:
            print("Integration: ", r.status_code, r.json())
            return
        otel_integration_id = r.json()["id"]

        r = await client.post("/experiments/import", json=EXPERIMENT)
        if r.status_code > 399:
            print("Experiment: ", r.status_code, r.json())
            return
        x_id = r.json()["id"]

        PLAN["environment"]["id"] = env_id
        PLAN["deployment"]["deployment_id"] = dep_id
        PLAN["integrations"] = [otel_integration_id, slack_integration_id]
        PLAN["experiments"].append(x_id)
    
        r = await client.post("/plans", json=PLAN)
        if r.status_code > 399:
            print("Plan: ", r.status_code, r.json())
            return
        plan_id = r.json()["id"]

        print(
            f"Plan {plan_id} - Deployment {dep_id} - "
            f"Environment {env_id} - Experiment {x_id}"
        )


if __name__ == '__main__':
    asyncio.run(run())
