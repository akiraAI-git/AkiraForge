from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor, QPen, QBrush
from PySide6.QtCore import Qt, QTimer, QRectF

class NeonHealthIndicator(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.health = "GOOD"  # GOOD / WARNING / CRITICAL
        self.pulse = 0
        self.pulse_direction = 1

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(50)

    def set_health(self, health):
        self.health = health
        self.update()

    def animate(self):
        if self.health == "CRITICAL":
            self.pulse += self.pulse_direction * 0.08
            if self.pulse >= 1 or self.pulse <= 0:
                self.pulse_direction *= -1
        else:
            self.pulse = 0

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        size = min(self.width(), self.height())
        rect = QRectF(5, 5, size - 10, size - 10)

        if self.health == "GOOD":
            color = QColor(0, 255, 80)
        elif self.health == "WARNING":
            color = QColor(255, 200, 0)
        else:
            base = 150 + int(self.pulse * 105)
            color = QColor(255, base, base)

        glow = QPen(color)
        glow.setWidth(12)
        painter.setPen(glow)
        painter.drawEllipse(rect)

        brush = QBrush(color)
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        painter.setBrush(brush)

        inner_rect = QRectF(20, 20, size - 40, size - 40)
        painter.drawEllipse(inner_rect)
