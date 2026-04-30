from PySide6.QtWidgets import QStackedWidget, QDialog
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QVBoxLayout, QWidget

class ModalOverlay(QDialog):

    def __init__(self, parent, title="Dialog"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.setStyleSheet("""
            QDialog {
                background-color: rgba(0, 0, 0, 0.5);
                border-radius: 8px;
            }
        index = self.stacked_widget.addWidget(widget)
        return index

    def show_screen(self, name):
        if name in self.screens:
            self.stacked_widget.setCurrentWidget(self.screens[name])
            return True
        return False

    def show_modal(self, dialog, title="Dialog"):
        modal = ModalOverlay(self.main_window, title)
        layout = QVBoxLayout()
        layout.addWidget(dialog)
        modal.setLayout(layout)
        modal.exec()
