from enum import Enum
from http import HTTPStatus
from typing import Annotated, Literal

import msgspec
from msgspec import Struct, Meta

PositiveInteger = Annotated[int, Meta(ge=0)]
PositiveFloat = Annotated[float, Meta(ge=0.0)]
Probability = Annotated[float, Meta(ge=0.0, le=1.0)]


StreamSide = Literal["client", "server"]
Direction = Literal["ingress", "egress"]
BandwidthUnit = Literal["bps", "kbps", "mbps", "gbps"]
SchedPattern = r"(?:start:\s*(\d+s|\d+m|\d+%)(?:,)?;?)*(?:duration:\s*(\d+s|\d+m|\d+%)(?:,)?;?)*"


class Latency(Struct):
    distribution: str | None
    global_: bool | None
    mean: PositiveFloat | None
    stddev: PositiveFloat | None
    min: PositiveFloat | None
    max: PositiveFloat | None
    shape: PositiveFloat | None
    scale: PositiveFloat | None
    side: StreamSide | None = "server"
    direction: Direction | None = "ingress"
    sched: Annotated[str, msgspec.Meta(pattern=SchedPattern)] | None = None


class PacketLoss(Struct):
    side: StreamSide | None = "server"
    direction: Direction | None = "ingress"
    sched: Annotated[str, msgspec.Meta(pattern=SchedPattern)] | None = None


class Bandwidth(Struct):
    rate: PositiveInteger = 1000
    unit: BandwidthUnit = "bps"
    side: StreamSide | None = "server"
    direction: Direction | None = "ingress"
    sched: Annotated[str, msgspec.Meta(pattern=SchedPattern)] | None = None


class Jitter(Struct):
    amplitude: PositiveFloat = 20.0
    frequency: PositiveFloat = 5.0
    side: StreamSide | None = "server"
    direction: Direction | None = "ingress"
    sched: Annotated[str, msgspec.Meta(pattern=SchedPattern)] | None = None


class Blackhole(Struct):
    side: StreamSide | None = "server"
    direction: Direction | None = "ingress"
    sched: Annotated[str, msgspec.Meta(pattern=SchedPattern)] | None = None


class HttpError(Struct):
    body: str | None
    status_code: HTTPStatus = HTTPStatus.INTERNAL_SERVER_ERROR
    probability: Probability = 1.0


class Blackhole(Struct):
    direction: Direction = "egress"
    side: StreamSide | None = "server"


class FaultConfiguration(Struct):
    Latency: Latency
    PacketLoss: PacketLoss
    Bandwidth: Bandwidth
    Jitter: Jitter
    Blackhole: Blackhole
    HttpError: HttpError


class ScenarioItemCallOpenAPIMeta(Struct):
    operation_id: str | None = None


class ScenarioItemCall(Struct):
    method: str
    url: str
    headers: dict[str, str] | None
    body: str | None
    timeout: float | None = None
    meta: ScenarioItemCallOpenAPIMeta | None = None


class ScenarioRepeatItemCallStrategy(Struct, tag=True):
    mode: Literal["repeat"]
    step: PositiveFloat
    failfast: bool | None
    wait: PositiveFloat | None
    add_baseline_call: bool | None
    count: PositiveInteger = 0


class ScenarioLoadItemCallStrategy(Struct, tag=True):
    mode: Literal["load"]
    duration: str
    clients: PositiveInteger
    rps: PositiveInteger


class ScenarioItemSLO(Struct):
    type: str
    title: str
    objective: float
    threshold: float


class ScenarioItemContext(Struct):
    upstreams: list[str]
    faults: list[FaultConfiguration]
    strategy: ScenarioRepeatItemCallStrategy | ScenarioLoadItemCallStrategy | None
    slo: list[ScenarioItemSLO] | None = None


class ScenarioItemExpectation(Struct):
    status: PositiveInteger | None
    response_time_under: PositiveFloat | None


class ScenarioItem(Struct):
    call: ScenarioItemCall
    context: ScenarioItemContext
    expect: ScenarioItemExpectation | None = None


class HTTPPathsConfig(Struct):
    segments: dict[str, str]


class ScenarioHTTPGlobalConfig(Struct):
    headers: dict[str, str]
    paths: HTTPPathsConfig | None = None


class ScenarioGlobalConfig(Struct):
    http: ScenarioHTTPGlobalConfig | None = None


class Scenario(Struct):
    title: str
    description: str | None
    scenarios: list[ScenarioItem]
    config: ScenarioGlobalConfig | None = None


def generate() -> str:
    schema = msgspec.json.schema(Scenario)
    return msgspec.json.format(
        msgspec.json.encode(schema), indent=2).decode("utf-8")


if __name__ == "__main__":
    s = generate()
    print(s)
