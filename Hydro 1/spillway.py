from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt
from buttons import CustomButton
from gauges import UniversalGauge, LevelGauge
from annunciators import Annunciator

class SpillwayWindow(QWidget):
    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        self.setWindowTitle("Spillway")
        self.setStyleSheet("background-color: #808080; color: #222222;")

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        main_layout.addWidget(QLabel("<h2>Spillway Panel</h2>", alignment=Qt.AlignmentFlag.AlignCenter))

        # --- 1 ---
        spill_1_layout = QHBoxLayout()
        self.spill_1_gauge = UniversalGauge(title="Spillway 1", unit="%", min_val=0, max_val = 100)
        self.spill_1_gauge.set_danger(70,90)
        self.spill_1_dec = CustomButton("-")
        self.spill_1_stop = CustomButton("x")
        self.spill_1_inc = CustomButton("+")
        spill_1_layout.addWidget(self.spill_1_gauge)
        spill_1_layout.addWidget(self.spill_1_dec)
        spill_1_layout.addWidget(self.spill_1_stop)
        spill_1_layout.addWidget(self.spill_1_inc)
        main_layout.addLayout(spill_1_layout)

        # --- 2 ---
        spill_2_layout = QHBoxLayout()
        self.spill_2_gauge = UniversalGauge(title="Spillway 1", unit="%", min_val=0, max_val = 100)    
        self.spill_2_gauge.set_danger(70,90) 
        self.spill_2_dec = CustomButton("-")
        self.spill_2_stop = CustomButton("x")
        self.spill_2_inc = CustomButton("+")
        spill_2_layout.addWidget(self.spill_2_gauge)
        spill_2_layout.addWidget(self.spill_2_dec)
        spill_2_layout.addWidget(self.spill_2_stop)
        spill_2_layout.addWidget(self.spill_2_inc)
        main_layout.addLayout(spill_2_layout)


        # --- Functions ---
        self.spill_1_inc.clicked.connect(lambda: setattr(self.engine, 'spill_open_1', 0.1))
        self.spill_1_stop.clicked.connect(lambda: setattr(self.engine, 'spill_open_1', 0))
        self.spill_1_dec.clicked.connect(lambda: setattr(self.engine, 'spill_open_1', -0.1))
        self.spill_2_inc.clicked.connect(lambda: setattr(self.engine, 'spill_open_2', 0.1))
        self.spill_2_stop.clicked.connect(lambda: setattr(self.engine, 'spill_open_2', 0))
        self.spill_2_dec.clicked.connect(lambda: setattr(self.engine, 'spill_open_2', -0.1))

    def update_ui(self):
        self.spill_1_gauge.set_value(self.engine.spill_1)
        self.spill_2_gauge.set_value(self.engine.spill_2)


    
    def closeEvent(self, event):
        self.hide()
        event.ignore()