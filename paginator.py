class QueryPaginator:
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
        self.current_page = 0
        # define default number of rows per fetch
        self.number_of_rows = rows_num
        # we need to run query on the open connection
        self.conn = connection
        # we need to know current cursor
        self.curs = None
        # we need the query to run
        self.query = query
        # execute query at creation
        self.__execute_query(query)
        self.fetched = False

    def __execute_query(
        self, query: str = "", reset_counter: bool = True
    ) -> bool:
        """Executes query"""
        # let's try to execute query
        # obtain the cursor before the query
        if not self.curs:
            try:
                self.curs = self.conn.cursor()
            except Exception:
                raise
        # execute query
        self.curs.execute(query)
        # commit it just in case
        self.conn.commit()
        # reset variables
        self.fetched = False
        if reset_counter:
            self.current_page = 0
        return True

    @property
    def real_current_page(self):
        """Returns the number of current page"""
        if not self.query:
            # nothing to do
            return
        # this is the actual page number
        return 1 if self.current_page <= 0 else self.current_page

    @property
    def is_data_query(self):
        """Returns True if this is 'select' query"""
        if self.query and self.curs:
            return False if self.curs.description is None else True

    def headers(self) -> list:
        """Returns list of headers for the query"""
        # return list of the columns headers
        if self.is_data_query:
            # DML
            return [descr[0] for descr in self.curs.description]
        # DDL
        return ["Result"]

    def feeder(self, forward: bool = True):
        """Feeds the data from the query's result."""
        feeder_func = self.sql_type_factory(self.is_data_query)
        yield from feeder_func(forward)
        self.fetched = True

    def sql_type_factory(self, data_query=True):
        """Factory function returns handler for DDL or DML queries."""
        if data_query:
            # select
            return self.__dml_feeder
        # create, insert, delete
        return self.__ddl_feeder

    def __dml_feeder(self, forward=True):
        """Feeder for DML (SELECT) type queries."""
        if not forward:
            if self.current_page <= 1:
                raise StopIteration()
            # in order to get back we need to rerun query from the start
            # REexecute query
            self.__execute_query(self.query, reset_counter=False)
            # fast forward to the desired page
            self.__fast_forward()
        # select
        for num, row in enumerate(self.curs.fetchmany(self.number_of_rows)):
            yield row, self.current_page * self.number_of_rows + num + 1
        # in order to maintain current_page at the actual figure we
        # must raise exception when empty runs discovered
        try:
            num
        except UnboundLocalError:
            raise StopIteration()
        self.__change_current_page(forward)

    def __change_current_page(self, forward: bool = True):
        """Maintaines the current_page at the actual figure."""
        if forward:
            self.current_page += 1
        else:
            self.current_page = (
                0 if self.current_page <= 1 else self.current_page - 1
            )

    def __fast_forward(self):
        """Fast forward some pages to make going back possible."""
        # dry runs
        for _ in range(0, self.current_page - 2):
            self.curs.fetchmany(self.number_of_rows)

    def __ddl_feeder(self, forward=True):
        """Feeder for DDL type queries."""
        # creates, inserts, updates, deletes
        if not forward or self.fetched:
            raise StopIteration()
        if self.curs.rowcount == -1:
            # create statement
            yield ("Successfully executed!",), 1
        else:
            # insert or update or delete
            yield ("Affected rows: {}".format(self.curs.rowcount),), 1
