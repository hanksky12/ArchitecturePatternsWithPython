from datetime import date, timedelta
import pytest

from model import Batch, OrderLine

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


def test_prefers_warehouse_batches_to_shipments():
    pytest.fail("todo")


def test_prefers_earlier_batches():
    pytest.fail("todo")



def _make_batch_and_line(sku, batch_qty, line_qty):
    return (
        Batch("batch-001", sku, batch_qty, eta=today),
        OrderLine("order-001", sku, line_qty),
    )