import os
import tempfile
import unittest
from unittest.mock import patch

from calculator.history import HistoryStore


class HistoryStoreTests(unittest.TestCase):
    def test_saves_and_loads_calculations(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with patch.dict(os.environ, {"APPDATA": directory}):
                store = HistoryStore()
                entries = [{"expression": "2 + 2", "result": "4"}]

                store.save(entries)

                self.assertEqual(store.load(), entries)


if __name__ == "__main__":
    unittest.main()
