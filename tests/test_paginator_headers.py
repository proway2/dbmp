import unittest
import sqlite3
from paginator import QueryPaginator
from settings import (
    CREATE,
    INSERT,
    UPDATE,
    UPDATE_EMPTY,
    DELETE,
    DELETE_EMPTY,
    SELECT,
    SELECT_EMPTY,
)


class TestSQLitePaginatorHeaders(unittest.TestCase):
    """Testing QueryPaginator.headers()"""

    @classmethod
    def setUpClass(cls):
        cls.conn = sqlite3.connect(":memory:")

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    def test_1_create_table(self):
        """CREATE TABLE headers"""
        paginator = QueryPaginator(
            query=CREATE, connection=TestSQLitePaginatorHeaders.conn
        )
        self.assertEqual(["Result"], paginator.headers())

    def test_2_insert_into(self):
        """INSERT INTO headers"""
        paginator = QueryPaginator(
            query=INSERT, connection=TestSQLitePaginatorHeaders.conn
        )
        self.assertEqual(["Result"], paginator.headers())

    def test_3_update(self):
        """UPDATE existing row"""
        paginator = QueryPaginator(
            query=UPDATE, connection=TestSQLitePaginatorHeaders.conn
        )
        self.assertEqual(["Result"], paginator.headers())

    def test_4_update(self):
        """UPDATE NON existing row"""
        paginator = QueryPaginator(
            query=UPDATE_EMPTY, connection=TestSQLitePaginatorHeaders.conn
        )
        self.assertEqual(["Result"], paginator.headers())

    def test_5_delete(self):
        """DELETE existing row"""
        paginator = QueryPaginator(
            query=DELETE, connection=TestSQLitePaginatorHeaders.conn
        )
        self.assertEqual(["Result"], paginator.headers())

    def test_5_delete_nonexisting(self):
        """DELETE NON existing row"""
        paginator = QueryPaginator(
            query=DELETE_EMPTY, connection=TestSQLitePaginatorHeaders.conn
        )
        self.assertEqual(["Result"], paginator.headers())

    def test_6_select(self):
        """SELECT existing row"""
        paginator = QueryPaginator(
            query=SELECT, connection=TestSQLitePaginatorHeaders.conn
        )
        self.assertEqual(["a", "b"], paginator.headers())

    def test_7_select_nonexisting(self):
        """SELECT NON existing row"""
        paginator = QueryPaginator(
            query=SELECT_EMPTY, connection=TestSQLitePaginatorHeaders.conn
        )
        self.assertEqual(["a", "b"], paginator.headers())


if __name__ == "__main__":
    unittest.main()
