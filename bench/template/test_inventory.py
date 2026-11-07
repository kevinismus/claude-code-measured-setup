import unittest
from inventory import Item, total_value, apply_discount, low_stock


class InventoryTest(unittest.TestCase):
    def setUp(self):
        self.items = [Item("A1", "Bolt", 0.5, 100), Item("B2", "Nut", 0.2, 3), Item("C3", "Gear", 12.0, 5)]

    def test_total_value(self):
        self.assertAlmostEqual(total_value(self.items), 50 + 0.6 + 60)

    def test_apply_discount(self):
        self.assertAlmostEqual(apply_discount(100, 10), 90)

    def test_low_stock(self):
        self.assertEqual([i.sku for i in low_stock(self.items)], ["B2"])


if __name__ == "__main__":
    unittest.main()
