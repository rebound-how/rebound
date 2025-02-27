__all__ = ["PlanFailedError"]


class PlanFailedError(Exception):
    def __init__(self, plan_id: str, message: str) -> None:
        self.plan_id = plan_id
        self.message = message
