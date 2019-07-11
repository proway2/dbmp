#!/usr/bin/python3
import importlib
import os
import sys
from datetime import datetime

from PyQt5 import QtCore, QtWidgets, uic
from PyQt5.Qt import QMessageBox, QWidget, pyqtSlot

from custom_tableview import CustomTableView
from model import TableModel
from paginator import QueryPaginator

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
        self.pbForth.clicked.connect(self.page)
        self.pbBack.clicked.connect(self.page)

        # signals and slots for CustomTableView
        self.tbvResults.upReached.connect(self.pbBack.click)
        self.tbvResults.downReached.connect(self.pbForth.click)

    def __add_custom_tableview(self) -> bool:
        """
        Removes standard QTableView, adds custom CustomTableView to the form.
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
        """
        Overriding of parent's (Qt) method, that's why camelCase used.
        Ctrl+Enter executes query.
        """
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
    def check_connection(self, user: bool = True) -> bool:
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
            if user:
                self.message_box(
                    "Success!",
                    "Connection established",
                    QMessageBox.Information,
                )
            return True

    def __import_provider(self, provider_name: str):
        """Trying to import module for the provider and return it."""
        return importlib.import_module(str(self.providers[provider_name]))

    def __is_sqlite_db(self) -> bool:
        """Checks if DB provider is SQLite"""
        return self.db_provider.__name__ == "sqlite3"

    def __is_db_in_memory(self, db_type: str = ":memory:") -> bool:
        """
        Checks if database connection is of type :memory:.
        Makes sense for SQLite only.
        """
        return db_type == ":memory:"

    def __is_file(self, path_str: str = "") -> bool:
        """Checks if the path is a file."""
        return os.path.isfile(path_str)

    def __create_sqlite_file(self, file_name: str = ""):
        """
        Ckecks if user wants to create new SQLite file.
        Otherwise rises an exception.
        """
        question = (
            f"The file {file_name} does not exist! Do you want to create it?"
        )
        res = self.message_box(
            "Attention!",
            question,
            QMessageBox.Warning,
            buttons=QMessageBox.Ok | QMessageBox.Cancel,
        )
        if res != QMessageBox.Ok:
            raise RuntimeError("no such file!")

    def try_to_connect(self):
        """
        Connects to the database with the connection string
        provided by the user.
        """
        if self.conn:
            return self.conn

        # it's unknown what type of provider will user choose, so import here
        self.db_provider = self.__import_provider(
            self.cmbProvider.currentData(0)
        )

        db_conn_str = self.leConnection.text().strip()
        if not db_conn_str:
            raise ValueError("no connection string provided!")

        # since SQLite DB is a file we need to check if there is such file
        # or user wants to create new one
        if (
            self.__is_sqlite_db()
            and not self.__is_db_in_memory(db_conn_str)
            and not self.__is_file(db_conn_str)
        ):
            # Exception might be risen here
            self.__create_sqlite_file(db_conn_str)

        return self.db_provider.connect(db_conn_str)

    def __is_query_exists(self) -> bool:
        """Checks if query text is present."""
        if self.teQuery.toPlainText().strip():
            return True
        self.message_box("Error!", "No query provided", QMessageBox.Critical)
        return False

    @pyqtSlot()
    def execute_query(self):
        """Handles 'Execute' button."""
        if not self.check_connection(False) or not self.__is_query_exists():
            return False

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

        # model is created when forth or back button pressed
        # in order to create model we must emit signal
        self.pbForth.clicked.emit()

    def __is_forward(self, sender) -> bool:
        """Checks if direction is forward"""
        if sender().objectName() == BACK_BUTTON_NAME:
            return False
        return True

    @pyqtSlot()
    def page(self):
        """Pages query results"""
        if not self.paginator:
            return
        self.model = None
        # if data is not fetched from paginator yet we must recreate model
        # because we dont know beforehead if data will arrive.
        # otherwise we can end up in situation when paginator is already
        # fetched (might be partially), model is None and
        # no new data will arrive in for loop (paginator.feeder)
        # this potential situation leads to empty model in view
        if not self.paginator.fetched:
            self.model = TableModel(columns=self.paginator.headers())
        # let's save current state of the cursor
        savedCursor = self.cursor()
        try:
            # set the cursor to the wait cursor
            self.setCursor(QtCore.Qt.WaitCursor)
            # feed the model
            for row in self.paginator.feeder(self.__is_forward(self.sender)):
                # we must be ensured that model is changed when
                # actual data arrives only
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
        self.__update_model_in_view()
        # update last query result time and page number
        self.__update_time_and_page()

        if self.__is_forward(self.sender):
            self.tbvResults.selectRow(0)
        else:
            self.tbvResults.selectRow(self.model.rowCount(None) - 1)
        return True

    def __update_model_in_view(self):
        """Updates model in view."""
        self.tbvResults.setModel(None)
        self.tbvResults.setModel(self.model)
        self.tbvResults.selectRow(0)

    def __update_time_and_page(self):
        """Updates execution time and page number"""
        self.lblUpdateTime.setText(
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        self.lblCurrentPage.setText(str(self.paginator.current_page))

    @pyqtSlot()
    def reset_conn(self):
        """Resets connection"""
        if self.conn:
            self.conn.close()
            self.conn = None

    @pyqtSlot(int)
    def provider_changed(self, index):
        """Handles provider change in the providers list box. Resets conn."""
        self.reset_conn()

    def message_box(self, text, informative, icon, buttons=QMessageBox.Ok):
        """Wraps up the QMessageBox"""
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
