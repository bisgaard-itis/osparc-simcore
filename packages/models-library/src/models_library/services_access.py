"""Service access rights models

"""


from pydantic import BaseModel, Field

from .users import GroupID


class ServiceGroupAccessRights(BaseModel):
    execute_access: bool = Field(
        default=False,
        description="defines whether the group can execute the service",
    )
    write_access: bool = Field(
        default=False, description="defines whether the group can modify the service"
    )


class ServiceAccessRights(BaseModel):
    access_rights: dict[GroupID, ServiceGroupAccessRights] | None = Field(
        None,
        alias="accessRights",
        description="service access rights per group id",
    )
