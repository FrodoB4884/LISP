from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

@dataclass
class Customer:
    name: str
    email: str
    address: str
    id: int | None = None

    def to_dict(self):
        return {
            "name": self.name,
            "email": self.email,
            "address": self.address,
            "id": self.id
        }
    
@dataclass
class ItemType:
    name: str
    part_no: str
    item_group: str
    cost: float
    id: int | None = None

    def to_dict(self):
        return {
            "name": self.name,
            "part_no": self.part_no,
            "item_group": self.item_group,
            "cost": self.cost,
            "id": self.id
        }

@dataclass
class Location:
    name: str
    address: str
    id: int | None = None

    def to_dict(self):
        return {
            "name": self.name,
            "address": self.address,
            "id": self.id
        }

@dataclass
class Stock:
    item_type: ItemType
    location: Location
    in_stock: int
    reserved: int
    reorder_point: int
    id: int | None = None

    def to_dict(self):
        return {
            "item_type": self.item_type.to_dict(),
            "location": self.location.to_dict(),
            "in_stock": self.in_stock,
            "reserved": self.reserved,
            "reorder_point": self.reorder_point,
            "available": self.available,
            "id": self.id
        }

    @property
    def available(self) -> int:
        return self.in_stock - self.reserved

@dataclass
class Order:
    customer: Customer
    items: dict[ItemType, int]  # item_type_id , quantity
    status: OrderStatus
    change_log: list[tuple[datetime, OrderStatus, str]]
    id: int | None = None

    def change_log_dict(self):
        return [
            {
                "timestamp": ts.isoformat(),
                "status": status.value,
                "comment": comment
            }
            for ts, status, comment in self.change_log
        ]

    def to_dict(self):
        return {
            "customer": self.customer.to_dict(),
            "items": {item.to_dict():self.items[item] for item in self.items},
            "status": self.status.value,
            "change_log": self.change_log_dict(),
            "id": self.id
        }

class OrderStatus(Enum):
    PENDING = "Pending" # still in basket, not confirmed, basically just an idea
    CONFIRMED = "Confirmed" # ordered and therefore needs invoice
    PAID = "Paid" # invoice paid and therefore requires shipping
    SHIPPED = "Shipped" # shipped and everything is all good
    CANCELLED = "Cancelled" # the client has cancelled the order, only possible before shipped stage
    FAILED = "Failed" # an issue has occured, this always requires explanation in order history
    UNKNOWN = "Unknown" # used if the status retrieved from the db is invalid
