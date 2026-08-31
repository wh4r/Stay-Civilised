from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QGridLayout,
    QScrollArea,
)
from PyQt6.QtCore import Qt

from buttons import CustomButton
from numerical_display import SevenSegmentDisplay
import math


class WindFarmWindow(QWidget):
    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        self.setWindowTitle("Wind Farm — 50 × 10 MW")
        self.setStyleSheet("background-color: #121212; color: white;")
        self.resize(980, 520)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        self.setLayout(main_layout)

        main_layout.addWidget(QLabel("<h2>Wind Farm — 50 × 10 MW</h2>"))

        wind_header = QHBoxLayout()
        wind_header.addWidget(QLabel("<b>Wind Speed:</b>"))
        self.wind_speed_display = SevenSegmentDisplay(4)
        self.wind_speed_display.set_number(0)
        wind_header.addWidget(self.wind_speed_display)
        wind_header.addWidget(QLabel("m/s"))
        wind_header.addStretch()
        wind_header.addWidget(QLabel("<b>Total Wind:</b>"))
        self.wind_total_display = SevenSegmentDisplay(6)
        self.wind_total_display.set_number(0)
        wind_header.addWidget(self.wind_total_display)
        wind_header.addWidget(QLabel("MW"))
        main_layout.addLayout(wind_header)

        main_layout.addWidget(self.create_separator())

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFixedHeight(420)
        scroll.setStyleSheet("QScrollArea { border: 1px solid #333; background-color: #1a1a1a; }")
        scroll_container = QWidget()
        scroll_container.setStyleSheet("background-color: #1a1a1a;")
        self.wind_grid = QGridLayout(scroll_container)
        self.wind_grid.setSpacing(6)
        self.wind_grid.setContentsMargins(6, 6, 6, 6)

        self.wind_buttons = []
        self.wind_displays = []
        for idx in range(50):
            card = QFrame()
            card.setStyleSheet("""
                QFrame {
                    background-color: #1e1e1e;
                    border: 1px solid #333;
                    border-radius: 4px;
                }
            """)
            v = QVBoxLayout(card)
            v.setContentsMargins(4, 4, 4, 4)
            v.setSpacing(3)
            v.addWidget(QLabel(f"<b>W{idx+1:02d}</b>", alignment=Qt.AlignmentFlag.AlignCenter))

            btn = CustomButton("OFF", color="#444")
            btn.setFixedHeight(26)
            btn.clicked.connect(lambda checked, i=idx: self.handle_wind_toggle(i))
            v.addWidget(btn)
            self.wind_buttons.append(btn)

            disp = SevenSegmentDisplay(4, 8)
            disp.setFixedHeight(36)
            disp.setMinimumWidth(80)
            disp.set_number(0)
            v.addWidget(disp)
            self.wind_displays.append(disp)

            row = idx // 10
            col = idx % 10
            self.wind_grid.addWidget(card, row, col)

        scroll.setWidget(scroll_container)
        main_layout.addWidget(scroll)

    def create_separator(self):
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("background-color: #2a2a2a; max-height: 1px;")
        return line

    def handle_wind_toggle(self, idx):
        self.engine.wind_turbine_toggle(idx)
        self.update_ui()

    def update_ui(self):
        self.wind_speed_display.set_number(round(self.engine.wind_speed, 1))
        self.wind_total_display.set_number(round(self.engine.wind_total_power, 1))
        for idx in range(50):
            state = self.engine.wind_turbines_state[idx]
            power = self.engine.wind_turbines_power[idx]
            timer = self.engine.wind_turbines_timer[idx]
            btn = self.wind_buttons[idx]
            disp = self.wind_displays[idx]
            if state == 1:
                disp.set_number(int(math.ceil(timer)))
            elif state == 3:
                disp.set_number(round(power, 1))
            else:
                disp.set_number(round(power, 1))
            if state == 1 or state == 3:
                flashing_on = self.engine.wind_flash
                bg = "#ffaa00" if flashing_on else "#332200"
                border = "#ffcc33" if flashing_on else "#664400"
                text = "STARTING" if state == 1 else "STOPPING"
                btn.setText(text)
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {bg};
                        color: white;
                        border: 1px solid {border};
                        border-radius: 3px;
                        padding: 4px;
                        font-weight: bold;
                        font-size: 8px;
                    }}
                """)
            elif state == 2:
                btn.setText("ON")
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #006633;
                        color: white;
                        border: 1px solid #008844;
                        border-radius: 3px;
                        padding: 4px;
                        font-weight: bold;
                        font-size: 9px;
                    }
                    QPushButton:hover { border: 1px solid #33cc66; }
                    QPushButton:pressed { background-color: #003311; }
                """)
            else:
                btn.setText("OFF")
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #444;
                        color: white;
                        border: 1px solid #666;
                        border-radius: 3px;
                        padding: 4px;
                        font-weight: bold;
                        font-size: 9px;
                    }
                    QPushButton:hover { border: 1px solid #999; }
                    QPushButton:pressed { background-color: #222; }
                """)

    def closeEvent(self, event):
        self.hide()
        event.ignore()
