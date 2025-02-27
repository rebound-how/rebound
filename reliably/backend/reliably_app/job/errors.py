__all__ = ["JobError"]


class JobError(Exception):
    def __init__(self, job_id: str, message: str) -> None:
        self.job_id = job_id
        self.message = message
