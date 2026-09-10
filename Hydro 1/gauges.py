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
        self.yellow_start = None
        self.red_start = None
        self.warning_zone = False
        self.reverse_yellow_start = None
        self.reverse_red_start = None
        self.reverse_warning_zone = False

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

    def set_danger(self, yellow=None, red=None, reverse_yellow=None, reverse_red=None):
        if yellow is not None and red is not None:
            self.yellow_start = yellow
            self.red_start = red
            self.warning_zone = True

        if reverse_yellow is not None and reverse_red is not None:
            self.reverse_yellow_start = reverse_yellow
            self.reverse_red_start = reverse_red
            self.reverse_warning_zone = True

    # Draws the gauge
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.rect()
        side = min(rect.width(), rect.height())
        painter.translate(rect.center())
        painter.scale(side / 200.0, side / 200.0)

        # black bezel
        painter.setPen(QPen(QColor(20, 20, 20), 3))
        painter.setBrush(QColor(20, 20, 20))
        painter.drawEllipse(-94, -94, 188, 188)

        # white face
        painter.setPen(QPen(QColor(180, 180, 175), 1))
        painter.setBrush(QColor(240, 240, 235))
        painter.drawEllipse(-90, -90, 180, 180)
        
        if self.warning_zone:
            self.draw_warning_zones(painter, self.yellow_start, self.red_start)
        if self.reverse_warning_zone:
            self.draw_reverse_warning_zones(painter, self.reverse_yellow_start, self.reverse_red_start)

        # scale ticks - black
        painter.setPen(QPen(QColor(40, 40, 40), 1))
        # scale if not synchroscope
        if self.span_angle < 360:
            for i in range(0, 11):
                angle = self.start_angle + i * (self.span_angle / 10)
                painter.save()
                painter.rotate(angle)
                painter.drawLine(0, -80, 0, -88)
                painter.restore()
        else:
            painter.setPen(QPen(QColor(20, 120, 40), 3))
            painter.drawLine(0, -80, 0, -90) # sync marker

        # needle - black
        painter.save()
        ratio = (self.value - self.min_val) / (self.max_val - self.min_val)
        painter.rotate(self.start_angle + (ratio * self.span_angle))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(20, 20, 20))
        needle = QPolygonF([QPointF(-2, 0), QPointF(2, 0), QPointF(0, -75)])
        painter.drawPolygon(needle)
        painter.restore()

        # center cap
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(60, 60, 60))
        painter.drawEllipse(-5, -5, 10, 10)

        # text - black on white face
        painter.setPen(QColor(30, 30, 30))
        if self.span_angle < 360:
            painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            painter.drawText(-50, 40, 100, 20, Qt.AlignmentFlag.AlignCenter, f"{round(self.value, self.dp)} {self.unit}")
            painter.setFont(QFont("Arial", 8))
            painter.drawText(-50, 60, 100, 20, Qt.AlignmentFlag.AlignCenter, self.title)
        

    def draw_warning_zones(self, painter, yellow_start=None, red_start=None):
        """
        Draws yellow and red warning zones on the gauge.

        Parameters
        ----------
        yellow_start : float
            Value where the yellow zone begins.
        red_start : float
            Value where the red zone begins.
        """
        if yellow_start is None or red_start is None:
            return

        pen = QPen()
        pen.setWidth(8)
        pen.setCapStyle(Qt.PenCapStyle.FlatCap)

        radius = 85
        rect = (-radius, -radius, radius * 2, radius * 2)

        # Yellow zone
        yellow_angle = self.start_angle + (
            (yellow_start - self.min_val) / (self.max_val - self.min_val)
        ) * self.span_angle

        red_angle = self.start_angle + (
            (red_start - self.min_val) / (self.max_val - self.min_val)
        ) * self.span_angle

        pen.setColor(QColor("orange"))
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawArc(
            *rect,
            int((-yellow_angle + 90) * 16),
            int(-(red_angle - yellow_angle) * 16),
        )

        # Red zone
        pen.setColor(QColor("red"))
        painter.setPen(pen)
        painter.drawArc(
            *rect,
            int((-red_angle + 90) * 16),
            int(-(self.start_angle + self.span_angle - red_angle) * 16),
        )
    
    def draw_reverse_warning_zones(self, painter, yellow_end=None, red_end=None):
        """
        Draw warning zones for LOW values.

        red_end    : end of the red zone
        yellow_end : end of the yellow zone
        """
        if yellow_end is None or red_end is None:
            return

        pen = QPen()
        pen.setWidth(8)
        pen.setCapStyle(Qt.PenCapStyle.FlatCap)

        radius = 85
        rect = (-radius, -radius, radius * 2, radius * 2)

        red_angle = self.start_angle + (
            (red_end - self.min_val)
            / (self.max_val - self.min_val)
        ) * self.span_angle

        yellow_angle = self.start_angle + (
            (yellow_end - self.min_val)
            / (self.max_val - self.min_val)
        ) * self.span_angle

        painter.setBrush(Qt.BrushStyle.NoBrush)

        # Red zone (minimum -> red_end)
        pen.setColor(QColor("red"))
        painter.setPen(pen)
        painter.drawArc(
            *rect,
            int((-self.start_angle + 90) * 16),
            int(-(red_angle - self.start_angle) * 16),
        )

        # Yellow zone (red_end -> yellow_end)
        pen.setColor(QColor("orange"))
        painter.setPen(pen)
        painter.drawArc(
            *rect,
            int((-red_angle + 90) * 16),
            int(-(yellow_angle - red_angle) * 16),
        )

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
        
        # black bezel
        painter.setPen(QPen(QColor(20, 20, 20), 2))
        painter.setBrush(QColor(20, 20, 20))
        painter.drawRect(18, 38, w-36, h-76)

        # white face
        painter.setPen(QPen(QColor(180, 180, 175), 1))
        painter.setBrush(QColor(240, 240, 235))
        painter.drawRect(20, 40, w-40, h-80)

        # water fill
        fill_h = (self.level / 100.0) * (h - 80)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(self.color[0], self.color[1], self.color[2]))
        painter.drawRect(20, int(h - 40 - fill_h), w-40, int(fill_h))
        
        # text - black on white
        painter.setPen(QColor(30, 30, 30))
        painter.drawText(0, h-30, w, 20, Qt.AlignmentFlag.AlignCenter, f"{self.level:.1f}%")
        painter.drawText(0, 10, w, 20, Qt.AlignmentFlag.AlignCenter, self.title)
