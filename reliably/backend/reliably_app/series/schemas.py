from datetime import date, datetime
from decimal import Decimal
from typing import Annotated, Any, Dict, Iterator, List, Literal, Tuple

from pydantic import UUID4, PlainSerializer, RootModel

from reliably_app.schemas import BaseSchema

__all__ = ["ExecutionBreakdownSeries"]


class ExperimentExecutionsDurationBreakdownItem(BaseSchema):  # noqa
    name: str
    data: List[float | None]
    kind: Literal["action", "probe"]
    loc: Literal["ssh-before", "ssh-after", "ssh-during", "method", "rollback"]
    stack: str | None = None
    status: List[str | None]
    tolerance_met: List[bool | None]


class ExperimentExecutionsDurationCollatedItem(BaseSchema):
    name: str
    data: List[float | None]
    stack: str | None = None


class ExperimentContributionsPerOrg(BaseSchema):
    data: List[int]


class ExecutionBreakdownSeries(BaseSchema):  # noqa
    labels: List[UUID4 | str]
    datasets: List[
        ExperimentExecutionsDurationBreakdownItem
        | ExperimentExecutionsDurationCollatedItem
        | ExperimentContributionsPerOrg
    ]


class ExperimentlExecutionsDistPerOrg(BaseSchema):
    data: Dict[str, Any]


class ExecutionsContributionOrgDistribution(BaseSchema):
    c: Dict[str, str]
    t: str | None = None
    x: List[Tuple[str, datetime]]


class ExecutionsContributionsOrgDistribution(BaseSchema):
    experiments: Dict[UUID4, ExecutionsContributionOrgDistribution]


class OrgExecutionCalendarDay(BaseSchema):
    deviated: int = 0
    failed: int = 0
    completed: int = 0
    interrupted: int = 0
    aborted: int = 0
    total: int = 0


class OrgExecutionCalendar(RootModel):
    root: Dict[str, OrgExecutionCalendarDay]

    def __iter__(self) -> Iterator[str]:  # type: ignore
        return iter(self.root.keys())


class ExperimentScoreTrend(BaseSchema):
    score: float | None = None
    trend: List[tuple[UUID4, str, float]]


class ExecutionMetricsCountPerUser(BaseSchema):
    user_id: UUID4
    username: str
    count: int = 0


class ExecutionMetricsPerUserCurrentWeek(BaseSchema):
    user_id: UUID4
    username: str
    execution_id: UUID4
    started_on: datetime
    status: Literal["interrupted", "aborted", "completed", "failed"] | None = (
        None
    )
    deviated: bool = False
    plan_title: str | None = None
    plan_id: UUID4
    experiment_id: UUID4
    duration: float | None = None


class ExecutionMetricsUserDistribution(BaseSchema):
    total: List[ExecutionMetricsCountPerUser]
    current_week: List[ExecutionMetricsPerUserCurrentWeek]


class ExecutionMetricsPeriodPerDayDistribution(BaseSchema):
    day: date
    count: int = 0


class ExecutionMetricsPeriodPerWeekDistribution(BaseSchema):
    week: date
    count: int = 0


class ExecutionMetricsPeriodPerMonthDistribution(BaseSchema):
    month: date
    count: int = 0


class ExecutionMetricsPeriodDistribution(BaseSchema):
    per_day: List[ExecutionMetricsPeriodPerDayDistribution]
    per_week: List[ExecutionMetricsPeriodPerWeekDistribution]
    per_month: List[ExecutionMetricsPeriodPerMonthDistribution]


class ImpactDistributionPerPlan(BaseSchema):
    plan_id: UUID4
    plan_title: str
    total: int = 0
    deviated: int = 0
    completed: int = 0


class ImpactDistributionPerTag(BaseSchema):
    tag: str
    total: int = 0
    deviated: int = 0
    completed: int = 0


class Impacts(BaseSchema):
    per_plan: List[ImpactDistributionPerPlan]
    per_tag: List[ImpactDistributionPerTag]


class ScorePerExperiment(BaseSchema):
    experiment_id: UUID4
    execution_count: int
    experiment_title: str | None = None
    freshness: int
    score: Annotated[
        Decimal,
        PlainSerializer(
            lambda x: float(x), return_type=float, when_used="json"
        ),
    ]


class ScorePerPlan(BaseSchema):
    plan_id: UUID4
    execution_count: int
    plan_title: str | None = None
    freshness: int
    score: Annotated[
        Decimal,
        PlainSerializer(
            lambda x: float(x), return_type=float, when_used="json"
        ),
    ]


class Scores(BaseSchema):
    per_experiment: List[ScorePerExperiment]
    per_plan: List[ScorePerPlan]


class ContributionsPerExperiment(BaseSchema):
    name: str
    count: int


class ContributionsPerExecution(BaseSchema):
    name: str
    count: int


class Contributions(BaseSchema):
    per_experiment: List[ContributionsPerExperiment]
    per_execution: List[ContributionsPerExecution]


class ExecutionMetricsDistribution(BaseSchema):
    running_count: int
    per_user: ExecutionMetricsUserDistribution
    per_period: ExecutionMetricsPeriodDistribution
    impacts: Impacts
    scores: Scores
    contributions: Contributions


class ExecutionMetrics(BaseSchema):
    distributions: ExecutionMetricsDistribution
