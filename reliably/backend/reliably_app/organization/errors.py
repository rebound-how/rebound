__all__ = ["OrgAlreadyExistError"]


class OrgAlreadyExistError(Exception):
    pass


class CloudOrganizationCreationError(Exception):
    def __init__(self, org_id: str, message: str) -> None:
        self.org_id = org_id
        self.message = message


class CloudOrganizationDeletionError(Exception):
    def __init__(self, org_id: str, message: str) -> None:
        self.org_id = org_id
        self.message = message
