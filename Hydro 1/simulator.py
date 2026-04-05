import sys
import math
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QGridLayout, QLabel, QFrame, QPushButton)
from PyQt6.QtGui import QPainter, QColor, QPen, QPolygonF, QFont
from PyQt6.QtCore import Qt, QPointF, QTimer
import random

class UniversalGauge(QWidget):
    def __init__(self, title="", min_val=0, max_val=100, unit="", parent=None):
        super().__init__(parent)
        self.setMinimumSize(200, 200)
        self.value = 0
        self.configure(min_val, max_val, unit, title)
        self.needle_color = QColor(255, 0, 0)
        self.start_angle = 240  # start position
        self.span_angle = 240   # arc length

    def configure(self, min_val, max_val, unit, title, start_angle=240, span_angle=240, needle_color="red"):
        self.min_val = min_val
        self.max_val = max_val
        self.unit = unit
        self.title = title
        self.start_angle = start_angle
        self.span_angle = span_angle
        self.needle_color = QColor(needle_color)
        self.update()

    def set_value(self, val):
        self.value = max(self.min_val, min(self.max_val, val))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.rect()
        side = min(rect.width(), rect.height())
        painter.translate(rect.center())
        painter.scale(side / 200.0, side / 200.0)

        # face
        painter.setPen(QPen(Qt.GlobalColor.white, 2))
        painter.setBrush(QColor(30, 30, 30))
        painter.drawEllipse(-90, -90, 180, 180)

        # scale
        painter.setPen(QPen(Qt.GlobalColor.white, 1))
        # scale if not synchroscope
        if self.span_angle < 360:
            for i in range(0, 11):
                angle = self.start_angle + i * (self.span_angle / 10)
                painter.save()
                painter.rotate(angle)
                painter.drawLine(0, -80, 0, -88)
                painter.restore()
        else:
            painter.setPen(QPen(Qt.GlobalColor.green, 3))
            painter.drawLine(0, -80, 0, -90) # sync marker

        # needle
        painter.save()
        ratio = (self.value - self.min_val) / (self.max_val - self.min_val)
        painter.rotate(self.start_angle + (ratio * self.span_angle))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.needle_color)
        needle = QPolygonF([QPointF(-2, 0), QPointF(2, 0), QPointF(0, -75)])
        painter.drawPolygon(needle)
        painter.restore()

        # text
        painter.setPen(Qt.GlobalColor.white)
        if self.span_angle < 360:
            painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            painter.drawText(-50, 40, 100, 20, Qt.AlignmentFlag.AlignCenter, f"{self.value:.1f} {self.unit}")
            painter.setFont(QFont("Arial", 8))
            painter.drawText(-50, 60, 100, 20, Qt.AlignmentFlag.AlignCenter, self.title)

