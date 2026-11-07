import unittest
from inventory import Item, restock


class RestockHidden(unittest.TestCase):
    def test_increases_qty(self):
        items = [Item("A1", "Bolt", 0.5, 1), Item("B2", "Nut", 0.2, 3)]
        restock(items, "B2", 4)
        self.assertEqual(items[1].qty, 7)
        self.assertEqual(items[0].qty, 1)

    def test_unknown_sku(self):
        with self.assertRaises(KeyError):
            restock([Item("A1", "Bolt", 0.5, 1)], "ZZ", 1)


if __name__ == "__main__":
    unittest.main()
