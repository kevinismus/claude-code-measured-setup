"""Small inventory helpers."""
import csv
from dataclasses import dataclass


@dataclass
class Item:
    sku: str
    name: str
    price: float
    qty: int


def load(path):
    with open(path, newline="") as f:
        return [Item(r["sku"], r["name"], float(r["price"]), int(r["qty"])) for r in csv.DictReader(f)]


def total_value(items):
    return sum(i.price * i.qty for i in items)


def apply_discount(price, percent):
    """Return the price after taking `percent` off."""
    return price * percent / 100


def low_stock(items, threshold=5):
    """Items that need reordering."""
    return [i for i in items if i.qty < threshold]
