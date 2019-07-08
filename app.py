#!/usr/bin/python3
import sys
import os
import importlib
from datetime import datetime
from PyQt5 import uic, QtCore, QtWidgets
from PyQt5.Qt import QMessageBox, pyqtSlot, QWidget

from model import TableModel
from paginator import QueryPaginator
from custom_tableview import CustomTableView

# we have to inherit the form from UI file, so we need to load it first.
FORM_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "app.ui")
)

# back button name
BACK_BUTTON_NAME = "pbBack"


class MainForm(QWidget, FORM_CLASS):
    def __init__(self, parent=None):
        # initialization
        super().__init__(parent)
        self.setupUi(self)
        self.__add_custom_tableview()
        self.leRowsPerPage.setText("001000")
        self.conn = None
        self.model = None
        self.db_provider = None

        # paginator
        self.paginator = None

        # describe DB providers here
        # order needs to be maintained to ensure that SQLite is the first one
        self.providers = {"SQLite": "sqlite3", "PostgreSQL": "psycopg2"}
        # add items to the list
        self.cmbProvider.addItems(self.providers.keys())

        # connect signals
        self.pbCheck.clicked.connect(self.check_connection)
        self.pbExecute.clicked.connect(self.execute_query)
        self.pbClose.clicked.connect(self.close_all)
        self.leConnection.editingFinished.connect(self.reset_conn)
        self.cmbProvider.currentIndexChanged.connect(self.provider_changed)
        # self.pbForth.clicked.connect(self.paging)
        self.pbForth.clicked.connect(self.page)
        # self.pbBack.clicked.connect(self.paging)
        self.pbBack.clicked.connect(self.page)

        # signals and slots for CustomTableView
        self.tbvResults.upReached.connect(self.pbBack.click)
        self.tbvResults.downReached.connect(self.pbForth.click)

    def __add_custom_tableview(self) -> bool:
        """
        Remove standard QTableView and adds custom CustomTableView to the form.
        """
        self.verticalLayout_2.removeWidget(self.tbvResults)
        self.tbvResults.deleteLater()
        self.tbvResults = None
        self.tbvResults = CustomTableView(self.gpbResults)
        self.tbvResults.setFrameShape(QtWidgets.QFrame.Panel)
        self.tbvResults.setObjectName("tbvResults")
        self.tbvResults.horizontalHeader().setVisible(True)
        self.verticalLayout_2.addWidget(self.tbvResults)
        self.verticalLayout_2.insertWidget(0, self.tbvResults)
        return True

    def close_all(self):
        # finish up the connection
        self.reset_conn()
        self.close()

    def keyPressEvent(self, *args, **kwargs):
        # check if Ctrl+Enter|Return pressed
        if (
            args[0].key() == QtCore.Qt.Key_Enter
            or args[0].key() == QtCore.Qt.Key_Return
        ) and args[0].modifiers() == QtCore.Qt.ControlModifier:
            # execute query
            self.execute_query()
        elif args[0].key() == QtCore.Qt.Key_Escape:
            self.pbClose.clicked.emit()
        else:
            # regular reaction
            return QWidget.keyPressEvent(self, *args, **kwargs)

    @pyqtSlot()
    def check_connection(self) -> bool:
        """Check button handler."""

        try:
            self.conn = self.try_to_connect()
        except (
            ValueError,
            ModuleNotFoundError,
            RuntimeError,
            self.db_provider.Warning,
            self.db_provider.InterfaceError,
            self.db_provider.DatabaseError,
            self.db_provider.DataError,
            self.db_provider.OperationalError,
            self.db_provider.IntegrityError,
            self.db_provider.InternalError,
            self.db_provider.ProgrammingError,
        ) as err:
            self.message_box(
                "Error!",
                f"Connection can not be established due to: {str(err)}",
                QMessageBox.Critical,
            )
            return False
        else:
            return True

    def __import_provider(self, provider_name: str):
        """Trying to import module for the provider and return it."""
        return importlib.import_module(str(self.providers[provider_name]))

    def __create_new_sqlite_file(self) -> bool:
        """Returns True if new sqlite file needs to be created"""
        if (
            self.leConnection.text().strip() != ":memory:"
            and not os.path.isfile(self.leConnection.text().strip())
            and self.message_box(
                "Attention!",
                (
                    f"The file {self.leConnection.text().strip()} does"
                    " not exist! Do you want to create it?"
                ),
                QMessageBox.Warning,
                buttons=QMessageBox.Ok | QMessageBox.Cancel,
            )
            != QMessageBox.Ok
        ):
            # User does not want to create file!
            return False
        return True

    def try_to_connect(self):
        """
        This function connects to the database with connection string
        provided by the user.
        """
        # there is a connection jump out of here
        if self.conn:
            return self.conn

        # no text - no connection
        if not self.leConnection.text().strip():
            raise ValueError("no connection string provided!")

        # let's try to import module
        self.db_provider = self.__import_provider(
            self.cmbProvider.currentData(0)
        )

        # since SQLite DB is a file we need to check if there is such file
        # or user wants to create new one
        if (
            self.db_provider.__name__ == "sqlite3"
            and not self.__create_new_sqlite_file()
        ):
            raise RuntimeError("no such file!")

        # create the connection
        return self.db_provider.connect(self.leConnection.text().strip())

    # def ready_to_execute(self):
    #     # just in case if connection is not established yet
    #     # we must try to connect
    #     res, sqliteSpecific = self.try_to_connect()
    #     if sqliteSpecific:
    #         # user does not want to create SQLite3 file!!!
    #         return False

    #     if not res and not sqliteSpecific:
    #         # somehow connection could not be established
    #         self.message_box(
    #             "Error!",
    #             "Connection can not be established!",
    #             QMessageBox.Critical,
    #         )
    #         return False

    #     if not self.teQuery.toPlainText():
    #         # we need to check if the query exists
    #         self.message_box(
    #             "Error!", "Nothing to execute!", QMessageBox.Critical
    #         )
    #         return False

    #     if int(self.leRowsPerPage.displayText()) < 1:
    #         self.message_box(
    #             "Error!",
    #             "Rows per page cannot be less than 1!",
    #             QMessageBox.Critical,
    #         )
    #         return False
    #     # yes, we can
    #     return True

    def __is_query_exists(self) -> bool:
        """Checks if query text is present."""
        if self.teQuery.toPlainText().strip():
            return True
        self.message_box("Error!", "No query provided", QMessageBox.Critical)
        return False

    @pyqtSlot()
    def execute_query(self):
        if not self.check_connection() or not self.__is_query_exists():
            return False

        # # check if we're ready
        # if not self.ready_to_execute():
        #     return False

        # let's try to create paginator object and execute query inside of it
        try:
            self.paginator = QueryPaginator(
                rows_num=int(self.leRowsPerPage.displayText().strip()),
                connection=self.conn,
                query=self.teQuery.toPlainText().strip(),
            )
        except (
            self.db_provider.Warning,
            self.db_provider.InterfaceError,
            self.db_provider.DatabaseError,
            self.db_provider.DataError,
            self.db_provider.OperationalError,
            self.db_provider.IntegrityError,
            self.db_provider.InternalError,
            self.db_provider.ProgrammingError,
            ValueError,
        ) as err:
            self.lblCurrentPage.setText("")
            self.message_box("Error!", str(err), QMessageBox.Critical)
            return False

        # emitting clicked signal on pbForth button
        self.pbForth.clicked.emit()

    def __is_forward(self, sender) -> bool:
        if sender().objectName() == BACK_BUTTON_NAME:
            return False
        return True

    @pyqtSlot()
    def page(self):
        if not self.paginator:
            return
        self.model = None
        if not self.paginator.fetched:
            self.model = TableModel(columns=self.paginator.headers())
        # let's save current state of the cursor
        savedCursor = self.cursor()
        try:
            # set the cursor to the wait cursor
            self.setCursor(QtCore.Qt.WaitCursor)
            # feed the model
            for row in self.paginator.feeder(self.__is_forward(self.sender)):
                if not self.model:
                    self.model = TableModel(columns=self.paginator.headers())

                # data
                self.model.input_data.append(row[0])
                # row number
                self.model.rows.append(row[1])
            # return the cursor to the previous state
            self.setCursor(savedCursor)
        except (
            self.db_provider.Warning,
            self.db_provider.InterfaceError,
            self.db_provider.DatabaseError,
            self.db_provider.DataError,
            self.db_provider.OperationalError,
            self.db_provider.IntegrityError,
            self.db_provider.InternalError,
            self.db_provider.ProgrammingError,
        ) as err:
            # return the cursor to the previous state
            self.setCursor(savedCursor)
            # unset current page
            self.lblCurrentPage.setText("")
            self.message_box("Error!", str(err), QMessageBox.Critical)
            # clean the model
            self.tbvResults.setModel(None)
            return False
        if not self.model:
            return False
        # clean the model
        self.tbvResults.setModel(None)
        # assign the new model
        self.tbvResults.setModel(self.model)
        self.tbvResults.selectRow(0)
        # if forward:
        #     self.tbvResults.selectRow(0)
        # else:
        #     self.tbvResults.selectRow(self.model.rowCount(None) - 1)

        # update last query result time
        self.lblUpdateTime.setText(
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        # update current page number
        self.lblCurrentPage.setText(str(self.paginator.real_current_page))
        return True

    # @pyqtSlot()
    # def paging(self):
    #     # first check if paginator exists
    #     if self.paginator is None:
    #         self.message_box(
    #             "Warning!", "No results to page!", QMessageBox.Warning
    #         )
    #         return

    #     # let's determine back or forth function
    #     func = self.paginator.forth
    #     forward = True
    #     if self.sender().objectName() == BACK_BUTTON_NAME:
    #         forward = False
    #         func = self.paginator.back

    #     if forward:
    #         # can we go forward?
    #         if not self.paginator.is_forth_possible():
    #             self.message_box(
    #                 "Warning!",
    #                 "Not possible to go forward!",
    #                 QMessageBox.Warning,
    #             )
    #             return
    #     else:
    #         # can we go backward?
    #         if not self.paginator.isBackPossible():
    #             # can we go backward?
    #             self.message_box(
    #                 "Warning!", "Not possible to go back!", QMessageBox.Warning
    #             )
    #             return

    #     # first create the new model
    #     self.model = TableModel(
    #         # input_data=[], columns=self.paginator.headers()
    #         columns=self.paginator.headers()
    #     )
    #     # let's save current state of the cursor
    #     savedCursor = self.cursor()
    #     try:
    #         # set the cursor to the wait cursor
    #         self.setCursor(QtCore.Qt.WaitCursor)
    #         # feed the model
    #         for row in func():
    #             # data
    #             self.model.input_data.append(row[0])
    #             # row number
    #             self.model.rows.append(row[1])
    #         # return the cursor to the previous state
    #         self.setCursor(savedCursor)
    #     except (
    #         self.db_provider.Warning,
    #         self.db_provider.InterfaceError,
    #         self.db_provider.DatabaseError,
    #         self.db_provider.DataError,
    #         self.db_provider.OperationalError,
    #         self.db_provider.IntegrityError,
    #         self.db_provider.InternalError,
    #         self.db_provider.ProgrammingError,
    #     ) as err:
    #         # return the cursor to the previous state
    #         self.setCursor(savedCursor)
    #         # unset current page
    #         self.lblCurrentPage.setText("")
    #         self.message_box("Error!", str(err), QMessageBox.Critical)
    #         # clean the model
    #         self.tbvResults.setModel(None)
    #         return False

    #     if self.paginator.is_data_query and self.paginator.no_more_results:
    #         # additional check in case the select query is fully depleted
    #         if not self.paginator.isForthPossible():
    #             self.message_box(
    #                 "Warning!",
    #                 "Not possible to go forward!",
    #                 QMessageBox.Warning,
    #             )
    #             return

    #     # clean the model
    #     self.tbvResults.setModel(None)
    #     # assign the new model
    #     self.tbvResults.setModel(self.model)
    #     if forward:
    #         self.tbvResults.selectRow(0)
    #     else:
    #         self.tbvResults.selectRow(self.model.rowCount(None) - 1)

    #     # update last query result time
    #     self.lblUpdateTime.setText(
    #         datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #     )
    #     # update current page number
    #     self.lblCurrentPage.setText(str(self.paginator.realCurrentPage))

    @pyqtSlot()
    def reset_conn(self):
        # drop the connection if it's established
        if self.conn:
            self.conn.close()
            self.conn = None

    @pyqtSlot(int)
    def provider_changed(self, index):
        # when the provider is changed we need to drop the connection
        self.reset_conn()

    def message_box(self, text, informative, icon, buttons=QMessageBox.Ok):
        # just to show informative boxes
        msg = QMessageBox(self)
        msg.setStandardButtons(buttons)
        msg.setDefaultButton(QMessageBox.Ok)
        msg.setText(text)
        msg.setInformativeText(informative)
        msg.setIcon(icon)
        return msg.exec_()


if __name__ == "__main__":
    # create the application
    app = QtWidgets.QApplication(sys.argv)

    # create form
    form = MainForm()
    form.show()

    # start main loop
    sys.exit(app.exec_())
