class QueryPaginator:
    """
    Takes query as input and feeds its data to the customer.
    Feeder can go forward or backward.
    """

    def __init__(self, rows_num: int = 1000, query: str = "", connection=None):
        if not connection:
            raise ValueError("no connection provided")
        if not (isinstance(query, str) and query.strip()):
            raise ValueError("no query provided")
        if not hasattr(connection, "cursor") and not hasattr(
            connection, "commit"
        ):
            raise ValueError("unexpected connection")
        if rows_num < 1:
            raise ValueError("number of rows must be greater than 0")
        # define default page
        self.__current_page = 0
        # define default number of rows per fetch
        self.__number_of_rows = rows_num
        # we need to run query on the open connection
        self.__conn = connection
        # we need to know current cursor
        self.__curs = None
        # we need the query to run
        self.__query = query
        # execute query at creation
        self.__execute_query(self.__query)
        self.__fetched = False

    def __execute_query(self, query: str = "") -> bool:
        """Executes query"""
        # let's try to execute query
        # obtain the cursor before the query
        if not self.__curs:
            try:
                self.__curs = self.__conn.cursor()
            except Exception:
                raise
        # execute query
        self.__curs.execute(query)
        # commit it just in case
        self.__conn.commit()
        # reset variables
        self.__fetched = False
        self.__current_page = 0
        return True

    @property
    def fetched(self) -> bool:
        """Returns status if the query fetched already."""
        return self.__fetched

    @property
    def current_page(self):
        """Returns the number of current page"""
        if not self.__query:
            # nothing to do
            return
        # this is the actual page number
        return 1 if self.__current_page <= 0 else self.__current_page

    @property
    def is_data_query(self):
        """Returns True if this is 'select' query"""
        if self.__query and self.__curs:
            return False if self.__curs.description is None else True

    def headers(self) -> list:
        """Returns list of headers for the query"""
        # return list of the columns headers
        if self.is_data_query:
            # DML
            return [descr[0] for descr in self.__curs.description]
        # DDL
        return ["Result"]

    def feeder(self, forward: bool = True):
        """Feeds the data from the query's result."""
        feeder_func = self.__sql_type_factory(self.is_data_query)
        yield from feeder_func(forward)
        self.__fetched = True

    def __sql_type_factory(self, data_query=True):
        """Factory function returns handler for DDL or DML queries."""
        if data_query:
            # select
            return self.__dml_feeder
        # create, insert, delete
        return self.__ddl_feeder

    def __dml_feeder(self, forward=True):
        """Pager for DML query, handles backward direction."""
        if not forward:
            if self.__current_page <= 1:
                return  # StopIteration
            # to fast forward for certain number of runs we must save cur page
            ff_runs = self.__current_page
            # ff must be done from the very begining, so reexecute query
            self.__execute_query(self.__query)
            self.__fast_forward(ff_runs - 2)
        # feed data to customer
        yield from self.__select_feeder()

    def __select_feeder(self):
        """
        Feeds results from the select query. Forward direction only.
        Feeds tuple (<row data>, <row number>)
        """
        runs = False
        for num, row in enumerate(
            self.__curs.fetchmany(self.__number_of_rows), 1
        ):
            runs = True
            yield row, self.__current_page * self.__number_of_rows + num
        if runs:
            self.__current_page += 1

    def __fast_forward(self, runs: int = 0):
        """Fast forward some pages to make going back possible."""
        for _ in range(0, runs):
            for _ in self.__select_feeder():
                pass

    def __ddl_feeder(self, forward=True):
        """Feeder for DDL type queries."""
        # creates, inserts, updates, deletes
        if not forward or self.__fetched:
            return  # StopIteration
        if self.__curs.rowcount == -1:
            # create statement
            yield ("Successfully executed!",), 1
        else:
            # insert or update or delete
            yield ("Affected rows: {}".format(self.__curs.rowcount),), 1
