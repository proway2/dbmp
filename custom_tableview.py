from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QTableView


class CustomTableView(QTableView):
    """
    This class inherits standard QTableView and extends it's functionality
    by adding two new signals: top_reached_signal, bottom_reached_signal.
    Signals are emitted when the top or the bottom of the table is reached by
    either of: navigation keys, PgUp/PgDown, mouse wheel.
    New signals help in situation when pagination is required.
    Names of the overriden methods left intact with Qt naming scheme.
    """

    # signals for situation where up or down reached
    top_reached_signal = pyqtSignal()
    bottom_reached_signal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

    def wheelEvent(self, *args, **kwargs):
        """
        This is the reimplementation of mouse wheel handler.
        'Go up' in this context means wheel was rotated away from the user.
        """
        # 'go up' means - wheel is going outbound from user
        go_up = False
        if args[0].angleDelta().y() > 0:
            go_up = True
        if self.rowAt(0) == 0 and go_up:
            # this is the first row in viewport and we want to go up
            self.top_row_reached(args[0])
        elif self.rowAt(self.height()) == -1 and not go_up:
            # this is the last row in viewport and we want to go down
            self.bottom_row_reached(args[0])
        else:
            return QTableView.wheelEvent(self, *args, **kwargs)

    def keyPressEvent(self, *args, **kwargs):
        """
        Handles arrows (up/down) and PgUp/PgDn
        """
        if args[0].key() == Qt.Key_Up and self.currentIndex().row() == 0:
            # Arrow Up
            self.top_row_reached(args[0])
        elif (
            args[0].key() == Qt.Key_Down
            and self.currentIndex().row()
            == self.model().rowCount(self.currentIndex()) - 1
        ):
            # Arrow Down
            self.bottom_row_reached(args[0])
        elif args[0].key() == Qt.Key_PageUp and self.rowAt(0) == 0:
            # PageUp
            self.top_row_reached(args[0])
        elif (
            args[0].key() == Qt.Key_PageDown
            and self.rowAt(self.height()) == -1
        ):
            # PageDown
            self.bottom_row_reached(args[0])
        else:
            return QTableView.keyPressEvent(self, *args, **kwargs)

    def top_row_reached(self, event):
        """Emits signal when the first row reached"""
        event.ignore()
        self.top_reached_signal.emit()

    def bottom_row_reached(self, event):
        """Emits signal when the last row reached"""
        event.ignore()
        self.bottom_reached_signal.emit()
