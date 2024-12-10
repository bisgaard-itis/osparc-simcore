from datetime import datetime
from decimal import Decimal

from models_library.licensed_items import LicensedItemID
from models_library.products import ProductName
from models_library.resource_tracker import PricingUnitCostId
from models_library.resource_tracker_licensed_items_purchases import (
    LicensedItemPurchaseID,
)
from models_library.users import UserID
from models_library.wallets import WalletID
from pydantic import BaseModel, ConfigDict, PositiveInt


class LicensedItemPurchaseGet(BaseModel):
    licensed_item_purchase_id: LicensedItemPurchaseID
    product_name: ProductName
    licensed_item_id: LicensedItemID
    wallet_id: WalletID | None
    wallet_name: str | None
    pricing_unit_cost_id: PricingUnitCostId
    pricing_unit_cost: Decimal
    start_at: datetime
    expire_at: datetime
    num_of_seats: int
    purchased_by_user: UserID
    purchased_at: datetime
    modified: datetime

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "licensed_item_purchase_id": 1,
                    "product_name": "osparc",
                    "licensed_item_id": "Special Pricing Plan for Sleeper",
                    "wallet_id": 1,
                    "wallet_name": "My Wallet",
                    "pricing_unit_cost_id": 1,
                    "pricing_unit_cost": Decimal(10),
                    "start_at": "2023-01-11 13:11:47.293595",
                    "expire_at": "2023-01-11 13:11:47.293595",
                    "num_of_seats": 1,
                    "purchased_by_user": 1,
                    "purchased_at": "2023-01-11 13:11:47.293595",
                    "modified": "2023-01-11 13:11:47.293595",
                }  # type: ignore[index,union-attr]
            ]
        }
    )


class LicensedItemsPurchasesPage(NamedTuple):
    items: list[LicensedItemPurchaseGet]
    total: PositiveInt
