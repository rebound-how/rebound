from enum import Enum
from http import HTTPStatus
from typing import Annotated, Literal, Optional

import msgspec
from msgspec import Struct, Meta

PositiveInteger = Annotated[int, Meta(ge=0)]
PositiveFloat = Annotated[float, Meta(ge=0.0)]
Probability = Annotated[float, Meta(ge=0.0, le=1.0)]


StreamSide = Literal["client", "server"]
Direction = Literal["ingress", "egress"]
BandwidthUnit = Literal["bps", "kbps", "mbps", "gbps"]


class Latency(Struct):
    distribution: str | None
    global_: bool | None
    side: StreamSide | None
    mean: PositiveFloat | None
    stddev: PositiveFloat | None
    min: PositiveFloat | None
    max: PositiveFloat | None
    shape: PositiveFloat | None
    scale: PositiveFloat | None
    direction: Direction | None


class PacketLoss(Struct):
    direction: Direction
    side: StreamSide | None


class Bandwidth(Struct):
    rate: PositiveInteger = 1000
    unit: BandwidthUnit = "bps"
    direction: Direction = "server"
    side: StreamSide | None = "server"


class Jitter(Struct):
    side: StreamSide | None
    amplitude: PositiveFloat = 20.0
    frequency: PositiveFloat = 5.0


class Dns(Struct):
    rate: Probability = 0.5


class HttpError(Struct):
    body: str | None
    status_code: HTTPStatus = HTTPStatus.INTERNAL_SERVER_ERROR
    probability: Probability = 1.0


class FaultConfiguration(Struct):
    Latency: Latency
    PacketLoss: PacketLoss
    Bandwidth: Bandwidth
    Jitter: Jitter
    Dns: Dns
    HttpError: HttpError


class ScenarioItemCall(Struct):
    method: str
    url: str
    headers: dict[str, str] | None
    body: str | None


class ScenarioItemCallStrategyMode(Enum):
    Repeat = 1


class ScenarioItemCallStrategy(Struct):
    mode: ScenarioItemCallStrategyMode | None
    failfast: bool | None
    step: PositiveFloat
    wait: PositiveFloat | None
    add_baseline_call: bool | None
    count: PositiveInteger = 0


class ScenarioItemContext(Struct):
    upstreams: list[str]
    faults: list[FaultConfiguration]
    strategy: ScenarioItemCallStrategy | None


class ScenarioItemExpectation(Struct):
    status: PositiveInteger | None
    response_time_under: PositiveFloat | None


class ScenarioItem(Struct):
    call: ScenarioItemCall
    context: ScenarioItemContext
    expect: ScenarioItemExpectation | None


class Scenario(Struct):
    title: str
    description: str | None
    scenarios: list[ScenarioItem]


def generate() -> str:
    schema = msgspec.json.schema(Scenario)
    return msgspec.json.format(
        msgspec.json.encode(schema), indent=2).decode("utf-8")


if __name__ == "__main__":
    s = generate()
    print(s)