class CustomButton(QPushButton):
    def __init__(self, text, color="#444"):
        super().__init__(text)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: 1px solid #666;
                border-radius: 4px;
                padding: 10px;
                font-weight: bold;
            }}
            QPushButton:pressed {{
                background-color: #222;
            }}
            QPushButton:hover {{
                border: 1px solid #999;
            }}
        """)

class WaterLevelGauge(QWidget):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(80)
        self.level = 50.0  # percentage
        self.title = title

    def set_level(self, level):
        self.level = max(0, min(100, level))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        w, h = self.width(), self.height()
        
        # frame
        painter.setBrush(QColor(50, 50, 50))
        painter.drawRect(20, 40, w-40, h-80)

        # water
        fill_h = (self.level / 100.0) * (h - 80)
        painter.setBrush(QColor(0, 120, 255))
        painter.drawRect(20, int(h - 40 - fill_h), w-40, int(fill_h))
        
        # text
        painter.setPen(Qt.GlobalColor.white)
        painter.drawText(0, h-30, w, 20, Qt.AlignmentFlag.AlignCenter, f"{self.level:.1f}%")
        painter.drawText(0, 10, w, 20, Qt.AlignmentFlag.AlignCenter, self.title)

class Annunciator(QLabel):
    def __init__(self, text, alert_color="red"):
        super().__init__(text)
        self.alert_color = alert_color
        self.active = False
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFixedSize(120, 40)
        self.update_style()

    def set_state(self, active):
        self.active = active
        self.update_style()

    def update_style(self):
        bg = self.alert_color if self.active else "#333333"
        fg = "white" if self.active else "#666666"
        self.setStyleSheet(f"""
            background-color: {bg};
            color: {fg};
            border: 2px solid #555;
            font-weight: bold;
            border-radius: 4px;
        """)

class HydroSimulator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hydroelectric Plant Control System")
        self.setStyleSheet("background-color: #121212;")

        # -----------------------------------------------------------------------------------------------------------
        # simulation variables
        # -----------------------------------------------------------------------------------------------------------
        self.gen_phase = 0.0
        self.grid_phase = 0.0
        self.phase_diff = 0.0
        self.water_inflow = 50
        self.water_level = 70
        self.sync = False
        self.gate_opening = 0 
        self.is_emergency = False
        self.gate_direction = 0
        self.current_rpm = 0.0
        self.background_rpm = 0.0
        self.power = 0
        self.turbine_inflow_variation = 0

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # -----------------------------------------------------------------------------------------------------------
        # Top Section: Annunciators
        # -----------------------------------------------------------------------------------------------------------
        annunc_layout = QHBoxLayout()
        self.trip_alarm = Annunciator("TRIP", "red")
        self.alarm_overload = Annunciator("OVERLOAD", "red")
        self.alarm_low_water = Annunciator("LOW WATER", "orange")
        self.high_rpm = Annunciator("HIGH RPM", "yellow")
        self.sync_ready = Annunciator("SYNC READY", "green")
        self.reverse_power = Annunciator("REVERSE POWER", "red")
        self.high_acceleration = Annunciator("HIGH ACCEL.", "red")
        annunc_layout.addWidget(self.trip_alarm)
        annunc_layout.addWidget(self.alarm_low_water)
        annunc_layout.addWidget(self.high_rpm)
        annunc_layout.addWidget(self.high_acceleration)
        annunc_layout.addWidget(self.alarm_overload)
        annunc_layout.addWidget(self.sync_ready)
        annunc_layout.addWidget(self.reverse_power)
        main_layout.addLayout(annunc_layout)

        # -----------------------------------------------------------------------------------------------------------
        # Middle Section: Gauges
        # -----------------------------------------------------------------------------------------------------------
        # Gauges layout
        gauges_layout = QHBoxLayout()
        self.level_gauge = WaterLevelGauge("Forebay Level")
        self.inflow_guage = UniversalGauge("Water Inflow", 0, 100, "%")
        self.outflow_guage = UniversalGauge("Water Outflow", 0, 100, "%")
        self.rpm_gauge = UniversalGauge("Turbine RPM", 0, 1000, "RPM")
        self.freq_gauge = UniversalGauge("Frequency", 45, 65, "Hz")
        self.gate_guage = UniversalGauge("Gate", 0, 100, "%")
        self.synchro = UniversalGauge("Synchroscope", 0, 360, "")
        self.synchro.configure(0, 360, "", "Synchroscope", start_angle=0, span_angle=360, needle_color="yellow")
        self.power_gauge = UniversalGauge("Power", -10, 100, "MW")
        gauges_layout.addWidget(self.inflow_guage)
        gauges_layout.addWidget(self.outflow_guage)
        gauges_layout.addWidget(self.level_gauge)
        gauges_layout.addWidget(self.rpm_gauge)
        gauges_layout.addWidget(self.freq_gauge)
        gauges_layout.addWidget(self.gate_guage)
        gauges_layout.addWidget(self.power_gauge)
        
        # Customise sync gauge
        sync_container = QVBoxLayout()
        sync_container.addWidget(QLabel("<font color='white'>Synchroscope</font>", alignment=Qt.AlignmentFlag.AlignCenter))
        sync_container.addWidget(self.synchro)
        gauges_layout.addLayout(sync_container)

        main_layout.addLayout(gauges_layout)

        # -----------------------------------------------------------------------------------------------------------
        # Bottom Section (1): Dangerous controls
        # -----------------------------------------------------------------------------------------------------------
        # Buttons layout
        controls_layout = QHBoxLayout()
        self.btn_emergency = CustomButton("TRIP", "#800")
        self.btn_reset = CustomButton("RESET TRIP", "#800")
        self.sync_button = CustomButton("SYNC", "#800")
        controls_layout.addWidget(self.btn_emergency)
        controls_layout.addWidget(self.btn_reset)
        controls_layout.addWidget(self.sync_button)
        main_layout.addLayout(controls_layout)

        # link buttons to functions
        self.btn_emergency.clicked.connect(self.handle_emergency_stop)
        self.btn_reset.clicked.connect(self.handle_reset)
        self.sync_button.clicked.connect(lambda: self.synchronise())


        # -----------------------------------------------------------------------------------------------------------
        # Bottom Section (2): Gate controls
        # -----------------------------------------------------------------------------------------------------------
        # Buttons layout
        gate_layout = QHBoxLayout()
        self.increase_gate = CustomButton("+")
        self.increase_gate_2 = CustomButton("+++")
        self.decrease_gate = CustomButton("-")
        self.decrease_gate_2 = CustomButton("---")
        self.stop_gate = CustomButton("STOP")
        gate_layout.addWidget(self.decrease_gate_2)
        gate_layout.addWidget(self.decrease_gate)
        gate_layout.addWidget(self.stop_gate)
        gate_layout.addWidget(self.increase_gate)
        gate_layout.addWidget(self.increase_gate_2)
        main_layout.addLayout(gate_layout)

        # Link to functions
        self.increase_gate.clicked.connect(lambda: self.set_gate_direction(1))
        self.increase_gate_2.clicked.connect(lambda: self.set_gate_direction(5))
        self.decrease_gate.clicked.connect(lambda: self.set_gate_direction(-1))
        self.decrease_gate_2.clicked.connect(lambda: self.set_gate_direction(-5))
        self.stop_gate.clicked.connect(lambda: self.set_gate_direction(0))
        

        # -----------------------------------------------------------------------------------------------------------
        # Run simulation loops
        # -----------------------------------------------------------------------------------------------------------
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_simulation)
        self.timer.start(50)

        self.water_timer = QTimer()
        self.water_timer.timeout.connect(self.update_water_level)
        self.water_timer.start(100)
        
        self.sim_time = 0

    
    # -----------------------------------------------------------------------------------------------------------
    # Button functions
    # -----------------------------------------------------------------------------------------------------------
    def synchronise(self):
        if self.sync == True:
            self.sync = False
        elif (self.phase_diff < 10) or (self.phase_diff > 350) and self.sync == False:
            self.sync = True
            self.background_rpm = self.current_rpm
        else:
            self.sync = False
        
    def set_gate_direction(self, direction):
        if not self.is_emergency:
            self.gate_direction = direction

    def handle_emergency_stop(self):
        self.is_emergency = True
        self.trip_alarm.set_state(True)
        self.gate_opening = 0
        self.gate_direction = 0

    def handle_reset(self):
        self.is_emergency = False
        self.trip_alarm.set_state(False)

    # -----------------------------------------------------------------------------------------------------------
    # Simulation loop slow
    # -----------------------------------------------------------------------------------------------------------

    def update_water_level(self):
        min_inflow = 70.0
        max_inflow = 100.0

        # random walk
        step = random.uniform(-0.5, 0.5)
        self.water_inflow += step

        # soft bounds
        if self.water_inflow < min_inflow + 5:
            self.water_inflow += 0.3
        elif self.water_inflow > max_inflow - 5:
            self.water_inflow -= 0.3

        # random spikes/drops
        if random.random() < 0.01:
            spike = random.uniform(-10, 10)
            self.water_inflow += spike

        self.water_inflow = max(min_inflow, min(max_inflow, self.water_inflow))


    # -----------------------------------------------------------------------------------------------------------
    # Simulation loop fast
    # -----------------------------------------------------------------------------------------------------------

    def update_gate_pos(self):
        if not self.is_emergency and self.gate_direction != 0:
            self.gate_opening = max(0, min(100, self.gate_opening + (self.gate_direction * 0.1)))
            self.turbine_inflow_variation+=0.1
        self.gate_guage.set_value(self.gate_opening)

    def update_turbine_inflow(self):
        if self.turbine_inflow_variation > 0.09 :
            self.turbine_inflow_variation-=0.02
        else:
            self.turbine_inflow_variation = 0


    def update_rpm(self):
        if not self.sync:
            # physics based on gate opening (ADD WATER LEVEL MULTIPLIER)
            target_rpm = (self.gate_opening * 12.0) if not self.is_emergency else 0.0
            self.high_acceleration.set_state(abs(target_rpm-self.current_rpm) > 100)
            # Smoothly move current RPM to target
            self.current_rpm += (target_rpm - self.current_rpm) * 0.005 + (math.sin(20*self.sim_time)*self.turbine_inflow_variation*0.03)
                                
        else:
            target_rpm = 500
            self.current_rpm += (target_rpm - self.current_rpm) * 0.1
            target_rpm = (self.gate_opening * 12.0) if not self.is_emergency else 0.0
            # Simplified RPM
            self.background_rpm += (target_rpm - self.background_rpm) * 0.005
        
        self.rpm_gauge.set_value(self.current_rpm)
    
    def update_water_level(self):
        water_outflow = self.gate_opening
        water_outflow = self.gate_opening
        net_flow = self.water_inflow - water_outflow
        self.water_level += net_flow * 0.00001
        self.water_level = max(0, min(100, self.water_level))

        self.level_gauge.set_level(self.water_level)
        self.inflow_guage.set_value(self.water_inflow)
        self.outflow_guage.set_value(water_outflow)

    def update_synchroscope(self):
        if not self.sync:
            dt = 0.05
            grid_freq = 50.0  
            freq = (self.current_rpm / 10.0) + (0.1 * math.sin(self.sim_time))
            gen_freq = freq
            # hz to degrees
            self.grid_phase = (self.grid_phase + grid_freq * 360 * dt) % 360
            self.gen_phase = (self.gen_phase + gen_freq * 360 * dt) % 360
            current_phase_diff = (self.gen_phase - self.grid_phase) % 360
            if abs(current_phase_diff-self.phase_diff)<=90:
                self.synchro.set_value(current_phase_diff)
                self.sync_ready.set_state(abs(current_phase_diff) < 10 or abs(current_phase_diff > 350))
            else:
                self.synchro.set_value(5)
                self.sync_ready.set_state(False)
            self.phase_diff = current_phase_diff
        else:
            self.synchro.set_value(0)
            self.sync_ready.set_state(True)
            freq = 50.0
        self.freq_gauge.set_value(freq)
    
    def update_power_output(self):
        # caltulate power output (max rpm 1200)
        if self.sync:
            self.power = ((self.background_rpm-500)/700)*100
            if self.power < 0:
                self.reverse_power.set_state(True)
            else:
                self.reverse_power.set_state(False)
        else:
            self.power = 0

        self.power_gauge.set_value(self.power)
    
    def trigger_alarms(self):
        self.alarm_low_water.set_state(self.water_level < 70)
        self.alarm_overload.set_state(self.current_rpm > 600)
        self.high_rpm.set_state(self.current_rpm > 550)
        
        

    def update_simulation(self): # MAIN FUNCTION
        self.sim_time += 0.05
        
        self.update_gate_pos()
        self.update_turbine_inflow()
        self.update_rpm()
        self.update_water_level()
        self.update_synchroscope()
        self.update_power_output()
        self.trigger_alarms()

        


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HydroSimulator()
    window.show()
    sys.exit(app.exec())