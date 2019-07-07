import unittest
import sqlite3
from paginator import QueryPaginator


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
        query = "CREATE TABLE t1(a, b PRIMARY KEY);"
        paginator = QueryPaginator(
            query=query, connection=TestSQLitePaginatorHeaders.conn
        )
        self.assertEqual(["Result"], paginator.headers())

    def test_2_insert_into(self):
        """INSERT INTO headers"""
        query = (
            "insert into t1 (a, b) values "
            "('a', 1),('b', 2),('ccc', 3),('ddd', 4),('eee', 5),(NULL, 6),"
            "('g', 7), ('h', 8), ('j', 9), ('k', 10), ('l', 11), ('m', 12),"
            "('n', 13), ('o', 14), ('p', 15), ('q', 16), ('r', 17), ('s', 18),"
            "('t', 19), ('u', 20), ('v', 21), ('w', 22), ('x', 23),"
            "('y', 24), ('z', 25);"
        )
        paginator = QueryPaginator(
            query=query, connection=TestSQLitePaginatorHeaders.conn
        )
        self.assertEqual(["Result"], paginator.headers())

    def test_3_update(self):
        """UPDATE existing row"""
        query = "update t1 set a = 'sss' where b = 2 or b = 3"
        paginator = QueryPaginator(
            query=query, connection=TestSQLitePaginatorHeaders.conn
        )
        self.assertEqual(["Result"], paginator.headers())

    def test_4_update(self):
        """UPDATE NON existing row"""
        query = "update t1 set a = 'zzz' where b > 100"
        paginator = QueryPaginator(
            query=query, connection=TestSQLitePaginatorHeaders.conn
        )
        self.assertEqual(["Result"], paginator.headers())

    def test_5_delete(self):
        """DELETE existing row"""
        query = "delete from t1 where b = 4 or b = 5"
        paginator = QueryPaginator(
            query=query, connection=TestSQLitePaginatorHeaders.conn
        )
        self.assertEqual(["Result"], paginator.headers())

    def test_5_delete_nonexisting(self):
        """DELETE NON existing row"""
        query = "delete from t1 where b > 100"
        paginator = QueryPaginator(
            query=query, connection=TestSQLitePaginatorHeaders.conn
        )
        self.assertEqual(["Result"], paginator.headers())

    def test_6_select(self):
        """SELECT existing row"""
        query = "select * from t1;"
        paginator = QueryPaginator(
            query=query, connection=TestSQLitePaginatorHeaders.conn
        )
        self.assertEqual(["a", "b"], paginator.headers())

    def test_7_select_nonexisting(self):
        """SELECT NON existing row"""
        query = "select * from t1 where b > 100"
        paginator = QueryPaginator(
            query=query, connection=TestSQLitePaginatorHeaders.conn
        )
        self.assertEqual(["a", "b"], paginator.headers())


if __name__ == "__main__":
    unittest.main()
