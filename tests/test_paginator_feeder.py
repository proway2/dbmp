import unittest
import sqlite3
from settings import (
    CREATE,
    INSERT,
    UPDATE,
    UPDATE_EMPTY,
    SELECT,
    SELECT_EMPTY,
    DELETE,
    DELETE_EMPTY,
)
from paginator import QueryPaginator


class TestSQLitePaginatorFeeder(unittest.TestCase):
    paginator = None

    @classmethod
    def setUpClass(cls):
        cls.conn = sqlite3.connect(":memory:")

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    def setUp(self):
        self.local_conn = sqlite3.connect(":memory:")

    def tearDown(self):
        self.local_conn.close()

    def test_1_create(self):
        """CREATE with forward feeder."""
        paginator = QueryPaginator(
            rows_num=10,
            query=CREATE,
            connection=TestSQLitePaginatorFeeder.conn,
        )
        res = list(paginator.feeder(forward=True))
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0][0][0], "Successfully executed!")

    def test_2_create_forward(self):
        """CREATE forward again"""
        paginator = QueryPaginator(
            rows_num=10, query=CREATE,
            connection=self.local_conn
        )
        _ = list(paginator.feeder(forward=True))
        res = list(paginator.feeder(forward=True))
        self.assertEqual(len(res), 0)

    def test_3_create_backward(self):
        """CREATE backward"""
        paginator = QueryPaginator(
            rows_num=10, query=CREATE, connection=self.local_conn
        )
        _ = list(paginator.feeder(forward=True))
        res = list(paginator.feeder(forward=False))
        self.assertEqual(len(res), 0)

    def test_3_1_create_backward(self):
        """CREATE backward and backward"""
        paginator = QueryPaginator(
            rows_num=10, query=CREATE, connection=self.local_conn
        )
        _ = list(paginator.feeder(forward=False))
        res = list(paginator.feeder(forward=False))
        self.assertEqual(len(res), 0)

    def test_4_insert(self):
        """INSERT with forward feeder"""
        paginator = QueryPaginator(
            rows_num=10,
            query=INSERT,
            connection=TestSQLitePaginatorFeeder.conn,
        )
        res = list(paginator.feeder(forward=True))
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0][0][0], "Affected rows: 25")

    def test_5_insert_forward(self):
        """INSERT forward again"""
        self.local_conn.execute(CREATE)
        self.local_conn.commit()
        paginator = QueryPaginator(
            rows_num=10, query=INSERT, connection=self.local_conn
        )
        _ = list(paginator.feeder(forward=True))
        res = list(paginator.feeder(forward=True))
        self.assertEqual(len(res), 0)

    def test_6_insert_backward(self):
        """INSERT backward"""
        self.local_conn.execute(CREATE)
        self.local_conn.commit()
        paginator = QueryPaginator(
            rows_num=10, query=INSERT, connection=self.local_conn
        )
        _ = list(paginator.feeder(forward=True))
        res = list(paginator.feeder(forward=False))
        self.assertEqual(len(res), 0)

    def test_7_select(self):
        """SELECT simple"""
        paginator = QueryPaginator(
            rows_num=10,
            query=SELECT,
            connection=TestSQLitePaginatorFeeder.conn,
        )
        res = list(paginator.feeder(forward=True))
        self.assertEqual(len(res), 10)
        vals = sorted((i[0][1] for i in res))
        self.assertEqual(vals, list(range(1, 11)))

    def test_8_select(self):
        paginator = QueryPaginator(
            rows_num=10,
            query=SELECT,
            connection=TestSQLitePaginatorFeeder.conn,
        )
        _ = list(paginator.feeder(forward=True))
        res = list(paginator.feeder(forward=True))
        self.assertEqual(len(res), 10)
        vals = sorted((i[0][1] for i in res))
        self.assertEqual(vals, list(range(11, 21)))


if __name__ == "__main__":
    unittest.main()
