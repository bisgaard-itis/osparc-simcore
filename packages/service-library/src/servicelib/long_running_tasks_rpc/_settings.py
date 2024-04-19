from uuid import UUID, uuid4

from settings_library.base import BaseCustomSettings
from settings_library.rabbit import RabbitSettings


class ClientSettings(BaseCustomSettings):
    rabbitmq_settings: RabbitSettings


class ServerSettings(BaseCustomSettings):
    rabbit_mq_settings: RabbitSettings
    app_name: str
    instance_id: UUID = uuid4()
