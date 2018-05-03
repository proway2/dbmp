#!/usr/bin/python3
import sys
import os
import importlib
from collections import OrderedDict
from datetime import datetime
from PyQt5.QtWidgets import QApplication
from PyQt5 import uic, QtCore
from PyQt5.Qt import QMessageBox, pyqtSlot, QWidget
from model import TableModel
from paginator import QueryPaginator

# let's try to load the form
# if there is no form we're stuck!
FORM_CLASS, X_CLASS = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'app.ui'))

# back button name
BACK_BUTTON_NAME = 'pbBack'


class MainForm(QWidget, FORM_CLASS):

    def __init__(self, parent=None):
        # initialization
        super().__init__(parent)
        self.setupUi(self)
        self.leRowsPerPage.setText('001000')
        self.conn = None
        self.model = None
        self.dbProvider = None

        # paginator
        self.paginator = None

        # describe DB providers here (we need to maintain order)
        self.providers = OrderedDict([
            ('SQLite', 'sqlite3'),
            ('PostgreSQL', 'psycopg2'),
        ])
        # add items to the list
        self.cmbProvider.addItems(self.providers.keys())

        # connect signals
        self.pbCheck.clicked.connect(self.checkConnection)
        self.pbExecute.clicked.connect(self.executeQuery)
        self.pbClose.clicked.connect(self.closeAll)
        self.leConnection.editingFinished.connect(self.resetConn)
        self.cmbProvider.currentIndexChanged.connect(self.providerChanged)
        self.pbForth.clicked.connect(self.paging)
        self.pbBack.clicked.connect(self.paging)

    def closeAll(self):
        # finish up the connection
        self.resetConn()
        self.close()

    def keyPressEvent(self, *args, **kwargs):
        # check if Ctrl+Enter|Return pressed
        if (args[0].key() == QtCore.Qt.Key_Enter or
           args[0].key() == QtCore.Qt.Key_Return) and\
           args[0].modifiers() == QtCore.Qt.ControlModifier:
            # execute query
            self.executeQuery()
        elif (args[0].key() == QtCore.Qt.Key_Right and
              args[0].modifiers() == QtCore.Qt.ControlModifier
              ):
            self.pbForth.clicked.emit()
        elif args[0].key() == QtCore.Qt.Key_Escape:
            self.pbClose.clicked.emit()
        else:
            # regular reaction
            return QWidget.keyPressEvent(self, *args, **kwargs)

    @pyqtSlot()
    def checkConnection(self):
        # let's check if we can connect
        if self.tryToConnect():
            self.messageBox('Success!',
                            'Connection established successfully!',
                            QMessageBox.Information)
            return True

        self.messageBox('Error!', 'Connection can not be established!',
                        QMessageBox.Critical)

    def readyToExecute(self):
        # we need to check if the query exists
        if not self.teQuery.toPlainText():
            self.messageBox('Error!', 'No query to execute!',
                            QMessageBox.Critical)
            return False

        # just in case if connection is not established yet
        # we must try to connect
        if not self.tryToConnect():
            self.messageBox('Error!', 'Connection can not be established!',
                            QMessageBox.Critical)
            return False

        if int(self.leRowsPerPage.displayText()) < 1:
            self.messageBox('Error!', 'Rows per page cannot be less than 1!',
                            QMessageBox.Critical)
            return False
        # yes, we can
        return True

    @pyqtSlot()
    def executeQuery(self):
        # check if we're ready
        if not self.readyToExecute():
            return False

        # let's try to create paginator object and execute query inside of it
        try:
            self.paginator = QueryPaginator(
                numberOfRows=int(self.leRowsPerPage.displayText()),
                connection=self.conn,
                query=self.teQuery.toPlainText()
            )
        except (
                self.dbProvider.Warning, self.dbProvider.InterfaceError,
                self.dbProvider.DatabaseError, self.dbProvider.DataError,
                self.dbProvider.OperationalError,
                self.dbProvider.IntegrityError,
                self.dbProvider.InternalError,
                self.dbProvider.ProgrammingError
                ) as err:
            self.lblCurrentPage.setText(str(''))
            self.messageBox('Error!', str(err),
                            QMessageBox.Critical)
            return False

        # emitting clicked signal on pbForth button
        self.pbForth.clicked.emit()

    @pyqtSlot()
    def paging(self):
        # first check if paginator exists
        if self.paginator is None:
            self.messageBox('Warning!',
                            'No results to page!',
                            QMessageBox.Warning)
            return

        # let's determine back or forth function
        func = self.paginator.forth
        forward = True
        if self.sender().objectName() == BACK_BUTTON_NAME:
            forward = False
            func = self.paginator.back

        if forward:
            # can we go forward?
            if not self.paginator.isForthPossible():
                self.messageBox('Warning!',
                                'Not possible to go forward!',
                                QMessageBox.Warning)
                return
        else:
            # can we go backward?
            if not self.paginator.isBackPossible():
                # can we go backward?
                self.messageBox('Warning!',
                                'Not possible to go back!',
                                QMessageBox.Warning)
                return

        # first create the new model
        self.model = TableModel(inputData=[],
                                columns=self.paginator.getHeaders())
        try:
            # feed the model
            for row in func():
                # data
                self.model.inputData.append(row[0])
                # row number
                self.model.rows.append(row[1])
        except (
                self.dbProvider.Warning, self.dbProvider.InterfaceError,
                self.dbProvider.DatabaseError, self.dbProvider.DataError,
                self.dbProvider.OperationalError,
                self.dbProvider.IntegrityError,
                self.dbProvider.InternalError,
                self.dbProvider.ProgrammingError
                ) as err:
            self.lblCurrentPage.setText(str(''))
            self.messageBox('Error!', str(err),
                            QMessageBox.Critical)
            # clean the model
            self.tbvResults.setModel(None)
            return False

        if self.paginator.isDataQuery and self.paginator.noMoreResults:
            # additional check in case the select query is fully depleted
            if not self.paginator.isForthPossible():
                self.messageBox('Warning!',
                                'Not possible to go forward!',
                                QMessageBox.Warning)
                return

        # clean the model
        self.tbvResults.setModel(None)
        # assign the new model
        self.tbvResults.setModel(self.model)
        # update last query result time
        self.lblUpdateTime.setText(
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        # update current page number
        self.lblCurrentPage.setText(
            str(self.paginator.realCurrentPage)
        )

    def tryToConnect(self):
        # no text - no connection
        if not self.leConnection.text():
            return False

        # there is a connection jump out of here
        if self.conn is not None:
            return True

        # let's try to import module
        try:
            self.dbProvider = importlib.import_module(
                str(self.providers[self.cmbProvider.currentData(0)])
            )
        except Exception as err:
            self.messageBox('Error!', str(err),
                            QMessageBox.Critical)
            return False

        # let's try to make a connection based on provider name
        try:
            # create the connection
            self.conn = self.dbProvider.connect(self.leConnection.text())
            # is it possible???
            if self.conn is not None:
                return True
        except (
                self.dbProvider.Warning, self.dbProvider.InterfaceError,
                self.dbProvider.DatabaseError, self.dbProvider.DataError,
                self.dbProvider.OperationalError,
                self.dbProvider.IntegrityError,
                self.dbProvider.InternalError,
                self.dbProvider.ProgrammingError
                ) as err:
            self.messageBox('Error!', str(err),
                            QMessageBox.Critical)
            # no import or no connection created
            return False

    @pyqtSlot()
    def resetConn(self):
        # drop the connection if it's established
        if self.conn is not None:
            self.conn.close()
            self.conn = None

    @pyqtSlot(int)
    def providerChanged(self, index):
        # when the provider is changed we need to drop the connection
        self.resetConn()

    def messageBox(self, text, informative, icon):
        # just to show informative boxes
        msg = QMessageBox(self)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setDefaultButton(QMessageBox.Ok)
        msg.setText(text)
        msg.setInformativeText(informative)
        msg.setIcon(icon)
        msg.exec_()


if __name__ == '__main__':
    # create the application
    app = QApplication(sys.argv)

    # create form
    test = MainForm()
    test.show()

    # start main loop
    sys.exit(app.exec_())