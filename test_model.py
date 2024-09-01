from datetime import date, timedelta
import pytest

from model import Batch, OrderLine, allocate, OutOfStock

today = date.today()
tomorrow = today + timedelta(days=1)
later = tomorrow + timedelta(days=10)


def test_allocating_to_a_batch_reduces_the_available_quantity():
    batch = Batch("batch-001", "hat", qty=20, eta=today)
    line = OrderLine("order-ref", "hat", 3)
    batch.allocate(line)
    assert batch.available_quantity == 17


def test_can_allocate_if_available_greater_than_required():
    batch, line = _make_batch_and_line("apple", 20, 2)
    assert batch.can_allocate(line) is True


def test_cannot_allocate_if_available_smaller_than_required():
    batch, line = _make_batch_and_line("apple", 2, 20)
    assert batch.can_allocate(line) is False


def test_can_allocate_if_available_equal_to_required():
    batch, line = _make_batch_and_line("apple", 20, 20)
    assert batch.can_allocate(line) is True


def test_cannot_allocate_if_skus_do_not_match():
    batch = Batch("batch-001", "apple", 100, eta=today)
    line = OrderLine("order-123", "cat", 10)
    assert batch.can_allocate(line) is False

def test_can_only_deallocate_allocated_lines():
    batch, line = _make_batch_and_line("apple", 20, 2)
    batch.deallocate(line)
    assert batch.available_quantity == 20

def test_allocation_is_idempotent():
    batch, line = _make_batch_and_line("apple", 20, 2)
    batch.allocate(line)
    batch.allocate(line)
    assert batch.available_quantity == 18


def test_prefers_current_stock_batches_to_shipments():
    in_stock_batch = Batch("in-stock-batch", "sku", 100, eta=None)
    shipment_batch = Batch("shipment-batch", "sku", 100, eta=tomorrow)
    line = OrderLine("order-123", "sku", 20)

    allocate(line, [in_stock_batch, shipment_batch])
    assert in_stock_batch.available_quantity == 80
    assert shipment_batch.available_quantity == 100


def test_prefers_earlier_batches():
    earliest = Batch("speedy-batch", "sku", 100, eta=today)
    medium = Batch("normal-batch", "sku", 100, eta=tomorrow)
    latest = Batch("slow-batch", "sku", 100, eta=later)
    line = OrderLine("order-123", "sku", 20)

    allocate(line, [medium, earliest, latest])
    assert earliest.available_quantity == 80
    assert medium.available_quantity == 100
    assert latest.available_quantity == 100


def test_returns_allocated_batch_ref():
    in_stock_batch = Batch("in-stock-batch", "sku", 100, eta=None)
    line = OrderLine("order-123", "sku", 20)
    allocation = allocate(line, [in_stock_batch])
    assert allocation == in_stock_batch.reference


def test_raises_out_of_stock_exception_if_cannot_allocate():
    batch = Batch("batch-001", "sku", 10, eta=today)
    allocate(OrderLine("order-001", "sku", 10), [batch])

    with pytest.raises(OutOfStock, match="sku"):
        allocate(OrderLine("order-001", "sku", 10), [batch])


def _make_batch_and_line(sku, batch_qty, line_qty):
    return (
        Batch("batch-001", sku, batch_qty, eta=today),
        OrderLine("order-001", sku, line_qty),
    )
