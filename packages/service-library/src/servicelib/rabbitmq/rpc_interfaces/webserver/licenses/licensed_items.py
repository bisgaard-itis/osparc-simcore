import logging

from models_library.api_schemas_webserver import WEBSERVER_RPC_NAMESPACE
from models_library.api_schemas_webserver.licensed_items import (
    LicensedItemGet,
    LicensedItemGetPage,
)
from models_library.api_schemas_webserver.licensed_items_checkouts import (
    LicensedItemCheckoutGet,
)
from models_library.licensed_items import LicensedItemID
from models_library.products import ProductName
from models_library.rabbitmq_basic_types import RPCMethodName
from models_library.resource_tracker import ServiceRunId
from models_library.resource_tracker_licensed_items_checkouts import (
    LicensedItemCheckoutID,
)
from models_library.users import UserID
from models_library.wallets import WalletID
from pydantic import TypeAdapter
from servicelib.logging_utils import log_decorator
from servicelib.rabbitmq import RabbitMQRPCClient

_logger = logging.getLogger(__name__)


@log_decorator(_logger, level=logging.DEBUG)
async def get_licensed_items(
    rabbitmq_rpc_client: RabbitMQRPCClient,
    *,
    product_name: str,
    offset: int = 0,
    limit: int = 20,
) -> LicensedItemGetPage:
    result: LicensedItemGetPage = await rabbitmq_rpc_client.request(
        WEBSERVER_RPC_NAMESPACE,
        TypeAdapter(RPCMethodName).validate_python("get_licensed_items"),
        product_name=product_name,
        offset=offset,
        limit=limit,
    )
    assert isinstance(result, LicensedItemGetPage)  # nosec
    return result


@log_decorator(_logger, level=logging.DEBUG)
async def get_available_licensed_items_for_wallet(
    rabbitmq_rpc_client: RabbitMQRPCClient,
    *,
    product_name: ProductName,
    wallet_id: WalletID,
    user_id: UserID,
    offset: int = 0,
    limit: int = 20,
) -> LicensedItemGetPage:
    result: LicensedItemGet = await rabbitmq_rpc_client.request(
        WEBSERVER_RPC_NAMESPACE,
        TypeAdapter(RPCMethodName).validate_python(
            "get_available_licensed_items_for_wallet"
        ),
        product_name=product_name,
        user_id=user_id,
        wallet_id=wallet_id,
        offset=offset,
        limit=limit,
    )
    assert isinstance(result, LicensedItemGetPage)  # nosec
    return result


@log_decorator(_logger, level=logging.DEBUG)
async def checkout_licensed_item_for_wallet(
    rabbitmq_rpc_client: RabbitMQRPCClient,
    *,
    product_name: ProductName,
    user_id: UserID,
    wallet_id: WalletID,
    licensed_item_id: LicensedItemID,
    num_of_seats: int,
    service_run_id: ServiceRunId,
) -> LicensedItemCheckoutGet:
    result = await rabbitmq_rpc_client.request(
        WEBSERVER_RPC_NAMESPACE,
        TypeAdapter(RPCMethodName).validate_python("checkout_licensed_item_for_wallet"),
        product_name=product_name,
        user_id=user_id,
        wallet_id=wallet_id,
        licensed_item_id=licensed_item_id,
        num_of_seats=num_of_seats,
        service_run_id=service_run_id,
    )
    assert isinstance(result, LicensedItemCheckoutGet)  # nosec
    return result


@log_decorator(_logger, level=logging.DEBUG)
async def release_licensed_item_for_wallet(
    rabbitmq_rpc_client: RabbitMQRPCClient,
    *,
    product_name: ProductName,
    user_id: UserID,
    licensed_item_checkout_id: LicensedItemCheckoutID,
) -> LicensedItemCheckoutGet:
    result = await rabbitmq_rpc_client.request(
        WEBSERVER_RPC_NAMESPACE,
        TypeAdapter(RPCMethodName).validate_python("release_licensed_item_for_wallet"),
        product_name=product_name,
        user_id=user_id,
        licensed_item_checkout_id=licensed_item_checkout_id,
    )
    assert isinstance(result, LicensedItemCheckoutGet)  # nosec
    return result