from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QGridLayout,
    QSizePolicy
)
import math

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

from buttons import CustomButton
from annunciators import Annunciator
from gauges import UniversalGauge
from numerical_display import SevenSegmentDisplay

class GridWindow(QWidget):

    def __init__(self, engine):
        super().__init__()

        self.engine = engine

        self.setWindowTitle("Breaker Panel")
        self.setStyleSheet("background-color: #121212; color: white;")

        # ================= MAIN LAYOUT =================
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)

        self.setLayout(main_layout)

        main_layout.addWidget(QLabel("<h2>Grid</h2>"))

        generation_layout = QHBoxLayout()

        current_demand = QVBoxLayout()
        current_demand.addWidget(QLabel("<h4>Current Demand</h4>"))
        self.current_demand = SevenSegmentDisplay(6)
        self.current_demand.set_number(8888)
        current_demand.addWidget(self.current_demand)
        generation_layout.addLayout(current_demand)

        generation_layout.addWidget(self.create_vseparator())

        hydro_prod = QVBoxLayout()
        hydro_prod.addWidget(QLabel("<h4>Hydroelectric Production</h4>"))
        self.hydro_prod = SevenSegmentDisplay(3)
        self.hydro_prod.set_number(000)
        hydro_prod.addWidget(self.hydro_prod)
        generation_layout.addLayout(hydro_prod)

        main_layout.addLayout(generation_layout)

        main_layout.addWidget(self.create_separator())





    # ==========================================================
    # SEPARATOR
    # ==========================================================

    def create_separator(self):
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("""
            background-color: #2a2a2a;
            max-height: 1px;
        """)
        return line

    def create_vseparator(self):
            line = QFrame()
            line.setFrameShape(QFrame.Shape.VLine)
            line.setFrameShadow(QFrame.Shadow.Sunken)
            line.setStyleSheet("""
                background-color: #2a2a2a;
                max-width: 1px;
            """)
            return line

    # ==========================================================
    # UPDATE UI
    # ==========================================================

    def update_ui(self):
        self.current_demand.set_number(self.engine.current_demand)
        self.hydro_prod.set_number(math.floor(self.engine.power))

    # ==========================================================
    # CLOSE EVENT
    # ==========================================================

    def closeEvent(self, event):
        self.hide()
        event.ignore()