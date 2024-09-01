from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class OrderLine:
    orderid: str  # 定單id
    sku: str  # 商品名稱
    qty: int  # 數量


class Batch:
    def __init__(self, ref: str, sku: str, qty: int, eta: Optional[date] = None):
        self._ref = ref
        self._sku = sku
        self._available_quantity = qty
        self._eta = eta

    def allocate(self, line: OrderLine):
        self._available_quantity -= line.qty

    def can_allocate(self, line: OrderLine):
        return self._sku == line.sku and self._available_quantity >= line.qty

    @property
    def available_quantity(self):
        return self._available_quantity
