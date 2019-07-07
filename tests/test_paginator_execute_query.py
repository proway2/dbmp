import unittest
import sqlite3
from paginator import QueryPaginator
from settings import NW_SQLITE, NW_SELECT, NW_SELECT_HUGE, SELECT


class TestSQLitePaginatorExecuteQuery(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(NW_SQLITE)

    def tearDown(self):
        self.conn.close()

    def test_new_query(self):
        """SELECT which is different from the one used during __init__"""
        paginator = QueryPaginator(query=NW_SELECT, connection=self.conn)
        self.assertEqual(
            True, paginator._QueryPaginator__execute_query(NW_SELECT_HUGE)
        )

    def test_wrong_select(self):
        """SELECT from different DB"""
        with self.assertRaises(sqlite3.OperationalError):
            QueryPaginator(query=SELECT, connection=self.conn)


if __name__ == "__main__":
    unittest.main()
