from PyQt5.Qt import QAbstractTableModel
from PyQt5.QtCore import Qt, QVariant


class TableModel(QAbstractTableModel):
    """
    This class inherits standard QAbstractTableModel and overrides some
    methods.
    All methods override base class methods, so names left intact with
    Qt naming scheme.
    """

    def __init__(self, parent=None, columns=None):
        super().__init__(parent)
        # data storage
        self.input_data = []
        # column names
        self.columns = columns or []
        # row numbers
        self.rows = []

    def data(self, index, role):
        """
        Returns the data stored under the given role
        for the item referred to by the index.
        """
        if not index.isValid():
            return QVariant()
        elif role != Qt.DisplayRole and role != Qt.EditRole:
            return QVariant()

        # let's check if we've got DisplayRole
        if role == Qt.DisplayRole:
            return QVariant(self.input_data[index.row()][index.column()])
        return QVariant("")

    def rowCount(self, index):
        """Returns the number of rows in the model"""
        return len(self.input_data)

    def columnCount(self, index):
        """Returns the number of columns"""
        if self.input_data:
            # number of columns returned
            return len(self.input_data[0])
        elif self.columns:
            # no input_data present (empty select)
            # we must return number of columns
            # for the view to render empty table
            return len(self.columns)
        else:
            # no data in the model
            return 0

    def headerData(self, section, orientation, role):
        """
        Returns the data for the given role and section in the header with
        the specified orientation.
        """
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
