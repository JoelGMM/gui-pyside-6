from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal, QPointF
from PySide6.QtGui import QPainter, QConicalGradient, QRadialGradient, QColor, QPen, QBrush
import sys
import math


class ColorWheel(QWidget):
    """Widget de roda de cores interativa"""
    colorSelected = Signal(QColor)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(300, 300)
        self._selected_color = QColor(255, 0, 0)
        self._selector_pos = QPointF(0, 0)
        self._is_pressed = False

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Calcular centro e raio
        center = self.rect().center()
        radius = min(self.width(), self.height()) // 2 - 20

        # Gradiente conico para as cores (matiz)
        conical = QConicalGradient(center, 0)
        for i in range(360):
            color = QColor.fromHsv(i, 255, 255)
            conical.setColorAt(i / 360.0, color)
        conical.setColorAt(1.0, QColor.fromHsv(0, 255, 255))

        # Desenhar o anel de cores
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(conical))
        painter.drawEllipse(center, radius, radius)

        # Gradiente radial para saturacao (branco no centro)
        radial = QRadialGradient(center, radius)
        radial.setColorAt(0.0, QColor(255, 255, 255))
        radial.setColorAt(1.0, QColor(255, 255, 255, 0))
        painter.setBrush(QBrush(radial))
        painter.drawEllipse(center, radius, radius)

        # Desenhar o seletor
        painter.setPen(QPen(Qt.white, 3))
        painter.setBrush(QBrush(self._selected_color))
        painter.drawEllipse(self._selector_pos, 12, 12)

        # Borda externa do seletor
        painter.setPen(QPen(Qt.black, 1))
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(self._selector_pos, 13, 13)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._is_pressed = True
            self._update_color(event.position())
            event.accept()

    def mouseMoveEvent(self, event):
        if self._is_pressed:
            self._update_color(event.position())
            event.accept()

    def mouseReleaseEvent(self, event):
        if self._is_pressed:
            self._is_pressed = False
            self.colorSelected.emit(self._selected_color)
            event.accept()

    def _update_color(self, pos):
        center = QPointF(self.width() / 2, self.height() / 2)
        radius = min(self.width(), self.height()) / 2 - 20

        # Vetor do centro ate o ponto clicado
        dx = pos.x() - center.x()
        dy = pos.y() - center.y()
        distance = math.sqrt(dx * dx + dy * dy)

        # Limitar ao raio
        if distance > radius:
            dx = dx * radius / distance
            dy = dy * radius / distance
            distance = radius

        # Calcular angulo (matiz)
        angle = math.degrees(math.atan2(dy, dx))
        hue = int((angle + 360) % 360)

        # Calcular saturacao baseada na distancia do centro
        saturation = int((distance / radius) * 255)

        # Criar cor
        self._selected_color = QColor.fromHsv(hue, saturation, 255)
        self._selector_pos = QPointF(center.x() + dx, center.y() + dy)
        self.update()


