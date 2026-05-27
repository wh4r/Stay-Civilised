import sys
import math
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer
import numpy as np
import sounddevice as sd
import random
from playsound3 import playsound

# Import custom modules
from annunciators import Annunciator
from gauges import UniversalGauge, WaterLevelGauge
from buttons import CustomButton
from calculation import SimulationEngine
from hydraulics import HydraulicsWindow
from electrical import ElectricalWindow

class HydroSimulator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hydroelectric Plant Control System")
        self.setStyleSheet("background-color: #121212;")

        # Initialize simulation engine
        self.engine = SimulationEngine()
        
        # Hydraulics Window
        self.hydraulics_win = HydraulicsWindow(self.engine)

        # Electrical Window
        self.electrical_win = ElectricalWindow(self.engine)

        # Set sound
        self.turbine_phase_hum = 0.0
        self.turbine_phase_whirr = 0.0
        self.alarm_sample_index = 0
        self.active_sound_freqs = []
        self.alarm_phases = {}
        self.stream = sd.OutputStream(channels=1, callback=self.sound_callback, samplerate=self.engine.SAMPLE_RATE)
        self.stream.start()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # -----------------------------------------------------------------------------------------------------------
        # Top Section (1): annunciators
        # -----------------------------------------------------------------------------------------------------------
        annunc_layout = QHBoxLayout()
        self.alarm_interlock = Annunciator("INTERLOCK", "red", persistent=True, sound_freq=330)
        self.alarm_low_water = Annunciator("LOW WATER", "orange", persistent=True, sound_freq=330)
        self.high_rpm = Annunciator("HIGH RPM", "orange", persistent=True, sound_freq=660)
        self.high_acceleration = Annunciator("HIGH ACCEL.", "red", persistent=True, sound_freq=770)
        self.reverse_power = Annunciator("REVERSE POWER", "red", persistent=True, sound_freq=880)
        self.sync_ready = Annunciator("SYNC READY", "green", persistent=False)
        self.placeholder = Annunciator(".", "gray", persistent=False)

        annunc_layout.addWidget(self.alarm_interlock)
        annunc_layout.addWidget(self.alarm_low_water)
        annunc_layout.addWidget(self.high_rpm)
        annunc_layout.addWidget(self.high_acceleration)
        annunc_layout.addWidget(self.sync_ready)
        annunc_layout.addWidget(self.reverse_power)
        annunc_layout.addWidget(self.placeholder)
        main_layout.addLayout(annunc_layout)

        # -----------------------------------------------------------------------------------------------------------
        # Top Section (2): annunciators
        # -----------------------------------------------------------------------------------------------------------
        annunc_layout_2 = QHBoxLayout()
        self.trip_alarm = Annunciator("TRIP", "red", persistent=True, sound_freq=440)
        self.alarm_overload = Annunciator("OVERLOAD", "red", persistent=True, sound_freq=550)
        self.malfunction = Annunciator("MALF.", "red", persistent=True, sound_freq=622)
        self.low_hyd_pres = Annunciator("LOW HYD. PRES.", "red", persistent=True, sound_freq=650)
        self.bus_a_pwr = Annunciator("BUS A PWR", "red", persistent=True, sound_freq=680)
        self.bus_b_pwr = Annunciator("BUS B PWR", "orange", persistent=True)
        self.bus_dc_pwr = Annunciator("DC BUS PWR", "red", persistent=True, sound_freq=680)

        annunc_layout_2.addWidget(self.trip_alarm)
        annunc_layout_2.addWidget(self.alarm_overload)
        annunc_layout_2.addWidget(self.malfunction)
        annunc_layout_2.addWidget(self.low_hyd_pres)
        annunc_layout_2.addWidget(self.bus_a_pwr)
        annunc_layout_2.addWidget(self.bus_b_pwr)
        annunc_layout_2.addWidget(self.bus_dc_pwr)
        main_layout.addLayout(annunc_layout_2)

        # -----------------------------------------------------------------------------------------------------------
        # Top Section (2): annunciators
        # -----------------------------------------------------------------------------------------------------------
        annunc_layout_3 = QHBoxLayout()
        self.placeholder_1 = Annunciator(".", "gray", persistent=False)
        self.placeholder_2 = Annunciator(".", "gray", persistent=False)
        self.placeholder_3 = Annunciator(".", "gray", persistent=False)
        self.placeholder_4 = Annunciator(".", "gray", persistent=False)
        self.placeholder_5 = Annunciator(".", "gray", persistent=False)
        self.placeholder_6 = Annunciator(".", "gray", persistent=False)
        self.placeholder_7 = Annunciator(".", "gray", persistent=False)

        annunc_layout_3.addWidget(self.placeholder_1)
        annunc_layout_3.addWidget(self.placeholder_2)
        annunc_layout_3.addWidget(self.placeholder_3)
        annunc_layout_3.addWidget(self.placeholder_4)
        annunc_layout_3.addWidget(self.placeholder_5)
        annunc_layout_3.addWidget(self.placeholder_6)
        annunc_layout_3.addWidget(self.placeholder_7)
        main_layout.addLayout(annunc_layout_3)

        # -----------------------------------------------------------------------------------------------------------
        # Middle Section (1): Operation gauges
        # -----------------------------------------------------------------------------------------------------------
        gauges_layout = QHBoxLayout()
        self.level_gauge = WaterLevelGauge("Forebay Level")
        self.turbine_level_gauge = WaterLevelGauge("Turbine level")
        self.drain_gauge = WaterLevelGauge("Drain", [255,0,100])
        self.bypass_gauge = WaterLevelGauge("Bypasss", [255,0,100])
        self.rpm_gauge = UniversalGauge("Turbine RPM", 0, 4000, "RPM")
        self.freq_gauge = UniversalGauge("Frequency", 45, 65, "Hz")
        self.gate_guage = UniversalGauge("Gate", 0, 100, "%")
        self.synchro = UniversalGauge("Synchroscope", 0, 360, "")
        self.synchro.configure(0, 360, "", "Synchroscope", start_angle=0, span_angle=360, needle_color="yellow")
        self.power_gauge = UniversalGauge("Power", -10, 100, "MW")
        
        gauges_layout.addWidget(self.level_gauge)
        gauges_layout.addWidget(self.turbine_level_gauge)
        gauges_layout.addWidget(self.drain_gauge)
        gauges_layout.addWidget(self.bypass_gauge)
        gauges_layout.addWidget(self.rpm_gauge)
        gauges_layout.addWidget(self.freq_gauge)
        gauges_layout.addWidget(self.gate_guage)
        gauges_layout.addWidget(self.power_gauge)
        
        sync_container = QVBoxLayout()
        sync_container.addWidget(QLabel("<font color='white'>Synchroscope</font>", alignment=Qt.AlignmentFlag.AlignCenter))
        sync_container.addWidget(self.synchro)
        gauges_layout.addLayout(sync_container)
        main_layout.addLayout(gauges_layout)

        # -----------------------------------------------------------------------------------------------------------
        # Middle Section (2): Alt gauges
        # -----------------------------------------------------------------------------------------------------------
        gauges_layout2 = QHBoxLayout()
        self.inflow_guage = UniversalGauge("Water Inflow", 0, 100, "%")
        self.outflow_guage = UniversalGauge("Water Outflow", 0, 100, "%")
        self.damage_guage = UniversalGauge("Damage", 0, 100, "%")
        self.excitation_gauge = UniversalGauge("Excitation", 0, 500, "V")
        
        gauges_layout2.addWidget(self.inflow_guage)
        gauges_layout2.addWidget(self.outflow_guage)
        gauges_layout2.addWidget(self.damage_guage)
        main_layout.addLayout(gauges_layout2)

        # -----------------------------------------------------------------------------------------------------------
        # Bottom Section (1): Dangerous controls
        # -----------------------------------------------------------------------------------------------------------
        controls_layout = QHBoxLayout()
        self.btn_emergency = CustomButton("TRIP", "#800")
        self.btn_reset = CustomButton("RESET TRIP", "#800")
        self.ack_button = CustomButton("ACKNOWLEDGE", "#444")
        self.decrease_excitation = CustomButton("-")
        self.stop_excitation = CustomButton("EXCITATION STOP")
        self.increase_excitation = CustomButton("+")
        self.btn_hydraulics = CustomButton("HYDRAULICS", "#0066cc")
        self.btn_electrical = CustomButton("ELECTRICAL", "#008080")
        
        controls_layout.addWidget(self.btn_emergency)
        controls_layout.addWidget(self.btn_reset)
        controls_layout.addWidget(self.ack_button)
        controls_layout.addWidget(self.decrease_excitation)
        controls_layout.addWidget(self.stop_excitation)
        controls_layout.addWidget(self.increase_excitation)
        controls_layout.addWidget(self.btn_hydraulics)
        controls_layout.addWidget(self.btn_electrical)
        main_layout.addLayout(controls_layout)

        # link buttons
        self.btn_emergency.clicked.connect(self.handle_emergency_stop)
        self.btn_reset.clicked.connect(self.handle_reset)
        self.ack_button.clicked.connect(self.acknowledge_alarms)
        self.decrease_excitation.clicked.connect(lambda: setattr(self.engine, 'excitation_direction', -1))
        self.stop_excitation.clicked.connect(lambda: setattr(self.engine, 'excitation_direction', 0))
        self.increase_excitation.clicked.connect(lambda: setattr(self.engine, 'excitation_direction', 1))
        self.btn_hydraulics.clicked.connect(self.toggle_hydraulics)
        self.btn_electrical.clicked.connect(self.toggle_electrical)

        # -----------------------------------------------------------------------------------------------------------
        # Bottom Section (2): Gate controls
        # -----------------------------------------------------------------------------------------------------------
        gate_layout = QHBoxLayout()
        self.increase_gate = CustomButton("+")
        self.increase_gate_2 = CustomButton("+++")
        self.decrease_gate = CustomButton("-")
        self.decrease_gate_2 = CustomButton("---")
        self.stop_gate = CustomButton("STOP")
        self.sync_button = CustomButton("SYNC", "#800")
        
        gate_layout.addWidget(self.decrease_gate_2)
        gate_layout.addWidget(self.decrease_gate)
        gate_layout.addWidget(self.stop_gate)
        gate_layout.addWidget(self.increase_gate)
        gate_layout.addWidget(self.increase_gate_2)
        gate_layout.addWidget(self.sync_button)
        main_layout.addLayout(gate_layout)

        # Link to functions
        self.increase_gate.clicked.connect(lambda: self.set_gate_direction(1))
        self.increase_gate_2.clicked.connect(lambda: self.set_gate_direction(5))
        self.decrease_gate.clicked.connect(lambda: self.set_gate_direction(-1))
        self.decrease_gate_2.clicked.connect(lambda: self.set_gate_direction(-5))
        self.stop_gate.clicked.connect(lambda: self.set_gate_direction(0))
        self.sync_button.clicked.connect(self.synchronise)

        # -----------------------------------------------------------------------------------------------------------
        # Bottom Section (3): Alt water flow
        # -----------------------------------------------------------------------------------------------------------
        bypass_layout = QHBoxLayout()
        self.decrease_drain = CustomButton("-")
        self.stop_drain = CustomButton("DRAIN STOP")
        self.increase_drain = CustomButton("+")
        self.decrease_bypass = CustomButton("-")
        self.stop_bypass = CustomButton("BYPASS STOP")
        self.increase_bypass = CustomButton("+")
        
        bypass_layout.addWidget(self.decrease_drain)
        bypass_layout.addWidget(self.stop_drain)
        bypass_layout.addWidget(self.increase_drain)
        bypass_layout.addWidget(self.decrease_bypass)
        bypass_layout.addWidget(self.stop_bypass)
        bypass_layout.addWidget(self.increase_bypass)
        main_layout.addLayout(bypass_layout)

        # Link to functions
        self.decrease_drain.clicked.connect(lambda: setattr(self.engine, 'drain_direction', -1))
        self.stop_drain.clicked.connect(lambda: setattr(self.engine, 'drain_direction', 0))
        self.increase_drain.clicked.connect(lambda: setattr(self.engine, 'drain_direction', 1))
        self.decrease_bypass.clicked.connect(lambda: setattr(self.engine, 'bypass_direction', -1))
        self.stop_bypass.clicked.connect(lambda: setattr(self.engine, 'bypass_direction', 0))
        self.increase_bypass.clicked.connect(lambda: setattr(self.engine, 'bypass_direction', 1))
        
        # -----------------------------------------------------------------------------------------------------------
        # Run simulation loops
        # -----------------------------------------------------------------------------------------------------------
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_simulation)
        self.timer.start(50)

        self.water_timer = QTimer()
        self.water_timer.timeout.connect(self.sim_loop_slow_main)
        self.water_timer.start(100)

        self.water_inflow = QTimer()
        self.water_inflow.timeout.connect(self.update_water_inflow)
        self.water_inflow.start(5000)

        self.blink_timer = QTimer()
        self.blink_timer.timeout.connect(self.blink_alarms)
        self.blink_timer.start(500)

        self.temp_timer = QTimer()
        self.temp_timer.timeout.connect(self.loop_1s)
        self.temp_timer.start(200)

        self.slow_timer = QTimer()
        self.slow_timer.timeout.connect(self.sim_loop_slow)
        self.slow_timer.start(1000)

    def update_water_inflow(self):
        self.engine.update_water_flow()

    def sim_loop_slow(self):
        # use this for optimisations
        self.electrical_win.update_ui()
        self.engine.update_battery()
        pass

    def loop_1s(self):
        self.engine.update_res_temp()
        self.hydraulics_win.res_temp_1.set_value(self.engine.res_temp_1)
        self.hydraulics_win.res_temp_2.set_value(self.engine.res_temp_2)

    def blink_alarms(self):
        for alarm in [self.trip_alarm, self.alarm_low_water, self.high_rpm, 
                    self.high_acceleration, self.alarm_overload, self.reverse_power, 
                    self.alarm_interlock, self.low_hyd_pres, self.bus_a_pwr, 
                    self.bus_b_pwr, self.bus_dc_pwr, self.malfunction]:
            alarm.toggle_blink()

    def synchronise(self):
        if self.engine.sync:
            self.engine.sync = False
            playsound("Hydro 1\\breaker.mp3", block=False)
        elif (self.engine.phase_diff < 3 or self.engine.phase_diff > 357) and not self.engine.sync and 2800 < self.engine.current_rpm < 3200:
            self.engine.sync = True
            self.engine.background_rpm = self.engine.current_rpm
            if 2 < self.engine.phase_diff < 358:
                self.engine.add_damage(1.0)
            if self.engine.excitation < 490 or self.engine.excitation > 510:
                self.engine.add_damage(abs(self.engine.excitation-500))
                self.engine.sync = False
                playsound("Hydro 1\\breaker.mp3", block=False)
        else:
            self.engine.sync = False
            self.engine.add_damage(abs(self.engine.phase_diff-180))
            playsound("Hydro 1\\breaker.mp3", block=False)
        
    def set_gate_direction(self, direction):
        if not self.engine.is_emergency:
            self.engine.gate_direction = direction

    def handle_emergency_stop(self):
        self.engine.is_emergency = True
        self.trip_alarm.set_state(True)
        self.engine.gate_opening = 0
        self.engine.gate_direction = 0
        self.engine.sync = False

    def handle_reset(self):
        self.engine.is_emergency = False
        self.trip_alarm.set_state(False)
        self.trip_alarm.acknowledge()
    
    def acknowledge_alarms(self):
        self.alarm_low_water.acknowledge()
        self.high_rpm.acknowledge()
        self.high_acceleration.acknowledge()
        self.alarm_overload.acknowledge()
        self.sync_ready.acknowledge()
        self.reverse_power.acknowledge()
        self.alarm_interlock.acknowledge()
        self.low_hyd_pres.acknowledge()
        self.bus_a_pwr.acknowledge()
        self.bus_b_pwr.acknowledge()
        self.bus_dc_pwr.acknowledge()

    def sim_loop_slow_main(self):
        self.engine.update_flow_to_turbine()
        self.engine.update_turbine_water_level()
        self.engine.update_pump_reservoir()
        self.engine.update_systems(0.1)
        self.alarm_interlock.set_state(self.engine.check_interlock())

        # electricity
        if self.engine.gen_island:
            self.engine.ac_bus_b = self.engine.breaker_hv1gb
        else:
            self.engine.ac_bus_b = False
            self.engine.ac_bus_b_unpowered()
        self.bus_a_pwr.set_state(not self.engine.ac_bus_a)
        self.bus_b_pwr.set_state(not self.engine.ac_bus_b)
        self.bus_dc_pwr.set_state(not self.engine.dc_bus)

    def update_simulation(self):
        self.engine.sim_time += 0.05
        
        self.engine.update_gate_pos()
        self.engine.update_turbine_inflow()
        
        # RPM update
        high_accel = self.engine.update_rpm()
        self.high_acceleration.set_state(high_accel)
        self.rpm_gauge.set_value(self.engine.current_rpm)
        
        # Water Level
        outflow = self.engine.update_water_level()
        self.level_gauge.set_level(self.engine.water_level)
        self.inflow_guage.set_value(self.engine.water_inflow)
        self.outflow_guage.set_value(outflow)

        # hydraulics
        self.engine.update_hydraulics()
        self.hydraulics_win.res_gauge_1.set_value(self.engine.res_press_1)
        self.hydraulics_win.res_gauge_2.set_value(self.engine.res_press_2)
        
        # Synchroscope
        freq, current_phase_diff = self.engine.update_synchroscope()
        
        # Restore original glitch protection logic
        if abs(current_phase_diff - self.engine.phase_diff_prev) <= 90:
            self.synchro.set_value(current_phase_diff)
            self.sync_ready.set_state(current_phase_diff < 10 or current_phase_diff > 350)
        else:
            self.synchro.set_value(5)
            self.sync_ready.set_state(False)
            
        self.engine.phase_diff_prev = current_phase_diff
        self.freq_gauge.set_value(freq)
        
        # Power
        power = self.engine.update_power_output()
        self.reverse_power.set_state(power < 0 if self.engine.sync else False)
        self.power_gauge.set_value(power)
        
        # Alarms
        self.alarm_low_water.set_state(self.engine.water_level < 50)
        self.alarm_overload.set_state(self.engine.current_rpm > 3300)
        self.high_rpm.set_state(self.engine.current_rpm > 3100)
        if self.engine.water_level < 50 or self.engine.current_rpm > 3100:
            self.engine.add_damage()

        # Update active sound frequencies for the audio callback
        active_freqs = []
        for alarm in [
            self.alarm_interlock, self.alarm_low_water, self.high_rpm, self.high_acceleration,
            self.reverse_power, self.trip_alarm, self.alarm_overload, self.malfunction,
            self.low_hyd_pres, self.bus_a_pwr, self.bus_dc_pwr
        ]:
            if alarm.active and alarm.sound_freq:
                active_freqs.append(alarm.sound_freq)
        self.active_sound_freqs = active_freqs

        # Malfunction
        if self.engine.damage_system():
            self.malfunction.set_state(True)
            self.engine.is_emergency = True

        # UI Updates
        self.damage_guage.set_value(self.engine.damage)
        self.excitation_gauge.set_value(self.engine.excitation)
        self.turbine_level_gauge.set_level(self.engine.turbine_water_level)
        self.low_hyd_pres.set_state(self.engine.hyd_coef <= 0.5)
        self.electrical_win.update_ui()
        
        # Turbine damage check
        if self.engine.turbine_water_level < 100:
            if self.engine.flow_to_turbine[0] >= 0.5:
                self.engine.add_damage(self.engine.flow_to_turbine[0] * 10)
                self.engine.turbine_water_level = 100
        
        self.engine.update_drain_bypass_pos()
        self.drain_gauge.set_level(self.engine.drain_opening)
        self.bypass_gauge.set_level(self.engine.bypass_opening)
        self.engine.update_excitation()
        self.gate_guage.set_value(self.engine.gate_opening)

    def toggle_hydraulics(self):
        if self.hydraulics_win.isVisible():
            self.hydraulics_win.hide()
        else:
            self.hydraulics_win.show()

    def toggle_electrical(self):
        if self.electrical_win.isVisible():
            self.electrical_win.hide()
        else:
            self.electrical_win.show()

    def sound_callback(self, outdata, frames, time, status):
        # 1. Calculate turbine sound (hum and whirr)
        rpm = self.engine.current_rpm
        chunk = np.zeros(frames, dtype=np.float32)
        
        if rpm >= 1:
            max_volume = 0.2
            volume = max(0.0, min(max_volume, ((rpm - 1) / (100 - 1)) * max_volume))
            base_freq = 50 + (rpm / 6000) * 500
            phase_inc_hum = 2 * np.pi * base_freq / self.engine.SAMPLE_RATE
            phase_inc_whirr = 2 * np.pi * base_freq * 3 / self.engine.SAMPLE_RATE
            
            for i in range(frames):
                chunk[i] = volume * (np.sin(self.turbine_phase_hum) + 0.3 * np.sin(self.turbine_phase_whirr))
                self.turbine_phase_hum += phase_inc_hum
                self.turbine_phase_whirr += phase_inc_whirr
            
            self.turbine_phase_hum %= 2 * np.pi
            self.turbine_phase_whirr %= 2 * np.pi

        # 2. Add alarm sounds if any are active
        active_freqs = getattr(self, 'active_sound_freqs', [])
        if active_freqs:
            cycle_samples = int(self.engine.SAMPLE_RATE * 0.5)  # 500 ms cycle
            on_samples = int(self.engine.SAMPLE_RATE * 0.2)     # 200 ms beep
            
            # Generate the alarm waves
            for i in range(frames):
                cycle_pos = (self.alarm_sample_index + i) % cycle_samples
                if cycle_pos < on_samples:
                    # Alarm is in the "ON" part of the beep cycle
                    alarm_signal = 0.0
                    for freq in active_freqs:
                        # Get or initialize phase for this frequency
                        phase = self.alarm_phases.get(freq, 0.0)
                        alarm_signal += np.sin(phase)
                        # Increment phase
                        phase += 2 * np.pi * freq / self.engine.SAMPLE_RATE
                        self.alarm_phases[freq] = phase % (2 * np.pi)
                    
                    # Normalize alarm volume so it doesn't clip
                    alarm_volume = 0.15
                    chunk[i] += (alarm_signal / len(active_freqs)) * alarm_volume
            
            self.alarm_sample_index = (self.alarm_sample_index + frames) % cycle_samples
        else:
            self.alarm_sample_index = 0
            self.alarm_phases.clear()
            
        outdata[:] = chunk.reshape(-1, 1)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HydroSimulator()
    window.show()
    sys.exit(app.exec())