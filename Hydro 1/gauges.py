from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QPen, QPolygonF, QFont
from PyQt6.QtCore import Qt, QPointF

class UniversalGauge(QWidget):
    def __init__(self, title="", min_val=0, max_val=100, unit="", parent=None, dp=1):
        super().__init__(parent)
        self.setMinimumSize(200, 200)
        self.value = 0
        self.configure(min_val, max_val, unit, title)
        self.needle_color = QColor(255, 0, 0)
        self.start_angle = 240  # start position
        self.span_angle = 240   # arc length
        self.dp=dp

    # Changes the values of the gauge
    def configure(self, min_val, max_val, unit, title, start_angle=240, span_angle=240, needle_color="red"):
        self.min_val = min_val
        self.max_val = max_val
        self.unit = unit
        self.title = title
        self.start_angle = start_angle
        self.span_angle = span_angle
        self.needle_color = QColor(needle_color)
        self.update()

    #Sets the value to be displated
    def set_value(self, val):
        self.value = max(self.min_val, min(self.max_val, val))
        self.update()

    # Draws the gauge
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.rect()
        side = min(rect.width(), rect.height())
        painter.translate(rect.center())
        painter.scale(side / 200.0, side / 200.0)

        # face
        painter.setPen(QPen(Qt.GlobalColor.white, 2))
        painter.setBrush(QColor(30, 30, 30))
        painter.drawEllipse(-90, -90, 180, 180)

        # scale
        painter.setPen(QPen(Qt.GlobalColor.white, 1))
        # scale if not synchroscope
        if self.span_angle < 360:
            for i in range(0, 11):
                angle = self.start_angle + i * (self.span_angle / 10)
                painter.save()
                painter.rotate(angle)
                painter.drawLine(0, -80, 0, -88)
                painter.restore()
        else:
            painter.setPen(QPen(Qt.GlobalColor.green, 3))
            painter.drawLine(0, -80, 0, -90) # sync marker

        # needle
        painter.save()
        ratio = (self.value - self.min_val) / (self.max_val - self.min_val)
        painter.rotate(self.start_angle + (ratio * self.span_angle))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.needle_color)
        needle = QPolygonF([QPointF(-2, 0), QPointF(2, 0), QPointF(0, -75)])
        painter.drawPolygon(needle)
        painter.restore()

        # text
        painter.setPen(Qt.GlobalColor.white)
        if self.span_angle < 360:
            painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            painter.drawText(-50, 40, 100, 20, Qt.AlignmentFlag.AlignCenter, f"{round(self.value, self.dp)} {self.unit}")
            painter.setFont(QFont("Arial", 8))
            painter.drawText(-50, 60, 100, 20, Qt.AlignmentFlag.AlignCenter, self.title)

class LevelGauge(QWidget):
    # Special vertical gauge for the water level display
    def __init__(self, title, color = [0,120,255], parent=None):
        super().__init__(parent)
        self.setMinimumWidth(80)
        self.color = color
        self.level = 50.0  # percentage
        self.title = title

    def set_level(self, level):
        self.level = max(0, min(100, level))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        w, h = self.width(), self.height()
        
        # frame
        painter.setBrush(QColor(50, 50, 50))
        painter.drawRect(20, 40, w-40, h-80)

        # water
        fill_h = (self.level / 100.0) * (h - 80)
        painter.setBrush(QColor(self.color[0], self.color[1], self.color[2]))
        painter.drawRect(20, int(h - 40 - fill_h), w-40, int(fill_h))
        
        # text
        painter.setPen(Qt.GlobalColor.white)
        painter.drawText(0, h-30, w, 20, Qt.AlignmentFlag.AlignCenter, f"{self.level:.1f}%")
        painter.drawText(0, 10, w, 20, Qt.AlignmentFlag.AlignCenter, self.title)
