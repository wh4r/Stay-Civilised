from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QGridLayout,
    QSizePolicy,
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
        self.setStyleSheet("background-color: #808080; color: #222222;")

        # ================= MAIN LAYOUT =================
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)

        self.setLayout(main_layout)

        main_layout.addWidget(QLabel("<h2>Grid</h2>"))

        # ------------------------------------------------------------------
        # Top row: Total demand + total generation
        # ------------------------------------------------------------------
        top_row = QHBoxLayout()
        top_row.setSpacing(20)

        total_demand = QVBoxLayout()
        total_demand.addWidget(QLabel("<h4>Total Demand</h4>", alignment=Qt.AlignmentFlag.AlignCenter))
        self.current_demand = SevenSegmentDisplay(6)
        self.current_demand.set_number(8888)
        total_demand.addWidget(self.current_demand)
        top_row.addLayout(total_demand, 1)

        total_gen = QVBoxLayout()
        total_gen.addWidget(QLabel("<h4>Total Generation</h4>", alignment=Qt.AlignmentFlag.AlignCenter))
        self.total_generation = SevenSegmentDisplay(6)
        self.total_generation.set_number(0)
        total_gen.addWidget(self.total_generation)
        top_row.addLayout(total_gen, 1)

        main_layout.addLayout(top_row)
        main_layout.addWidget(self.create_separator())

        # ------------------------------------------------------------------
        # Remaining displays, two per row
        # ------------------------------------------------------------------
        def gen_row(d1_title, d1_key, d2_title, d2_key):
            row = QHBoxLayout()
            row.setSpacing(20)
            for title, key in ((d1_title, d1_key), (d2_title, d2_key)):
                col = QVBoxLayout()
                col.addWidget(QLabel(f"<h4>{title}</h4>", alignment=Qt.AlignmentFlag.AlignCenter))
                widget = SevenSegmentDisplay(6)
                widget.set_number(0)
                setattr(self, key, widget)
                col.addWidget(widget)
                row.addLayout(col, 1)
            main_layout.addLayout(row)

        gen_row("Hydroelectric", "hydro_prod", "Wind Generation", "wind_total")
        gen_row("Coal Unit 1", "coal_1", "Coal Unit 2", "coal_2")

        main_layout.addWidget(self.create_separator())





    # ==========================================================
    # SEPARATOR
    # ==========================================================

    def create_separator(self):
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("""
            background-color: #555;
            max-height: 1px;
        """)
        return line

    def create_vseparator(self):
            line = QFrame()
            line.setFrameShape(QFrame.Shape.VLine)
            line.setFrameShadow(QFrame.Shadow.Sunken)
            line.setStyleSheet("""
                background-color: #555;
                max-width: 1px;
            """)
            return line

    # ==========================================================
    # UPDATE UI
    # ==========================================================

    def update_ui(self):
        self.current_demand.set_number(self.engine.current_demand)
        self.total_generation.set_number(round(self.engine.total_generation, 1))
        self.hydro_prod.set_number(round(self.engine.power,1))
        self.wind_total.set_number(round(self.engine.wind_total_power, 1))
        self.coal_1.set_number(round(self.engine.coal_plants[0]['power'], 1))
        self.coal_2.set_number(round(self.engine.coal_plants[1]['power'], 1))

    # ==========================================================
    # CLOSE EVENT
    # ==========================================================

    def closeEvent(self, event):
        self.hide()
        event.ignore()