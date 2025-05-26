import logging
import textwrap
import importlib.resources
from pathlib import Path
from typing import Any, AsyncIterable, Dict, List

import orjson
from magentic import (
    AssistantMessage,
    OpenaiChatModel,
    SystemMessage,
    UserMessage,
    chatprompt,
)
from magentic.chatprompt import escape_braces
from pydantic import UUID4

from reliably_app import background
from reliably_app.assistant import crud
from reliably_app.assistant.schemas import ScenarioItem, ScenarioItemParameter
from reliably_app.config import get_settings
from reliably_app.database import SessionLocal
from reliably_app.observability import span

__all__ = ["generate_scenario"]

logger = logging.getLogger("reliably_app")


def generate_scenario(
    scenario_id: UUID4, api_key: str, query: str, tags: List[str]
) -> None:
    name = f"assistant-scenario-{str(scenario_id)}"
    background.add_background_async_task(
        generate(scenario_id, api_key, query, tags), name=name
    )


###############################################################################
# Private functions
###############################################################################
async def generate(
    scenario_id: UUID4, api_key: str, query: str, tags: List[str]
) -> None:
    attrs = {"scenario_id": str(scenario_id)}
    with span("generate-assistant-scenario", attributes=attrs) as spanit:
        try:
            settings = get_settings()

            if not settings.ASSISTANT_SCENARIO_ENABLED:
                spanit.set_attribute("enabled", "false")
                return None

            # force Reliably related activities to be taken into account
            tags.append("reliability")

            @chatprompt(
                get_initial_system_message(tags),
                *get_assistant_examples(),
                UserMessage("{query}"),
            )
            async def get_reliably_scenario(  # type: ignore[empty-body]  # noqa
                query: str,
            ) -> AsyncIterable[ScenarioItem]: ...

            with OpenaiChatModel(
                api_type="openai",
                api_key=api_key,
                model=settings.ASSISTANT_SCENARIO_MODEL,
                temperature=1,
            ):
                async for item in await get_reliably_scenario(query):
                    async with SessionLocal() as db:
                        await crud.update_scenario_suggestion(
                            db, scenario_id, item
                        )
        except Exception as x:
            spanit.record_exception(x)
            logger.error(
                f"Failed to generate assistant response for scenario {scenario_id}",  # noqa E501
                exc_info=True,
            )
            async with SessionLocal() as db:
                await crud.store_error(db, scenario_id, str(x))
        finally:
            async with SessionLocal() as db:
                await crud.mark_as_completed(db, scenario_id)


def filter_by_tags(catalog: bytes, tags: List[str]) -> str:
    lib: List[Dict[str, Any]] = orjson.loads(catalog)

    query_tags = set(tags)

    candidates = []
    for item in lib:
        item_tags = set(item["tags"])
        if query_tags.intersection(item_tags):
            candidates.append(item)

    return orjson.dumps(candidates).decode("utf-8")


def load_library() -> bytes:
    settings = get_settings()

    lib_file: Path | None = settings.ASSISTANT_LIBRARY_FILE

    if lib_file is None:
        with importlib.resources.path("reliably_app.data", "catalog.json") as p:
            if not p.absolute().is_file():
                raise RuntimeError("Default assistant library not found")

            return p.read_bytes()

    if not lib_file.exists():
        raise RuntimeError("Assistant library file does not exist")

    return lib_file.read_bytes()


def get_initial_system_message(tags: List[str]) -> SystemMessage:
    catalog = filter_by_tags(load_library(), tags)

    return SystemMessage(
        escape_braces(
            textwrap.dedent(
                f"""
                [no prose] [Output JSON Only]

                You are senior engineering manager and you are tasked to respond to leadership new objectives or risks assessments.
                                    
                You want to output a series of operations from the list below that create a
                scenario appropriate for performing an analysis on when things will start
                degrading.

                Here is the list, in json format. Use only items from this list for your reply. Never create your own operation.

                ```json
                {catalog}
                ```

                Be smart about it. Assume the following:

                * try to use an incremental approach when appropriate
                * DO NOT run the load test more than once
                * use the `purpose` property to explain the rationale for each operation in the context of the scenario
                * keep only required parameters of each operation
                * make sure required parameters are present in the output for each operation, even when they have a default value
                * update the name property so it reflects the purpose of the operation, but make the title human oriented. It should neatly convey the reason for this operation at this time
                * use the related operations, when an operation declares any, to help you complete the scenario. Notably the rollbacks. Make sure you match the number of rollbacks with the number of operations you introduced.
                """  # noqa E501
            )
        )
    )


