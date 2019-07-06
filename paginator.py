class QueryPaginator:
    def __init__(self, numberOfRows=1000, query=None, connection=None):
        if connection is None:
            return
        # define default page
        self.currentPage = 0
        # define default number of rows per fetch
        self.numberOfRows = numberOfRows
        # we need to run query on the open connection
        self.conn = connection
        # we need to know current cursor
        self.curs = None
        # we need the query to run
        self.query = query
        # we need an indicator to check if query is depleted
        self.noMoreResults = False
        self.lastFetchRows = -1
        # execute query at creation
        if query is not None:
            self.executeQuery(query)

    def executeQuery(self, query=""):
        """Executes query"""
        # let's try to execute query
        # obtain the cursor before the query
        if self.curs is None:
            self.curs = self.conn.cursor()
        # execute query
        self.curs.execute(query)
        # commit it just in case
        self.conn.commit()
        # reset variables
        self.lastFetchRows = -1
        self.noMoreResults = False

    @property
    def realCurrentPage(self):
        """Returns the number of current page"""
        if self.query is None:
            # nothing to do
            return
        # this is the actual page number
        return 1 if self.currentPage <= 0 else self.currentPage

    @property
    def isDataQuery(self):
        """Returns True if this was 'select' query"""
        if self.query and self.curs:
            return False if self.curs.description is None else True

    def isBackPossible(self):
        """Returns True if going back is possible"""
        if self.query is None:
            # nothing to do
            return False
        # returns TRUE if going back is possible
        return True if self.currentPage > 1 else False

    def back(self):
        """Generator to feed the rows of the query when going backward"""
        if self.query is None:
            # nothing to do
            return

        if self.currentPage <= 1:
            return
        # REexecute query
        self.executeQuery(self.query)
        # we need to check if this is data query
        if self.curs.description is not None:
            # dry runs
            for i in range(1, self.currentPage - 1):
                self.curs.fetchmany(self.numberOfRows)
                i = i
            # actual run
            yield from self.__feeder(forward=False)

    def isForthPossible(self):
        """Returns True if going forward is possible"""
        if self.query is None or self.noMoreResults:
            # nothing to do
            return False
        # we can go forward
        return True

    def forth(self):
        """Generator to feed the rows of the query when going forward"""
        if self.query is None:
            # nothing to do
            return

        # this is no data (select) query
        if not self.isDataQuery:
            # creates, inserts, updates, deletes
            if self.curs.rowcount == -1:
                # create statement
                yield ("Successfully executed!",), 1
            else:
                # insert or update or delete
                yield ("Affected rows: {}".format(self.curs.rowcount),), 1
            self.lastFetchRows = 1
            self.noMoreResults = True
        else:
            # select query
            yield from self.__feeder()

    def getHeaders(self):
        """Returns list of headers for the query"""
        # return list of the columns headers
        if not self.isDataQuery:
            # creates, inserts, updates, deletes
            return ["Result"]
        else:
            # select
            return [descr[0] for descr in self.curs.description]

    def __feeder(self, forward=True):
        """
        Returns rows from query in different direction.

        Keyword arguments:
        forward -- sets the direction (default True),
        backward direction is forward=False
        """
        # select query ONLY!!!
        if not self.isDataQuery or self.noMoreResults:
            return

        # must store prev rows fetched to check if this select returns 0 rows
        prevFetch = self.lastFetchRows
        # we need to check if this is data query
        self.lastFetchRows = 0
        for num, row in enumerate(self.curs.fetchmany(self.numberOfRows)):
            self.lastFetchRows += 1
            # return the row and the number of this row
            if forward:
                yield row, self.currentPage * self.numberOfRows + num + 1
            else:
                # return the row and the number of this row
                yield row, (self.currentPage - 2) * self.numberOfRows + num + 1

        if not self.lastFetchRows and prevFetch != -1:
            # no more results if lastFetchRows == 0 and prevFetch is not -1 !
            self.noMoreResults = True
        else:
            # we need to change current page
            # and check if the query has any rows
            # update current page number
            if forward:
                self.currentPage += 1
            elif self.currentPage > 0:
                self.currentPage -= 1
