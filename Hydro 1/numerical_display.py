from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtCore import Qt, QPointF

SEGMENTS = {
    '0': (1, 1, 1, 0, 1, 1, 1), '1': (0, 0, 1, 0, 0, 1, 0),
    '2': (1, 0, 1, 1, 1, 0, 1), '3': (1, 0, 1, 1, 0, 1, 1),
    '4': (0, 1, 1, 1, 0, 1, 0), '5': (1, 1, 0, 1, 0, 1, 1),
    '6': (1, 1, 0, 1, 1, 1, 1), '7': (1, 0, 1, 0, 0, 1, 0),
    '8': (1, 1, 1, 1, 1, 1, 1), '9': (1, 1, 1, 1, 0, 1, 1),
    ' ': (0, 0, 0, 0, 0, 0, 0), '-': (0, 0, 0, 1, 0, 0, 0),
    'E': (1, 1, 0, 1, 1, 0, 1), 'F': (1, 1, 0, 1, 1, 0, 0),
}
SEG_ORDER = ['a', 'f', 'b', 'g', 'e', 'c', 'd']

ON_COLOR = QColor("#ff2200")
OFF_COLOR = QColor("#1a0500")

POLYS = {
    'a': [QPointF(-3, -9.5), QPointF(3, -9.5), QPointF(2, -7.5), QPointF(-2, -7.5)],
    'b': [QPointF(3, -8.5), QPointF(5, -7), QPointF(4.5, -1), QPointF(2.5, -2.5)],
    'c': [QPointF(2.5, 1), QPointF(4.5, 0.5), QPointF(5, 7.5), QPointF(3, 9.5)],
    'd': [QPointF(-3, 7.5), QPointF(3, 7.5), QPointF(4, 9.5), QPointF(-4, 9.5)],
    'e': [QPointF(-2.5, 1), QPointF(-4.5, 0.5), QPointF(-5, 7.5), QPointF(-3, 9.5)],
    'f': [QPointF(-5, -7), QPointF(-3, -8.5), QPointF(-2.5, -2.5), QPointF(-4.5, -1)],
    'g': [QPointF(-3, -1.5), QPointF(-2, -2.5), QPointF(2, -2.5), QPointF(3, -1.5), QPointF(2, 0.5), QPointF(-2, 0.5)],
}


class SevenSegmentDisplay(QWidget):
    def __init__(self, length=4, decimal_offset=17,parent=None):
        self.decimal_offset = decimal_offset
        super().__init__(parent)
        self.length = length
        self.digits = [' '] * length
        self.dps = [False] * length
        self.setMinimumHeight(60)
        self.setMinimumWidth(length * 70 + 10)

    def set_number(self, value):
        if isinstance(value, str):
            text = value.strip()
        else:
            text = str(value)

        dp_pos = -1
        if '.' in text:
            dp_pos = text.index('.')

        clean = text.replace('.', '')

        if len(clean) > self.length and not isinstance(value, str):
            try:
                num = float(value)
                for decimals in range(6, -1, -1):
                    text = str(round(num, decimals))
                    dp_pos = text.index('.') if '.' in text else -1
                    clean = text.replace('.', '')
                    if len(clean) <= self.length:
                        break
            except (ValueError, OverflowError):
                pass

        if len(clean) > self.length:
            clean = clean[-self.length:]
            dp_pos = -1

        self.digits = list(clean.rjust(self.length, ' '))
        self.dps = [False] * self.length

        if dp_pos >= 0:
            start = self.length - len(clean)
            dp_char_idx = start + dp_pos - 1
            if 0 <= dp_char_idx < self.length:
                self.dps[dp_char_idx] = True

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.rect().width()
        h = self.rect().height()
        digit_w = w / self.length

        # dark background for LED display
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#1a0500"))
        painter.drawRoundedRect(self.rect().adjusted(2, 2, -2, -2), 3, 3)

        for i, char in enumerate(self.digits):
            cx = i * digit_w + digit_w * 0.5
            cy = h * 0.5
            scale = min(digit_w / 14, h / 24) * 0.85

            pattern = SEGMENTS.get(char.upper(), SEGMENTS[' '])

            painter.save()
            painter.translate(cx, cy)
            painter.scale(scale, scale)

            for idx, seg in enumerate(SEG_ORDER):
                color = ON_COLOR if pattern[idx] else OFF_COLOR
                painter.setBrush(color)
                painter.drawPolygon(POLYS[seg])

            if self.dps[i]:
                painter.setBrush(ON_COLOR)
                painter.drawEllipse(QPointF(self.decimal_offset, 9.5), 1.0, 1.0)

            painter.restore()
