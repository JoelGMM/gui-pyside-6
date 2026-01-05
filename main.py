from PySide6.QtWidgets import QApplication, QMainWindow, QWidget
from PySide6.QtCore import Qt
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        w = 800
        h = 400

        # Janela principal
        self.resize(w+500, h+500)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Widget arredondado
        self.round_widget = QWidget(self)
        self.round_widget.resize(w, h)
        self.round_widget.setStyleSheet("""
            background: rgb(255, 255, 255);
            border-radius: 50px;
        """)

        # Variável de arraste
        self._drag_pos = None

        # 🔥 Encaminha eventos do widget para a janela
        self.round_widget.mousePressEvent = self.mousePressEvent
        self.round_widget.mouseMoveEvent = self.mouseMoveEvent
        self.round_widget.mouseReleaseEvent = self.mouseReleaseEvent

        self.show()

    # 🖱️ Mouse pressionado
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = (
                event.globalPosition().toPoint()
                - self.frameGeometry().topLeft()
            )
            event.accept()

    # 🖱️ Mouse movendo
    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton and self._drag_pos:
            self.move(
                event.globalPosition().toPoint() - self._drag_pos
            )
            event.accept()

    # 🖱️ Mouse solto
    def mouseReleaseEvent(self, event):
        self._drag_pos = None
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())
