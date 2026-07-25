from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt
from buttons import CustomButton
from gauges import UniversalGauge, LevelGauge
from annunciators import Annunciator
from input import CustomInputField

class TurbineAutoWindow(QWidget):
    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        self.setWindowTitle("Automatic Turbine Control")
        self.setStyleSheet("background-color: #1a1a1a; color: white;")

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        main_layout.addWidget(QLabel("<h2>Automatic Turbine Control</h2>", alignment=Qt.AlignmentFlag.AlignCenter))

        # --- Annunciators ---
        annunc_layout = QHBoxLayout()
        self.active = Annunciator("AUTO ACTIVE", "green", False)
        self.high_accel = Annunciator("HIGH ACCEL.", persistent=False)
        annunc_layout.addWidget(self.active)
        annunc_layout.addWidget(self.high_accel)
        main_layout.addLayout(annunc_layout)

        # --- Gauges ---
        gauge_layout = QHBoxLayout()
        self.rpm_gauge = UniversalGauge(title="Turbine RPM", unit="RPM", min_val=0, max_val=700)
        self.oil_temperature = UniversalGauge(title="Oil temp.", unit="°", min_val=20, max_val=100, dp=2)
        gauge_layout.addWidget(self.rpm_gauge)
        gauge_layout.addWidget(self.oil_temperature)
        main_layout.addLayout(gauge_layout)
        main_layout.addWidget(self.create_separator())

        pid_layout = QVBoxLayout()
        self.setpoint = CustomInputField(
            placeholder_text="setpoint", 
            button_text="SET", 
            color="#0066cc", 
            callback=lambda val: self.setpoint_change(val)
        )
        self.speed = CustomInputField(
            placeholder_text="0.2", 
            button_text="SET", 
            color="#0066cc", 
            callback=lambda val: self.speed_change(val)
        )
        self.Kp = CustomInputField(
            placeholder_text="p", 
            button_text="SET", 
            color="#0066cc", 
            callback=lambda val: self.Kp_change(val)
        )
        self.Ki = CustomInputField(
            placeholder_text="i", 
            button_text="SET", 
            color="#0066cc", 
            callback=lambda val: self.Ki_change(val)
        )
        self.Kd = CustomInputField(
            placeholder_text="d", 
            button_text="SET", 
            color="#0066cc", 
            callback=lambda val: self.Kd_change(val)
        )
        
        # Set initial placeholders from engine's PID values
        self.setpoint.set_placeholder(str(self.engine.pid.setpoint))
        self.Kp.set_placeholder(str(self.engine.pid.Kp))
        self.Ki.set_placeholder(str(self.engine.pid.Ki))
        self.Kd.set_placeholder(str(self.engine.pid.Kd))

        pid_layout.addWidget(QLabel("<b>Setpoint (RPM)</b>"))
        pid_layout.addWidget(self.setpoint)
        pid_layout.addWidget(QLabel("<b>Speed (gate%/s)</b>"))
        pid_layout.addWidget(self.speed)
        pid_layout.addWidget(QLabel("<b>p</b>"))
        pid_layout.addWidget(self.Kp)
        pid_layout.addWidget(QLabel("<b>i</b>"))
        pid_layout.addWidget(self.Ki)
        pid_layout.addWidget(QLabel("<b>d</b>"))
        pid_layout.addWidget(self.Kd)
        main_layout.addLayout(pid_layout)

        toggle_layout = QHBoxLayout()
        self.start = CustomButton("START", "green")
        self.stop = CustomButton("STOP", "red")
        toggle_layout.addWidget(self.start)
        toggle_layout.addWidget(self.stop)
        main_layout.addLayout(toggle_layout)

        self.start.clicked.connect(lambda: setattr(self.engine, 'auto_state', True))
        self.stop.clicked.connect(lambda: setattr(self.engine, 'auto_state', False))

    
    def setpoint_change(self, val):
        try:
            self.engine.pid.setpoint = float(val)
            self.setpoint.clear()
            self.setpoint.set_placeholder(val)
        except Exception:
            pass

    def speed_change(self, val):
        try:
            self.engine.auto_speed = (float(val)/10)
            self.speed.clear()
            self.speed.set_placeholder(val)
        except Exception:
            pass

    def Kp_change(self, val):
        try:
            self.engine.pid.Kp = float(val)
            self.Kp.clear()
            self.Kp.set_placeholder(val)
        except Exception:
            pass

    def Ki_change(self, val):
        try:
            self.engine.pid.Ki = float(val)
            self.Ki.clear()
            self.Ki.set_placeholder(val)
        except Exception:
            pass

    def Kd_change(self, val):
        try:
            self.engine.pid.Kd = float(val)
            self.Kd.clear()
            self.Kd.set_placeholder(val)
        except Exception:
            pass

    def create_separator(self):
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("background-color: #444;")
        return line
    
    def update_ui(self):
        self.rpm_gauge.set_value(self.engine.current_rpm)
        self.oil_temperature.set_value(self.engine.oil_temperature)
        self.active.set_state(self.engine.auto_state)


    
    def closeEvent(self, event):
        self.hide()
        event.ignore()