class MonochromaticPaletteWindow(QWidget):
    """Janela que mostra uma paleta monocromatica"""

    def __init__(self, base_color: QColor, parent=None):
        super().__init__(parent)
        self.base_color = base_color

        # Configurar janela arredondada sem borda
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(400, 500)

        # Widget arredondado
        self.round_widget = QWidget(self)
        self.round_widget.setGeometry(0, 0, 400, 500)
        self.round_widget.setStyleSheet("""
            background: rgb(40, 40, 40);
            border-radius: 30px;
        """)

        # Layout
        layout = QVBoxLayout(self.round_widget)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(10)

        # Titulo
        title = QLabel("Paleta Monocromatica")
        title.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Cor base info
        hue = base_color.hue()
        sat = base_color.saturation()

        # Gerar variantes monocromaticas (diferentes valores de brilho/saturacao)
        variants = [
            ("Mais Claro", QColor.fromHsv(hue, max(0, sat - 100), 255)),
            ("Claro", QColor.fromHsv(hue, max(0, sat - 50), 240)),
            ("Base", base_color),
            ("Escuro", QColor.fromHsv(hue, min(255, sat + 30), 180)),
            ("Mais Escuro", QColor.fromHsv(hue, min(255, sat + 50), 120)),
            ("Muito Escuro", QColor.fromHsv(hue, min(255, sat + 50), 60)),
        ]

        for name, color in variants:
            color_widget = QWidget()
            color_widget.setFixedHeight(50)
            color_widget.setStyleSheet(f"""
                background: rgb({color.red()}, {color.green()}, {color.blue()});
                border-radius: 10px;
            """)

            # Label com nome e codigo hex
            label = QLabel(f"{name}: {color.name().upper()}")
            label.setAlignment(Qt.AlignCenter)

            # Cor do texto baseada no brilho
            text_color = "white" if color.value() < 150 else "black"
            label.setStyleSheet(f"color: {text_color}; font-size: 14px; background: transparent;")

            color_layout = QVBoxLayout(color_widget)
            color_layout.addWidget(label)

            layout.addWidget(color_widget)

        # Botao fechar
        close_btn = QLabel("Clique para fechar")
        close_btn.setStyleSheet("""
            color: #888;
            font-size: 12px;
            padding: 10px;
        """)
        close_btn.setAlignment(Qt.AlignCenter)
        close_btn.mousePressEvent = lambda e: self.close()
        layout.addWidget(close_btn)

        # Variavel de arraste
        self._drag_pos = None

        # Eventos de arraste
        self.round_widget.mousePressEvent = self._mouse_press
        self.round_widget.mouseMoveEvent = self._mouse_move
        self.round_widget.mouseReleaseEvent = self._mouse_release

    def _mouse_press(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def _mouse_move(self, event):
        if event.buttons() & Qt.LeftButton and self._drag_pos:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def _mouse_release(self, event):
        self._drag_pos = None
        event.accept()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        w = 400
        h = 500

        # Janela principal
        self.resize(w, h)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Widget arredondado
        self.round_widget = QWidget(self)
        self.round_widget.setGeometry(0, 0, w, h)
        self.round_widget.setStyleSheet("""
            background: rgb(30, 30, 30);
            border-radius: 40px;
        """)

        # Layout principal
        layout = QVBoxLayout(self.round_widget)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        # Titulo
        title = QLabel("Escolha uma Cor")
        title.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Color wheel
        self.color_wheel = ColorWheel()
        self.color_wheel.colorSelected.connect(self._on_color_selected)
        layout.addWidget(self.color_wheel, 1)

        # Instrucao
        instruction = QLabel("Clique e arraste para selecionar")
        instruction.setStyleSheet("color: #888; font-size: 12px;")
        instruction.setAlignment(Qt.AlignCenter)
        layout.addWidget(instruction)

        # Preview da cor selecionada
        self.preview = QWidget()
        self.preview.setFixedHeight(40)
        self.preview.setStyleSheet("""
            background: rgb(255, 0, 0);
            border-radius: 10px;
        """)
        layout.addWidget(self.preview)

        # Botao fechar
        close_btn = QLabel("ESC para fechar")
        close_btn.setStyleSheet("color: #555; font-size: 11px;")
        close_btn.setAlignment(Qt.AlignCenter)
        layout.addWidget(close_btn)

        # Variavel de arraste
        self._drag_pos = None

        # Janela de paleta
        self.palette_window = None

        self.show()

    def _on_color_selected(self, color: QColor):
        # Atualizar preview
        self.preview.setStyleSheet(f"""
            background: rgb({color.red()}, {color.green()}, {color.blue()});
            border-radius: 10px;
        """)

        # Fechar janela de paleta anterior se existir
        if self.palette_window:
            self.palette_window.close()

        # Criar nova janela de paleta monocromatica
        self.palette_window = MonochromaticPaletteWindow(color)
        self.palette_window.move(self.x() + self.width() + 20, self.y())
        self.palette_window.show()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
        super().keyPressEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = (
                event.globalPosition().toPoint()
                - self.frameGeometry().topLeft()
            )
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton and self._drag_pos:
            self.move(
                event.globalPosition().toPoint() - self._drag_pos
            )
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())
