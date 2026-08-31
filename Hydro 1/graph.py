from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QPolygonF
from PyQt6.QtCore import Qt, QPointF


class GraphWidget(QWidget):
    """A lightweight, self-contained line graph drawn with QPainter.

    Plots a 1D array of values along the x-axis (index 0 on the left, most
    recent point on the right). The y-axis auto-scales to the data unless a
    fixed (min_y, max_y) range is supplied.

    Example:
        graph = GraphWidget("Demand", "kW", max_points=60)
        graph.set_data([1000, 1010, 990, ...])
    """

    def __init__(self, title="", unit="", min_y=None, max_y=None, max_points=60,
                 color="#00ff9c", parent=None):
        super().__init__(parent)
        self.setMinimumSize(260, 160)

        self.title = title
        self.unit = unit
        self.min_y = min_y
        self.max_y = max_y
        self.max_points = max_points
        self.color = QColor(color)

        self.data = []

        self.pad_left = 46
        self.pad_right = 14
        self.pad_top = 26
        self.pad_bottom = 22

    # ------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------

    def set_title(self, title):
        self.title = title
        self.update()

    def set_color(self, color):
        self.color = QColor(color)
        self.update()

    def set_range(self, min_y, max_y):
        self.min_y = min_y
        self.max_y = max_y
        self.update()

    def set_data(self, data):
        """Replace the plotted array with a new iterable of values."""
        vals = list(data)
        if len(vals) > self.max_points:
            vals = vals[-self.max_points:]
        self.data = vals
        self.update()

    def append(self, value):
        """Append a single sample, dropping the oldest once past max_points."""
        self.data.append(value)
        if len(self.data) > self.max_points:
            self.data.pop(0)
        self.update()

    def clear(self):
        self.data = []
        self.update()

    # ------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------

    @property
    def plot_rect(self):
        r = self.rect()
        return r.adjusted(self.pad_left, self.pad_top, -self.pad_right, -self.pad_bottom)

    def _y_bounds(self):
        if self.min_y is not None and self.max_y is not None:
            return self.min_y, self.max_y
        if not self.data:
            return 0.0, 1.0
        lo, hi = min(self.data), max(self.data)
        if lo == hi:  # flat line - give it some vertical room
            if lo > 0:
                lo = 0
            else:
                hi = 1
        span = hi - lo
        if span < 40:
            mid = (lo + hi) / 2
            lo = mid - 20
            hi = mid + 20
            span = 40
        margin = span * 0.35 if span != 0 else 0.5
        return lo - margin, hi + margin

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        painter.fillRect(self.rect(), QColor(18, 18, 18))

        # Title
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        painter.drawText(
            self.rect().adjusted(0, 0, 0, -self.rect().height() + self.pad_top),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            self.title,
        )

        plot = self.plot_rect
        lo, hi = self._y_bounds()

        painter.setPen(QPen(QColor(60, 60, 60), 1))
        for i in range(5):
            y = plot.top() + plot.height() * i / 4
            painter.drawLine(int(plot.left()), int(y), int(plot.right()), int(y))

        # Y-axis labels (nice rounded ticks)
        painter.setFont(QFont("Segoe UI", 8))
        painter.setPen(QColor(200, 200, 200))
        for i in range(5):
            frac = i / 4
            y = plot.top() + plot.height() * frac
            value = hi - (hi - lo) * frac
            label = f"{value:.1f}"
            painter.drawText(
                int(plot.left() - self.pad_left + 4),
                int(y + 8),
                int(self.pad_left - 8),
                14,
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                label,
            )

        # Plot line
        if len(self.data) >= 1:
            if len(self.data) >= 2:
                n = len(self.data)
                poly = QPolygonF()
                for idx, value in enumerate(self.data):
                    x = plot.left() + plot.width() * (idx / (n - 1))
                    frac = (value - lo) / (hi - lo) if hi != lo else 0.0
                    y = plot.bottom() - plot.height() * frac
                    poly.append(QPointF(x, y))
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.setPen(QPen(self.color, 2))
                painter.drawPolyline(poly)
                last = poly.last()
            else:
                value = self.data[0]
                x = plot.right()
                frac = (value - lo) / (hi - lo) if hi != lo else 0.0
                y = plot.bottom() - plot.height() * frac
                last = QPointF(x, y)

            # Last-point marker
            painter.setBrush(self.color)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(last, 3, 3)

        # Axes frame
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor(160, 160, 160), 1))
        painter.drawRect(plot)

        # Unit under title
        if self.unit:
            painter.setPen(QColor(140, 140, 140))
            painter.setFont(QFont("Segoe UI", 8))
            painter.drawText(
                plot.right() - painter.fontMetrics().horizontalAdvance(self.unit) - 2,
                self.pad_top - 8,
                self.unit,
            )
