from ._models import ServiceName
from ._settings import ClientSettings


class LongRunningTaskRpcClient:
    def __init__(self, service_name: ServiceName) -> None:
        self._settings = ClientSettings.create_from_envs()
        self._service_name = service_name
