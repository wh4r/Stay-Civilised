from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt, QTimer
from buttons import CustomButton
from gauges import UniversalGauge
from annunciators import Annunciator

class HydraulicsWindow(QWidget):
    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        self.setWindowTitle("Hydraulic Systems")
        self.setStyleSheet("background-color: #1a1a1a; color: white;")
        self.setFixedSize(500, 700)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        main_layout.addWidget(QLabel("<h2>Hydraulics Panel</h2>", alignment=Qt.AlignmentFlag.AlignCenter))

        # --- Gauges ---
        gauge_layout = QHBoxLayout()
        self.res_gauge_1 = UniversalGauge(title="Reservoir 1 pressure", unit="%") # Replace with actual values using multiplier
        self.res_gauge_2 = UniversalGauge(title="Reserboir 2 pressure", unit="%")
        self.res_temp_1 = UniversalGauge(title="Reservoir 1 temp", unit="°", min_val=20, max_val=50)
        self.res_temp_1 = UniversalGauge(title="Reservoir 1 temp", unit="°", min_val=20, max_val=50)
        gauge_layout.addWidget(self.res_gauge_1)
        gauge_layout.addWidget(self.res_gauge_2)
        main_layout.addLayout(gauge_layout)
        main_layout.addWidget(self.create_separator())


        # --- Pumps Section ---
        pump_group = QVBoxLayout()
        pump_group.addWidget(QLabel("<b>PUMPS</b>"))
        
        # Pump 1
        p1_layout = QHBoxLayout()
        self.status_p1 = Annunciator("PUMP 1", "red", persistent=False)
        self.btn_p1_start = CustomButton("START")
        self.btn_p1_stop = CustomButton("STOP")
        p1_layout.addWidget(self.status_p1)
        p1_layout.addWidget(self.btn_p1_start)
        p1_layout.addWidget(self.btn_p1_stop)
        pump_group.addLayout(p1_layout)

        # Pump 2
        p2_layout = QHBoxLayout()
        self.status_p2 = Annunciator("PUMP 2", "red", persistent=False)
        self.btn_p2_start = CustomButton("START")
        self.btn_p2_stop = CustomButton("STOP")
        p2_layout.addWidget(self.status_p2)
        p2_layout.addWidget(self.btn_p2_start)
        p2_layout.addWidget(self.btn_p2_stop)
        pump_group.addLayout(p2_layout)


        # Pump Selector
        sel_layout = QHBoxLayout()
        sel_layout.addWidget(QLabel("Res. Selector:"))
        self.btn_sel_1 = CustomButton("P1")
        self.btn_sel_2 = CustomButton("P2")
        self.btn_sel_auto = CustomButton("AUTO")
        self.btn_sel_1.setFixedWidth(50)
        self.btn_sel_2.setFixedWidth(50)
        self.btn_sel_auto.setFixedWidth(60)
        sel_layout.addWidget(self.btn_sel_1)
        sel_layout.addWidget(self.btn_sel_2)
        sel_layout.addWidget(self.btn_sel_auto)
        sel_layout.addWidget(QLabel("AUTO UNAVAIL."))
        sel_layout.addStretch()
        pump_group.addLayout(sel_layout)
        
        main_layout.addLayout(pump_group)
        main_layout.addWidget(self.create_separator())

        # --- Fans Section ---
        fan_group = QVBoxLayout()
        fan_group.addWidget(QLabel("<b>FANS</b>"))
        # Fan 1
        f1_layout = QHBoxLayout()
        self.status_f1 = Annunciator("FAN 1", "green", persistent=False)
        self.btn_f1_start = CustomButton("START")
        self.btn_f1_stop = CustomButton("STOP")
        f1_layout.addWidget(self.status_f1)
        f1_layout.addWidget(self.btn_f1_start)
        f1_layout.addWidget(self.btn_f1_stop)
        fan_group.addLayout(f1_layout)

        # Fan 2
        f2_layout = QHBoxLayout()
        self.status_f2 = Annunciator("FAN 2", "green", persistent=False)
        self.btn_f2_start = CustomButton("START")
        self.btn_f2_stop = CustomButton("STOP")
        f2_layout.addWidget(self.status_f2)
        f2_layout.addWidget(self.btn_f2_start)
        f2_layout.addWidget(self.btn_f2_stop)
        fan_group.addLayout(f2_layout)
        main_layout.addLayout(fan_group)
        main_layout.addWidget(self.create_separator())

        # --- Preheaters Section ---
        pre_group = QVBoxLayout()
        pre_group.addWidget(QLabel("<b>PREHEATERS</b>"))
        pr_layout = QHBoxLayout()
        self.status_pr1 = Annunciator("PRE 1", "orange", persistent=False)
        self.status_pr2 = Annunciator("PRE 2", "orange", persistent=False)
        self.btn_pr1_toggle = CustomButton("P1 ON/OFF")
        self.btn_pr2_toggle = CustomButton("P2 ON/OFF")
        pr_layout.addWidget(self.status_pr1)
        pr_layout.addWidget(self.status_pr2)
        pr_layout.addWidget(self.btn_pr1_toggle)
        pr_layout.addWidget(self.btn_pr2_toggle)
        pre_group.addLayout(pr_layout)
        main_layout.addLayout(pre_group)

        # --- Connections ---
        self.btn_p1_start.clicked.connect(lambda: self.engine.start_pump(1))
        self.btn_p1_stop.clicked.connect(lambda: self.engine.stop_pump(1))
        self.btn_p2_start.clicked.connect(lambda: self.engine.start_pump(2))
        self.btn_p2_stop.clicked.connect(lambda: self.engine.stop_pump(2))
        
        self.btn_sel_1.clicked.connect(lambda: setattr(self.engine, 'pump_selector', 1))
        self.btn_sel_2.clicked.connect(lambda: setattr(self.engine, 'pump_selector', 2))
        self.btn_sel_auto.clicked.connect(lambda: setattr(self.engine, 'pump_selector', 0))

        self.btn_f1_start.clicked.connect(lambda: self.engine.start_fan(1))
        self.btn_f1_stop.clicked.connect(lambda: self.engine.stop_fan(1))
        self.btn_f2_start.clicked.connect(lambda: self.engine.start_fan(2))
        self.btn_f2_stop.clicked.connect(lambda: self.engine.stop_fan(2))
        self.btn_pr1_toggle.clicked.connect(self.toggle_pre1)
        self.btn_pr2_toggle.clicked.connect(self.toggle_pre2)

        # Update and Blink Timers
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_ui)
        self.timer.start(100)

        self.blink_timer = QTimer()
        self.blink_timer.timeout.connect(self.blink_tick)
        self.blink_timer.start(500)

    def create_separator(self):
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("background-color: #444;")
        return line

    def toggle_pre1(self): self.engine.pre1_on = not self.engine.pre1_on
    def toggle_pre2(self): self.engine.pre2_on = not self.engine.pre2_on

    def blink_tick(self):
        if self.engine.pump1_state == 1:
            self.status_p1.toggle_blink()
        if self.engine.pump2_state == 1:
            self.status_p2.toggle_blink()
        if self.engine.fan1_state == 1:
            self.status_f1.toggle_blink()
        if self.engine.fan2_state == 1:
            self.status_f2.toggle_blink()

    def update_ui(self):
        # Pump 1 status
        if self.engine.pump1_state == 0:
            self.status_p1.set_state(False)
        elif self.engine.pump1_state == 1:
            self.status_p1.set_state(True)
        elif self.engine.pump1_state == 2:
            self.status_p1.set_state(True)
            self.status_p1.blink = True
            self.status_p1.update_style()

        # Pump 2 status
        if self.engine.pump2_state == 0:
            self.status_p2.set_state(False)
        elif self.engine.pump2_state == 1:
            self.status_p2.set_state(True)
        elif self.engine.pump2_state == 2:
            self.status_p2.set_state(True)
            self.status_p2.blink = True
            self.status_p2.update_style()

        # Selector styling
        self.btn_sel_1.setStyleSheet("background-color: #444;" if self.engine.pump_selector != 1 else "background-color: #0066cc;")
        self.btn_sel_2.setStyleSheet("background-color: #444;" if self.engine.pump_selector != 2 else "background-color: #0066cc;")
        self.btn_sel_auto.setStyleSheet("background-color: #444;" if self.engine.pump_selector != 2 else "background-color: #0066cc;")

        # Fan 1 status
        if self.engine.fan1_state == 0:
            self.status_f1.set_state(False)
        elif self.engine.fan1_state == 1:
            self.status_f1.set_state(True)
        elif self.engine.fan1_state == 2:
            self.status_f1.set_state(True)
            self.status_f1.blink = True
            self.status_f1.update_style()

        # Fan 2 status
        if self.engine.fan2_state == 0:
            self.status_f2.set_state(False)
        elif self.engine.fan2_state == 1:
            self.status_f2.set_state(True)
        elif self.engine.fan2_state == 2:
            self.status_f2.set_state(True)
            self.status_f2.blink = True
            self.status_f2.update_style()

        # Selector styling
        self.btn_sel_1.setStyleSheet("background-color: #444;" if self.engine.pump_selector != 1 else "background-color: #0066cc;")
        self.btn_sel_2.setStyleSheet("background-color: #444;" if self.engine.pump_selector != 2 else "background-color: #0066cc;")
        self.btn_sel_auto.setStyleSheet("background-color: #444;" if self.engine.pump_selector != 2 else "background-color: #0066cc;")

        # Preheaters
        self.status_pr1.set_state(self.engine.pre1_on)
        self.status_pr2.set_state(self.engine.pre2_on)
    
    def closeEvent(self, event):
        self.hide()
        event.ignore()
