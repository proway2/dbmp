import sqlite3
import unittest

from paginator import QueryPaginator
from settings import CREATE, DELETE, INSERT, SELECT, UPDATE


class TestSQLitePaginatorIsDataQuery(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.conn = sqlite3.connect(":memory:")

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    def test_1_create(self):
        """CREATE"""
        paginator = QueryPaginator(
            query=CREATE, connection=TestSQLitePaginatorIsDataQuery.conn
        )
        self.assertEqual(False, paginator.is_data_query)

    def test_2_insert(self):
        """INSERT"""
        paginator = QueryPaginator(
            query=INSERT, connection=TestSQLitePaginatorIsDataQuery.conn
        )
        self.assertEqual(False, paginator.is_data_query)

    def test_3_update(self):
        """UPDATE"""
        paginator = QueryPaginator(
            query=UPDATE, connection=TestSQLitePaginatorIsDataQuery.conn
        )
        self.assertEqual(False, paginator.is_data_query)

    def test_4_delete(self):
        """DELETE"""
        paginator = QueryPaginator(
            query=DELETE, connection=TestSQLitePaginatorIsDataQuery.conn
        )
        self.assertEqual(False, paginator.is_data_query)

    def test_5_select(self):
        """SELECT"""
        paginator = QueryPaginator(
            query=SELECT, connection=TestSQLitePaginatorIsDataQuery.conn
        )
        self.assertEqual(True, paginator.is_data_query)


if __name__ == "__main__":
    unittest.main()
