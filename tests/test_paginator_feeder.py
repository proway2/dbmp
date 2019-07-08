import unittest
import sqlite3
from settings import (
    CREATE,
    INSERT,
    # UPDATE,
    # UPDATE_EMPTY,
    SELECT,
    # SELECT_EMPTY,
    # DELETE,
    # DELETE_EMPTY,
)
from paginator import QueryPaginator

# TESTS ORDER MATTERS!


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

    def test_a_create(self):
        """CREATE simple"""
        paginator = QueryPaginator(
            rows_num=10,
            query=CREATE,
            connection=TestSQLitePaginatorFeeder.conn,
        )
        res = list(paginator.feeder(forward=True))
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0][0][0], "Successfully executed!")

    def test_b_create_forward(self):
        """CREATE forward again"""
        paginator = QueryPaginator(
            rows_num=10, query=CREATE,
            connection=self.local_conn
        )
        _ = list(paginator.feeder(forward=True))
        res = list(paginator.feeder(forward=True))
        self.assertEqual(len(res), 0)

    def test_c_create_backward(self):
        """CREATE backward"""
        paginator = QueryPaginator(
            rows_num=10, query=CREATE, connection=self.local_conn
        )
        _ = list(paginator.feeder(forward=True))
        res = list(paginator.feeder(forward=False))
        self.assertEqual(len(res), 0)

    def test_d_create_backward(self):
        """CREATE backward and backward"""
        paginator = QueryPaginator(
            rows_num=10, query=CREATE, connection=self.local_conn
        )
        _ = list(paginator.feeder(forward=False))
        res = list(paginator.feeder(forward=False))
        self.assertEqual(len(res), 0)

    def test_e_insert(self):
        """INSERT simple"""
        paginator = QueryPaginator(
            rows_num=10,
            query=INSERT,
            connection=TestSQLitePaginatorFeeder.conn,
        )
        res = list(paginator.feeder(forward=True))
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0][0][0], "Affected rows: 25")

    def test_f_insert_forward(self):
        """INSERT forward"""
        self.local_conn.execute(CREATE)
        self.local_conn.commit()
        paginator = QueryPaginator(
            rows_num=10, query=INSERT, connection=self.local_conn
        )
        _ = list(paginator.feeder(forward=True))
        res = list(paginator.feeder(forward=True))
        self.assertEqual(len(res), 0)

    def test_g_insert_backward(self):
        """INSERT backward"""
        self.local_conn.execute(CREATE)
        self.local_conn.commit()
        paginator = QueryPaginator(
            rows_num=10, query=INSERT, connection=self.local_conn
        )
        _ = list(paginator.feeder(forward=True))
        res = list(paginator.feeder(forward=False))
        self.assertEqual(len(res), 0)

    def test_h_select(self):
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

    def test_i_select(self):
        """SELECT forward"""
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

    def test_j_select(self):
        """SELECT single page"""
        paginator = QueryPaginator(
            query=SELECT,
            connection=TestSQLitePaginatorFeeder.conn,
        )
        res = list(paginator.feeder(forward=True))
        self.assertEqual(len(res), 25)
        vals = sorted((i[0][1] for i in res))
        self.assertEqual(vals, list(range(1, 26)))

    def test_k_select(self):
        """SELECT single (last) page forward"""
        paginator = QueryPaginator(
            query=SELECT,
            connection=TestSQLitePaginatorFeeder.conn,
        )
        _ = list(paginator.feeder(forward=True))
        res = list(paginator.feeder(forward=True))
        self.assertEqual(len(res), 0)
        vals = sorted((i[0][1] for i in res))
        self.assertEqual(vals, [])

    def test_l_select(self):
        """SELECT single (last) page backward"""
        paginator = QueryPaginator(
            query=SELECT,
            connection=TestSQLitePaginatorFeeder.conn,
        )
        _ = list(paginator.feeder(forward=True))
        res = list(paginator.feeder(forward=False))
        self.assertEqual(len(res), 0)
        vals = sorted((i[0][1] for i in res))
        self.assertEqual(vals, [])

    def test_m_select(self):
        """SELECT second page backward"""

if __name__ == "__main__":
    unittest.main()
