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
        self.setFixedSize(1300, 600)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        main_layout.addWidget(QLabel("<h2>Turbine Panel</h2>", alignment=Qt.AlignmentFlag.AlignCenter))

        # --- Gauges ---
        gauge_layout = QHBoxLayout()
        self.turbine_level_gauge = LevelGauge("Turbine level")
        self.drain_gauge = LevelGauge("Drain", [255,0,100])
        self.bypass_gauge = LevelGauge("Bypasss", [255,0,100])
        self.rpm_gauge = UniversalGauge(title="RPM", unit="%", min_val=0, max_val=4000)
        self.excitation_guage = UniversalGauge(title="Excitation", unit="V", min_val=0, max_val=600)
        self.oil_temperature = UniversalGauge(title="Oil temp", unit="°", min_val=20, max_val=100, dp=2)
        self.pump = UniversalGauge(title="Pump", unit="%", min_val=0, max_val=100)
        self.exchanger = UniversalGauge(title="Exchanger valve", unit="%", min_val=0, max_val=100)
        gauge_layout.addWidget(self.turbine_level_gauge)
        gauge_layout.addWidget(self.drain_gauge)
        gauge_layout.addWidget(self.bypass_gauge)
        gauge_layout.addWidget(self.rpm_gauge)
        gauge_layout.addWidget(self.excitation_guage)
        gauge_layout.addWidget(self.oil_temperature)
        gauge_layout.addWidget(self.pump)
        gauge_layout.addWidget(self.exchanger)
        main_layout.addLayout(gauge_layout)
        main_layout.addWidget(self.create_separator())

        pid_layout = QVBoxLayout()
        self.Kp = CustomInputField(
                placeholder_text="p", 
                button_text="ENTER", 
                color="#0066cc", 
                callback=lambda val: self.Kp_change(val)
            )
        self.Ki = CustomInputField(
                placeholder_text="i", 
                button_text="ENTER", 
                color="#0066cc", 
                callback=lambda val: self.handle_variable_change(val)
            )
        self.Kd = CustomInputField(
                placeholder_text="d", 
                button_text="ENTER", 
                color="#0066cc", 
                callback=lambda val: self.handle_variable_change(val)
            )
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
        main_layout.addLayout()

    
    def Kp_change(self, val):
        self.engine.pid.Kp = val
        self.Kp.clear()
        self.Kp.set_placeholder(val)

    def Ki_change(self, val):
        self.engine.pid.Ki = val
        self.Ki.clear()
        self.Ki.set_placeholder(val)

    def Kd_change(self, val):
        self.engine.pid.Kd = val
        self.Ki.clear()
        self.Ki.set_placeholder(val)


    def create_separator(self):
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("background-color: #444;")
        return line
    
    def update_ui(self):
        self.rpm_gauge.set_value(self.engine.current_rpm)
        self.excitation_guage.set_value(self.engine.excitation)
        self.oil_temperature.set_value(self.engine.oil_temperature)
        self.pump.set_value(self.engine.oil_pump_power)
        self.exchanger.set_value(self.engine.heat_exc_flow)
        self.preheat_annunc.set_state(self.engine.oil_preheater)

        self.turbine_level_gauge.set_level(self.engine.turbine_water_level)
        self.bypass_gauge.set_level(self.engine.bypass_opening)
        self.drain_gauge.set_level(self.engine.drain_opening)


    
    def closeEvent(self, event):
        self.hide()
        event.ignore()