from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class OrderLine:
    orderid: str  # 定單id
    sku: str  # 商品名稱
    qty: int  # 數量

    def __hash__(self):
        return hash(self.orderid)


class Batch:
    def __init__(self, ref: str, sku: str, qty: int, eta: Optional[date] = None):
        """
        一個Batch代表 單一商品的一批庫存
        """
        self._ref = ref
        self._sku = sku
        self._purchased_quantity = qty
        self._eta = eta
        self._allocations = set()

    def allocate(self, line: OrderLine):
        if self.can_allocate(line):
            self._allocations.add(line)

    def deallocate(self, line: OrderLine):
        if line in self._allocations:
            self._allocations.remove(line)

    def can_allocate(self, line: OrderLine):
        # 先檢查sku是否相同，再檢查可用量是否足夠
        return self._sku == line.sku and self.available_quantity >= line.qty

    def __eq__(self, other):
        if not isinstance(other, Batch):
            return False
        return other._ref == self._ref

    def __hash__(self):
        return hash(self._ref)

    @property
    def available_quantity(self):
        # 可用量 = 購買量 - 已分配量
        return self._purchased_quantity - self.allocated_quantity

    @property
    def allocated_quantity(self):
        # 已分配量 = 分配給OrderLine的數量總和
        return sum(line.qty for line in self._allocations)
