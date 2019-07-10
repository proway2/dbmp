from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QTableView


class CustomTableView(QTableView):
    """
    This class inherits standard QTableView and for the only purpose is
    to handle mouse wheel and some keys which shines in conjuction with query
    paginator.
    Handling mouse wheel and keys gives user the ability to flawlessly walk
    thru pages.
    This class emits signals whether up or down of TableView is reached.
    Names left intact with Qt naming scheme.
    """

    # signals for situation where up or down reached
    upReached = pyqtSignal()
    downReached = pyqtSignal()

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
            self.firstRowReached(args[0])
        elif self.rowAt(self.height()) == -1 and not go_up:
            # this is the last row in viewport and we want to go down
            self.lastRowReached(args[0])
        else:
            return QTableView.wheelEvent(self, *args, **kwargs)

    def keyPressEvent(self, *args, **kwargs):
        """
        Handles arrows (up/down)
        """
        if args[0].key() == Qt.Key_Up and self.currentIndex().row() == 0:
            # Arrow Up
            self.firstRowReached(args[0])
        elif (
            args[0].key() == Qt.Key_Down
            and self.currentIndex().row()
            == self.model().rowCount(self.currentIndex()) - 1
        ):
            # Arrow Down
            self.lastRowReached(args[0])
        elif args[0].key() == Qt.Key_PageUp and self.rowAt(0) == 0:
            # PageUp
            self.firstRowReached(args[0])
        elif (
            args[0].key() == Qt.Key_PageDown
            and self.rowAt(self.height()) == -1
        ):
            # PageDown
            self.lastRowReached(args[0])
        else:
            return QTableView.keyPressEvent(self, *args, **kwargs)

    def firstRowReached(self, event):
        """Emits signal when first row reached"""
        event.ignore()
        self.upReached.emit()

    def lastRowReached(self, event):
        """Emits signal when last row reached"""
        event.ignore()
        self.downReached.emit()