def get_assistant_examples() -> List[AssistantMessage]:
    return [
        AssistantMessage(
            [
                ScenarioItem(
                    name="Run typical user traffic",
                    ref="reliably-load-run_load_test",
                    tags=["performance"],
                    type="action",
                    background=True,
                    purpose="Load traffic into our application using a typical Monday morning shape",  # noqa E501
                    parameters=[
                        ScenarioItemParameter(
                            key="url",
                            type="string",
                            title="URL under Test",
                            required=True,
                        ),
                        ScenarioItemParameter(
                            key="duration",
                            type="integer",
                            title="Duration of Test",
                            required=True,
                            default=60,
                        ),
                    ],
                ),
                ScenarioItem(
                    name="Let system warm-up",
                    ref="reliably-pauses-pause_execution",
                    tags=["workflow"],
                    type="action",
                    background=False,
                    purpose="Give our system a chance to warm up",
                    parameters=[
                        ScenarioItemParameter(
                            key="duration",
                            type="integer",
                            title="Pause Duration",
                            required=True,
                            default=5,
                        )
                    ],
                ),
                ScenarioItem(
                    name="Introduce latency into Kubernetes service",
                    ref="k8s-chaosmesh-add_latency",
                    tags=["k8s"],
                    type="action",
                    background=False,
                    purpose="Inject latency between source and target services",
                    parameters=[
                        ScenarioItemParameter(
                            key="name",
                            type="string",
                            title="First Fault Name",
                            required=True,
                        ),
                        ScenarioItemParameter(
                            key="latency",
                            type="string",
                            title="Latency Amount",
                            required=True,
                        ),
                        ScenarioItemParameter(
                            key="label_selectors",
                            type="string",
                            title="Source Label Selector",
                            required=True,
                        ),
                        ScenarioItemParameter(
                            key="target_label_selectors",
                            type="string",
                            title="Target Label Selector",
                            required=True,
                        ),
                    ],
                ),
                ScenarioItem(
                    name="Let system degrade for a while",
                    ref="reliably-pauses-pause_execution",
                    tags=["workflow"],
                    type="action",
                    background=False,
                    purpose="Observe system degradation",
                    parameters=[
                        ScenarioItemParameter(
                            key="duration",
                            type="integer",
                            title="Pause Duration",
                            required=True,
                            default=45,
                        )
                    ],
                ),
                ScenarioItem(
                    name="Increase latency between services",
                    ref="k8s-chaosmesh-add_latency",
                    tags=["k8s"],
                    type="action",
                    background=False,
                    purpose="degrade the system even further",
                    parameters=[
                        ScenarioItemParameter(
                            key="name",
                            type="string",
                            title="Second Fault Name",
                            required=True,
                        ),
                        ScenarioItemParameter(
                            key="latency",
                            type="string",
                            title="Latency Amount",
                            required=True,
                        ),
                        ScenarioItemParameter(
                            key="label_selectors",
                            type="string",
                            title="Source Label Selector",
                            required=True,
                        ),
                        ScenarioItemParameter(
                            key="target_label_selectors",
                            type="string",
                            title="Target Label Selector",
                            required=True,
                        ),
                    ],
                ),
                ScenarioItem(
                    name="System is now fully degraded",
                    ref="reliably-pauses-pause_execution",
                    tags=["workflow"],
                    type="action",
                    background=False,
                    purpose="Observe system degradation",
                    parameters=[
                        ScenarioItemParameter(
                            key="duration",
                            type="integer",
                            title="Pause Duration",
                            required=True,
                        )
                    ],
                ),
                ScenarioItem(
                    name="Increase latency between services",
                    ref="k8s-chaosmesh-delete_network_fault",
                    tags=["k8s"],
                    type="action",
                    background=False,
                    purpose="Remove first system degradation",
                    parameters=[
                        ScenarioItemParameter(
                            key="name",
                            type="string",
                            title="First Fault Name",
                            required=True,
                        ),
                    ],
                ),
                ScenarioItem(
                    name="Increase latency between services",
                    ref="k8s-chaosmesh-delete_network_fault",
                    tags=["k8s"],
                    type="action",
                    background=False,
                    purpose="Remove second system degradation",
                    parameters=[
                        ScenarioItemParameter(
                            key="name",
                            type="string",
                            title="Second Fault Name",
                            required=True,
                        ),
                    ],
                ),
            ],
        ),
        AssistantMessage(
            [
                ScenarioItem(
                    name="Run typical user traffic",
                    ref="reliably-load-run_load_test",
                    tags=["performance"],
                    type="action",
                    background=True,
                    purpose="Load traffic into our application using a typical Monday morning shape",  # noqa E501
                    parameters=[
                        ScenarioItemParameter(
                            key="url",
                            type="string",
                            title="URL under Test",
                            required=True,
                        ),
                        ScenarioItemParameter(
                            key="duration",
                            type="integer",
                            title="Duration of Test",
                            required=True,
                            default=60,
                        ),
                    ],
                ),
                ScenarioItem(
                    name="Delete one pod",
                    ref="k8s-pod-delete_pod",
                    tags=["reliability", "availability"],
                    type="action",
                    background=False,
                    purpose="Delete an applicationb pod and let the system self-heal",  # noqa E501
                    parameters=[
                        ScenarioItemParameter(
                            key="ns",
                            type="string",
                            title="Pod Namespace",
                            default="default",
                            required=True,
                        ),
                        ScenarioItemParameter(
                            key="label_selector",
                            type="string",
                            title="Pod Label Selector",
                            required=True,
                        ),
                    ],
                ),
                ScenarioItem(
                    name="Let system self-heal",
                    ref="reliably-pauses-pause_execution",
                    tags=["workflow"],
                    type="action",
                    background=False,
                    purpose="Give our system a chance to self-heal",
                    parameters=[
                        ScenarioItemParameter(
                            key="duration",
                            type="integer",
                            title="Pause Duration",
                            required=True,
                            default=5,
                        )
                    ],
                ),
                ScenarioItem(
                    name="Let system self-heal",
                    ref="k8s-deployment-deployment_available_and_healthy",
                    tags=["reliability", "availability"],
                    type="probe",
                    background=False,
                    purpose="Our application is now back and healthy",
                    parameters=[
                        ScenarioItemParameter(
                            key="name",
                            type="string",
                            title="Deployment Name",
                            required=True,
                        ),
                        ScenarioItemParameter(
                            key="ns",
                            type="string",
                            title="Deployment Namespace",
                            default="default",
                            required=True,
                        ),
                        ScenarioItemParameter(
                            key="label_selector",
                            type="string",
                            title="Deployment Label Selector",
                            required=False,
                        )
                    ],
                ),
            ]
        ),
        AssistantMessage(
            [
                ScenarioItem(
                    name="Run typical user traffic",
                    ref="reliably-load-run_load_test",
                    tags=["performance"],
                    type="action",
                    background=True,
                    purpose="Load traffic into our application using a typical Monday morning shape",  # noqa E501
                    parameters=[
                        ScenarioItemParameter(
                            key="url",
                            type="string",
                            title="URL under Test",
                            required=True,
                        ),
                        ScenarioItemParameter(
                            key="duration",
                            type="integer",
                            title="Duration of Test",
                            required=True,
                            default=60,
                        ),
                    ],
                ),
                ScenarioItem(
                    name="Let system warm-up",
                    ref="reliably-pauses-pause_execution",
                    tags=["workflow"],
                    type="action",
                    background=False,
                    purpose="Give our system a chance to warm up",
                    parameters=[
                        ScenarioItemParameter(
                            key="duration",
                            type="integer",
                            title="Pause Duration",
                            required=True,
                            default=5,
                        )
                    ],
                ),
                ScenarioItem(
                    name="Add delay from service response",
                    ref="gcp-lb-add-latency-to-endpoint",
                    tags=["google cloud", "load balancer"],
                    type="action",
                    background=False,
                    purpose="Set latency to URL",
                    parameters=[
                        ScenarioItemParameter(
                            key="url",
                            type="string",
                            title="Endpoint to add the latency to",
                            required=True,
                        ),
                        ScenarioItemParameter(
                            key="project_id",
                            type="string",
                            title="GCP project where the load balancer resides",
                            required=True,
                        ),
                        ScenarioItemParameter(
                            key="latency",
                            type="float",
                            title="Latency to set in seconds",
                            required=True,
                        ),
                        ScenarioItemParameter(
                            key="percentage",
                            type="float",
                            title="Volume of requests to impact with the delay",
                            required=True,
                        ),
                    ],
                ),
                ScenarioItem(
                    name="Keep system under duress for a while",
                    ref="reliably-pauses-pause_execution",
                    tags=["workflow"],
                    type="action",
                    background=False,
                    purpose="Give ourself a chance to observe the impacts",
                    parameters=[
                        ScenarioItemParameter(
                            key="duration",
                            type="integer",
                            title="Pause Duration",
                            required=True,
                        )
                    ],
                ),
                ScenarioItem(
                    name="Get SLO healths for URl endpoint",
                    ref="gcp-monitoring-get_slo_health_from_url",
                    tags=["workflow"],
                    type="action",
                    background=False,
                    purpose="Have we impacted our users?",
                    parameters=[
                        ScenarioItemParameter(
                            key="url",
                            type="string",
                            title="URL",
                            required=True,
                        )
                    ],
                ),
            ]
        ),
        AssistantMessage(
            [
                ScenarioItem(
                    name="Run typical user traffic",
                    ref="reliably-load-run_load_test",
                    tags=["performance"],
                    type="action",
                    background=True,
                    purpose="Load traffic into our application using a typical Monday morning shape",  # noqa E501
                    parameters=[
                        ScenarioItemParameter(
                            key="url",
                            type="string",
                            title="URL under Test",
                            required=True,
                        ),
                        ScenarioItemParameter(
                            key="duration",
                            type="integer",
                            title="Duration of Test",
                            required=True,
                        ),
                    ],
                ),
                ScenarioItem(
                    name="Let system warm-up",
                    ref="reliably-pauses-pause_execution",
                    tags=["workflow"],
                    type="action",
                    background=False,
                    purpose="Give our system a chance to warm up",
                    parameters=[
                        ScenarioItemParameter(
                            key="duration",
                            type="integer",
                            title="Pause Duration",
                            required=True,
                        )
                    ],
                ),
                ScenarioItem(
                    name="Move workload from some nodes to others",
                    ref="k8s-node-drain_nodes",
                    tags=["kubernetes"],
                    type="action",
                    background=False,
                    purpose="Move our workload from 5% of our cluster somewhere else",  # noqa E501
                    parameters=[
                        ScenarioItemParameter(
                            key="label_selector",
                            type="string",
                            title="Target Node Label Selector",
                            required=True,
                        )
                    ],
                ),
                ScenarioItem(
                    name="pause_experiment",
                    ref="reliably-pauses-pause_execution",
                    tags=["workflow"],
                    type="action",
                    background=False,
                    purpose="Let's wait for the system to settle",
                    parameters=[
                        ScenarioItemParameter(
                            key="duration",
                            type="integer",
                            title="Pause Duration",
                            required=True,
                        )
                    ],
                ),
                ScenarioItem(
                    name="drain_node",
                    ref="k8s-node-drain_nodes",
                    tags=["kubernetes"],
                    type="action",
                    background=False,
                    purpose="Move our workload from another 10% of our cluster somewhere else",  # noqa E501
                    parameters=[
                        ScenarioItemParameter(
                            key="label_selector",
                            type="string",
                            title="Target Node Label Selector",
                            required=True,
                        )
                    ],
                ),
                ScenarioItem(
                    name="pause_experiment",
                    ref="reliably-pauses-pause_execution",
                    tags=["workflow"],
                    type="action",
                    background=False,
                    purpose="Let's wait for the system to settle",
                    parameters=[
                        ScenarioItemParameter(
                            key="duration",
                            type="integer",
                            title="Pause Duration",
                            required=True,
                        )
                    ],
                ),
            ]
        ),
        AssistantMessage(
            [
                ScenarioItem(
                    name="Run typical user traffic",
                    ref="reliably-load-run_load_test",
                    tags=["performance"],
                    type="action",
                    background=True,
                    purpose="Load traffic into our application using a typical traffic of an intense peak day",  # noqa E501
                    parameters=[
                        ScenarioItemParameter(
                            key="url",
                            type="string",
                            title="URL under Test",
                            required=True,
                        ),
                        ScenarioItemParameter(
                            key="duration",
                            type="integer",
                            title="Duration of Test",
                            required=True,
                        ),
                    ],
                ),
                ScenarioItem(
                    name="Let system warm-up",
                    ref="reliably-pauses-pause_execution",
                    tags=["workflow"],
                    type="action",
                    background=False,
                    purpose="Give our system a chance to warm up",
                    parameters=[
                        ScenarioItemParameter(
                            key="duration",
                            type="integer",
                            title="Pause Duration",
                            required=True,
                        )
                    ],
                ),
                ScenarioItem(
                    name="Simulate the impact of a complete loss of an AWS Availability Zone on Users",  # noqa E501
                    ref="aws-fis-start_availability_zone_power_interruption_scenario",  # noqa E501
                    tags=["aws", "fis"],
                    type="action",
                    background=False,
                    purpose="Shutdown or remove resources in a various set of AWS services (EC2, ASG, subnets...) so that we can simulate a power loss of an AZ",  # noqa E501
                    parameters=[
                        ScenarioItemParameter(
                            key="az",
                            type="string",
                            title="Availability-Zone",
                            required=True,
                            default="us-east-1a",
                        ),
                    ],
                ),
                ScenarioItem(
                    name="Observe our system while disruption takes places",
                    ref="reliably-pauses-pause_execution",
                    tags=["workflow"],
                    type="action",
                    background=False,
                    purpose="We allow time to observe and investigate the system while it is degraded",  # noqa E501
                    parameters=[
                        ScenarioItemParameter(
                            key="duration",
                            type="integer",
                            title="Pause Duration",
                            required=True,
                        )
                    ],
                ),
                ScenarioItem(
                    name="Terminate the degradation and come back to a steady state",  # noqa E501
                    ref="aws-fis-restore_availability_zone_power_after_interruption",  # noqa E501
                    tags=["aws", "fis"],
                    type="action",
                    background=False,
                    purpose="Restore the Availability-Zone and all services after its interruption",  # noqa E501
                    parameters=[],
                ),
            ]
        ),
        AssistantMessage(
            [
                ScenarioItem(
                    name="Simulate the complete loss of an AWS Availability Zone",  # noqa E501
                    ref="aws-fis-start_availability_zone_power_interruption_scenario",  # noqa E501
                    tags=["aws", "fis"],
                    type="action",
                    background=False,
                    purpose="Shutdown or remove resources in a various set of AWS services (EC2, ASG, subnets...) so that we can simulate a power loss of an AZ",  # noqa E501
                    parameters=[
                        ScenarioItemParameter(
                            key="az",
                            type="string",
                            title="Availability-Zone",
                            required=True,
                            default="us-east-1a",
                        ),
                    ],
                ),
                ScenarioItem(
                    name="Observe our system while disruption takes places",
                    ref="reliably-pauses-pause_execution",
                    tags=["workflow"],
                    type="action",
                    background=False,
                    purpose="We allow time to observe and investigate the system while it is degraded",  # noqa E501
                    parameters=[
                        ScenarioItemParameter(
                            key="duration",
                            type="integer",
                            title="Pause Duration",
                            required=True,
                            default=5,
                        )
                    ],
                ),
                ScenarioItem(
                    name="Terminate the degradation and come back to a steady state",  # noqa E501
                    ref="aws-fis-restore_availability_zone_power_after_interruption",  # noqa E501
                    tags=["aws", "fis"],
                    type="action",
                    background=False,
                    purpose="Restore the Availability-Zone and all services after its interruption",  # noqa E501
                    parameters=[],
                ),
            ]
        ),
        AssistantMessage(
            [
                ScenarioItem(
                    name="Run typical user traffic",
                    ref="reliably-load-run_load_test",
                    tags=["performance"],
                    type="action",
                    background=True,
                    purpose="Load traffic into our application using a typical traffic of an intense peak day",  # noqa E501
                    parameters=[
                        ScenarioItemParameter(
                            key="url",
                            type="string",
                            title="URL under Test",
                            required=True,
                        ),
                        ScenarioItemParameter(
                            key="duration",
                            type="integer",
                            title="Duration of Test",
                            required=True,
                            default=60,
                        ),
                    ],
                ),
                ScenarioItem(
                    name="Let system warm-up",
                    ref="reliably-pauses-pause_execution",
                    tags=["workflow"],
                    type="action",
                    background=False,
                    purpose="Give our system a chance to warm up",
                    parameters=[
                        ScenarioItemParameter(
                            key="duration",
                            type="integer",
                            title="Pause Duration",
                            required=True,
                            default=5,
                        )
                    ],
                ),
                ScenarioItem(
                    name="Start a fault network proxy to inject latency and packet loss",  # noqa E501
                    ref="fault-proxy-run_proxy",
                    tags=["on-premise", "fault", "network"],
                    type="action",
                    background=True,
                    purpose="Inject network faults such as a latency, packet-loss, jittering... and observe the impact",  # noqa E501
                    parameters=[
                        ScenarioItemParameter(
                            key="proxy_args",
                            type="string",
                            title="Proxy CLI Arguments",
                            required=True,
                            default="--duration=60 --with-latency --latency-mean=300",  # noqa E501
                        ),
                    ],
                ),
            ]
        ),
    ]
