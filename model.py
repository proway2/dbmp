from PyQt5.Qt import QAbstractTableModel
from PyQt5.QtCore import QVariant, Qt


class TableModel(QAbstractTableModel):

    def __init__(self, parent=None, inputData=[], columns=[]):
        super().__init__(parent)
        # put inputData here
        self.inputData = inputData
        # assign column names
        self.columns = columns
        # reserve space for row numbers
        self.rows = []

    def data(self, index, role):
        # return the value of the model if index is valid
        # and role is DisplayRole
        if not index.isValid():
            return QVariant()
        elif role != Qt.DisplayRole and role != Qt.EditRole:
            return QVariant()

        # let's check if we've got DisplayRole
        if role == Qt.DisplayRole:
            return QVariant(self.inputData[index.row()][index.column()])
        return QVariant('')

    def rowCount(self, index):
        # just return the lengh of the list
        return len(self.inputData)

    def columnCount(self, index):
        # if there is a valid list then return number
        # of the elements in the first row
        if len(self.inputData):
            # regular return with inputData present
            return len(self.inputData[0])
        elif len(self.columns):
            # no inputData present (empty select)
            # we must return number of columns
            # for the view to render empty table
            return len(self.columns)
        else:
            # just in case
            return 0

    def headerData(self, section, orientation, role):
        # return the column name or the row number
        if role != Qt.DisplayRole:
            return QVariant()

        if orientation == Qt.Horizontal and self.columns:
            # this is for column name
            return self.columns[section]
        if self.rows:
            # this is for row number
            return self.rows[section]
        # this is the default
        return section + 1
