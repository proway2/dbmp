import unittest
import sqlite3
from settings import CREATE, INSERT, SELECT
from paginator import QueryPaginator

# TESTS ORDER MATTERS!


class TestSQLitePaginatorFeeder(unittest.TestCase):

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

    def test_a_create_simple(self):
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
            rows_num=10, query=CREATE, connection=self.local_conn
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

    def test_d_create_backward_backward(self):
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

    def test_i_select_forward(self):
        """SELECT page 1 and page 2"""
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

    def test_j_select_single_page(self):
        """SELECT single page"""
        paginator = QueryPaginator(
            query=SELECT, connection=TestSQLitePaginatorFeeder.conn
        )
        res = list(paginator.feeder(forward=True))
        self.assertEqual(len(res), 25)
        vals = sorted((i[0][1] for i in res))
        self.assertEqual(vals, list(range(1, 26)))

    def test_k_select_single_page_forward(self):
        """SELECT single (last) page forward"""
        paginator = QueryPaginator(
            query=SELECT, connection=TestSQLitePaginatorFeeder.conn
        )
        _ = list(paginator.feeder(forward=True))
        res = list(paginator.feeder(forward=True))
        self.assertEqual(len(res), 0)
        vals = sorted((i[0][1] for i in res))
        self.assertEqual(vals, [])

    def test_l_select_single_page_backward(self):
        """SELECT single (last) page backward"""
        paginator = QueryPaginator(
            query=SELECT, connection=TestSQLitePaginatorFeeder.conn
        )
        _ = list(paginator.feeder(forward=True))
        res = list(paginator.feeder(forward=False))
        self.assertEqual(len(res), 0)
        vals = sorted((i[0][1] for i in res))
        self.assertEqual(vals, [])

    def test_m_select_forward_backward(self):
        """SELECT second page backward"""
        paginator = QueryPaginator(
            rows_num=10,
            query=SELECT,
            connection=TestSQLitePaginatorFeeder.conn,
        )
        _ = list(paginator.feeder(forward=True))
        _ = list(paginator.feeder(forward=True))
        res = list(paginator.feeder(forward=False))
        self.assertEqual(len(res), 10)
        vals = sorted((i[0][1] for i in res))
        self.assertEqual(vals, list(range(1, 11)))

    def test_n_select_first_page_backward(self):
        """SELECT first (multi) page backward"""
        paginator = QueryPaginator(
            rows_num=10,
            query=SELECT,
            connection=TestSQLitePaginatorFeeder.conn,
        )
        _ = list(paginator.feeder(forward=True))
        res = list(paginator.feeder(forward=False))
        self.assertEqual(len(res), 0)
        vals = sorted((i[0][1] for i in res))
        self.assertEqual(vals, [])

    def test_o_select_last_page_forward(self):
        """SELECT last (multi) page forward"""
        paginator = QueryPaginator(
            rows_num=10,
            query=SELECT,
            connection=TestSQLitePaginatorFeeder.conn,
        )
        for _ in range(3):
            _ = list(paginator.feeder(forward=True))
        res = list(paginator.feeder(forward=True))
        self.assertEqual(len(res), 0)
        vals = sorted((i[0][1] for i in res))
        self.assertEqual(vals, [])

    def test_p_select_3fwd_1bwd(self):
        """SELECT 3 page forward and 1 backward"""
        paginator = QueryPaginator(
            rows_num=7, query=SELECT, connection=TestSQLitePaginatorFeeder.conn
        )
        for _ in range(3):
            _ = list(paginator.feeder(forward=True))
        res = list(paginator.feeder(forward=False))
        self.assertEqual(len(res), 7)
        vals = sorted((i[0][1] for i in res))
        self.assertEqual(vals, list(range(8, 15)))

    def test_q_select_4fwd(self):
        """SELECT 3 page forward and 1 forward up to the end"""
        paginator = QueryPaginator(
            rows_num=7, query=SELECT, connection=TestSQLitePaginatorFeeder.conn
        )
        for _ in range(3):
            _ = list(paginator.feeder(forward=True))
        res = list(paginator.feeder(forward=True))
        self.assertEqual(len(res), 4)
        vals = sorted((i[0][1] for i in res))
        self.assertEqual(vals, list(range(22, 26)))

    def test_r_select_6fwd_1bwd(self):
        """SELECT 6 page forward and 3 backward"""
        paginator = QueryPaginator(
            rows_num=7, query=SELECT, connection=TestSQLitePaginatorFeeder.conn
        )
        for _ in range(6):
            _ = list(paginator.feeder(forward=True))
        res = list(paginator.feeder(forward=False))
        self.assertEqual(len(res), 7)
        vals = sorted((i[0][1] for i in res))
        self.assertEqual(vals, list(range(15, 22)))

    def test_s_select_6fwd(self):
        """SELECT 6 forward beyond the end"""
        paginator = QueryPaginator(
            rows_num=7, query=SELECT, connection=TestSQLitePaginatorFeeder.conn
        )
        for _ in range(6):
            res = list(paginator.feeder(forward=True))
        self.assertEqual(len(res), 0)
        vals = sorted((i[0][1] for i in res))
        self.assertEqual(vals, [])

    def test_t_select_6bwd(self):
        """SELECT backward beyond the end"""
        paginator = QueryPaginator(
            rows_num=7, query=SELECT, connection=TestSQLitePaginatorFeeder.conn
        )
        for _ in range(4):
            res = list(paginator.feeder(forward=True))
        for _ in range(6):
            res = list(paginator.feeder(forward=False))
        self.assertEqual(len(res), 0)
        vals = sorted((i[0][1] for i in res))
        self.assertEqual(vals, [])

    def test_u_select_6bwd_2fwd(self):
        """SELECT backward beyond the end"""
        paginator = QueryPaginator(
            rows_num=7, query=SELECT, connection=TestSQLitePaginatorFeeder.conn
        )
        for _ in range(4):
            res = list(paginator.feeder(forward=True))
        for _ in range(6):
            res = list(paginator.feeder(forward=False))
        for _ in range(2):
            res = list(paginator.feeder(forward=True))
        self.assertEqual(len(res), 7)
        vals = sorted((i[0][1] for i in res))
        self.assertEqual(vals, list(range(15, 22)))

    def test_u_select_6fwd_3bwd(self):
        """SELECT 6 forward and 3 backward"""
        paginator = QueryPaginator(
            rows_num=7, query=SELECT, connection=TestSQLitePaginatorFeeder.conn
        )
        for _ in range(6):
            res = list(paginator.feeder(forward=True))
        for _ in range(3):
            res = list(paginator.feeder(forward=False))
        self.assertEqual(len(res), 7)
        vals = sorted((i[0][1] for i in res))
        self.assertEqual(vals, list(range(1, 8)))

    def test_v_select_10fwd_10bwd_2fwd(self):
        """SELECT 10 forward and 10 backward and 2 forward"""
        paginator = QueryPaginator(
            rows_num=7, query=SELECT, connection=TestSQLitePaginatorFeeder.conn
        )
        for _ in range(10):
            res = list(paginator.feeder(forward=True))
        for _ in range(10):
            res = list(paginator.feeder(forward=False))
        for _ in range(2):
            res = list(paginator.feeder(forward=True))

        self.assertEqual(len(res), 7)
        vals = sorted((i[0][1] for i in res))
        self.assertEqual(vals, list(range(15, 22)))


if __name__ == "__main__":
    unittest.main()
