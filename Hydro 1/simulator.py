import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction
import numpy as np
import sounddevice as sd
from playsound3 import playsound

# Import custom modules
from annunciators import Annunciator
from gauges import UniversalGauge, LevelGauge
from buttons import CustomButton
from calculation import SimulationEngine
from hydraulics import HydraulicsWindow
from electrical import ElectricalWindow
from turbine import TurbineWindow
from save_dialogue import SaveWindow
from load_dialogue import LoadWindow
from about_project import AboutWindow
from log import LogWindow
from console import ConsoleWindow

class HydroSimulator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hydroelectric Plant Control System")
        self.setStyleSheet("background-color: #121212;")
        self.setFixedSize(1130, 730)

        # Initialize simulation engine
        self.engine = SimulationEngine()
        
        # Hydraulics Window
        self.hydraulics_win = HydraulicsWindow(self.engine)

        # Electrical Window
        self.electrical_win = ElectricalWindow(self.engine)

        # Turbine Window
        self.turbine_win = TurbineWindow(self.engine)

        # Save Window
        self.save_win = SaveWindow(self.engine)

        # Load Window
        self.load_win = LoadWindow(self.engine)

        # About window
        self.about_win = AboutWindow()

        # Log window
        self.log_win = LogWindow(self.engine)

        # Console window
        self.console_win = ConsoleWindow(self.engine)

        # Set sound
        self.turbine_phase_hum = 0.0
        self.turbine_phase_whirr = 0.0
        self.alarm_sample_index = 0
        self.active_sound_freqs = []
        self.alarm_phases = {}
        self.stream = sd.OutputStream(channels=1, callback=self.sound_callback, samplerate=self.engine.SAMPLE_RATE)
        self.stream.start()
        self.silence_sounds = False

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('&File')
        save_action = QAction('&Save', self)
        if self.engine.OS == "Windows":
            save_action.setShortcut('Ctrl+S')
        else:
            save_action.setShortcut('Meta+S')
        save_action.triggered.connect(self.save_win.show)

        load_action = QAction('&Load', self)
        if self.engine.OS == "Windows":
            load_action.setShortcut('Ctrl+O')
        else:
            load_action.setShortcut('Meta+O')
        load_action.triggered.connect(self.load_win.show)
        
        exit_action = QAction('&Exit', self)
        if self.engine.OS == "Windows":
            exit_action.setShortcut('Ctrl+Q')
        else:
            exit_action.setShortcut('Meta+Q')
        exit_action.triggered.connect(exit)
        
        file_menu.addAction(save_action)
        file_menu.addSeparator()
        file_menu.addAction(load_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)
        
        help_menu = menu_bar.addMenu('&Help')
        about_action = QAction('&About', self)
        about_action.triggered.connect(self.toggle_about)
        help_menu.addAction(about_action)

        window_menu = menu_bar.addMenu('&Window')
        turbine_window = QAction('&Turbine', self)
        turbine_window.setShortcut('1')
        turbine_window.triggered.connect(self.toggle_turbine)
        window_menu.addAction(turbine_window)
        hydraulics_window = QAction('&Hydraulics', self)
        hydraulics_window.setShortcut('2')
        hydraulics_window.triggered.connect(self.toggle_hydraulics)
        window_menu.addAction(hydraulics_window)
        electrical_window = QAction('&Electrical', self)
        electrical_window.setShortcut('3')
        electrical_window.triggered.connect(self.toggle_electrical)
        window_menu.addAction(electrical_window)

        debug_menu = menu_bar.addMenu("&Debug")
        log_window = QAction('&Log', self)
        log_window.triggered.connect(self.toggle_log)
        debug_menu.addAction(log_window)
        console_window = QAction('&Console', self)
        console_window.triggered.connect(self.toggle_console)
        debug_menu.addAction(console_window)

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
        self.oil_temp = Annunciator("OIL TEMP", "red", persistent=False)

        annunc_layout.addWidget(self.alarm_interlock)
        annunc_layout.addWidget(self.alarm_low_water)
        annunc_layout.addWidget(self.high_rpm)
        annunc_layout.addWidget(self.high_acceleration)
        annunc_layout.addWidget(self.sync_ready)
        annunc_layout.addWidget(self.reverse_power)
        annunc_layout.addWidget(self.oil_temp)
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
        # Top Section (3): annunciators
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
        self.level_gauge = LevelGauge("Forebay Level")
        
        self.rpm_gauge = UniversalGauge("Turbine RPM", 0, 4000, "RPM")
        self.freq_gauge = UniversalGauge("Frequency", 45, 65, "Hz")
        self.gate_guage = UniversalGauge("Gate", 0, 100, "%", dp=3)
        self.synchro = UniversalGauge("Synchroscope", 0, 360, "")
        self.synchro.configure(0, 360, "", "Synchroscope", start_angle=0, span_angle=360, needle_color="yellow")
        self.power_gauge = UniversalGauge("Power", -10, 100, "MW")
        
        gauges_layout.addWidget(self.level_gauge)
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
        self.silence = CustomButton("SILENCE", "#800")
        self.btn_emergency = CustomButton("TRIP", "#800")
        self.btn_reset = CustomButton("RESET TRIP", "#800")
        self.ack_button = CustomButton("ACKNOWLEDGE", "#444")
        
        controls_layout.addWidget(self.silence)
        controls_layout.addWidget(self.btn_emergency)
        controls_layout.addWidget(self.btn_reset)
        controls_layout.addWidget(self.ack_button)
        main_layout.addLayout(controls_layout)

        # link buttons
        self.silence.clicked.connect(lambda: setattr(self, "silence_sounds", not self.silence_sounds))
        self.btn_emergency.clicked.connect(self.handle_emergency_stop)
        self.btn_reset.clicked.connect(self.handle_reset)
        self.ack_button.clicked.connect(self.acknowledge_alarms)

        # -----------------------------------------------------------------------------------------------------------
        # Bottom Section (2): Sync
        # -----------------------------------------------------------------------------------------------------------
        sync_layout = QHBoxLayout()
        self.sync_button = CustomButton("SYNC", "#800")
        sync_layout.addWidget(self.sync_button)
        main_layout.addLayout(sync_layout)
        self.sync_button.clicked.connect(self.synchronise)

        # -----------------------------------------------------------------------------------------------------------
        # Bottom Section (3): Gate controls
        # -----------------------------------------------------------------------------------------------------------
        gate_layout = QHBoxLayout()
        self.increase_gate = CustomButton("+")
        self.increase_gate_2 = CustomButton("++")
        self.increase_gate_3 = CustomButton("+++")
        self.decrease_gate = CustomButton("-")
        self.decrease_gate_2 = CustomButton("--")
        self.decrease_gate_3 = CustomButton("---")
        self.stop_gate = CustomButton("STOP")
        
        gate_layout.addWidget(self.decrease_gate_3)
        gate_layout.addWidget(self.decrease_gate_2)
        gate_layout.addWidget(self.decrease_gate)
        gate_layout.addWidget(self.stop_gate)
        gate_layout.addWidget(self.increase_gate)
        gate_layout.addWidget(self.increase_gate_2)
        gate_layout.addWidget(self.increase_gate_3)
        main_layout.addLayout(gate_layout)

        # Link to functions
        self.increase_gate.clicked.connect(lambda: self.set_gate_direction(0.2))
        self.increase_gate_2.clicked.connect(lambda: self.set_gate_direction(1))
        self.increase_gate_3.clicked.connect(lambda: self.set_gate_direction(5))
        self.decrease_gate.clicked.connect(lambda: self.set_gate_direction(-0.2))
        self.decrease_gate_2.clicked.connect(lambda: self.set_gate_direction(-1))
        self.decrease_gate_3.clicked.connect(lambda: self.set_gate_direction(-5))
        self.stop_gate.clicked.connect(lambda: self.set_gate_direction(0))
        
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
            self.engine.play_breaker_sound()
        elif (self.engine.phase_diff < 3 and self.engine.phase_diff > 357) and not self.engine.sync and self.engine.current_rpm > 2980 and self.engine.current_rpm < 3020:
            self.engine.sync = True
            self.engine.breaker_hv1ge = True
            self.engine.background_rpm = self.engine.current_rpm
            if 2 < self.engine.phase_diff < 358:
                self.engine.add_damage(1.0)
            if self.engine.excitation < 490 or self.engine.excitation > 510:
                self.engine.add_damage(abs(self.engine.excitation-500))
                self.engine.sync = False
                self.engine.play_breaker_sound()
        else:
            self.engine.sync = False
            self.engine.add_damage(abs(self.engine.phase_diff-180))
            self.engine.play_breaker_sound()
        
    def set_gate_direction(self, direction):
        if not self.engine.is_emergency:
            self.engine.gate_direction = direction
        self.engine.log(f"Gate {direction}")

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

        # Hydraulics
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
        self.turbine_win.turbine_level_gauge.set_level(self.engine.turbine_water_level)
        self.low_hyd_pres.set_state(self.engine.hyd_coef <= 0.5)
        self.electrical_win.update_ui()
        self.turbine_win.update_ui()
        
        # Turbine damage check
        if self.engine.turbine_water_level < 100:
            if self.engine.flow_to_turbine[0] >= 0.5:
                self.engine.add_damage(self.engine.flow_to_turbine[0] * 10)
                self.engine.turbine_water_level = 100
        
        self.engine.update_drain_bypass_pos()
        self.turbine_win.drain_gauge.set_level(self.engine.drain_opening)
        self.turbine_win.bypass_gauge.set_level(self.engine.bypass_opening)
        self.engine.update_excitation()
        self.gate_guage.set_value(self.engine.gate_opening)

        # Turbine systems update
        self.engine.turbine_systems()
        self.turbine_win.update_ui()
        self.oil_temp.set_state(self.engine.oil_temperature >= 85)
        if self.engine.oil_temperature >= 90:
            self.handle_emergency_stop()
    
    def toggle_about(self):
        if self.about_win.isVisible():
            self.about_win.hide()
        else:
            self.about_win.show()

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

    def toggle_turbine(self):
        if self.turbine_win.isVisible():
            self.turbine_win.hide()
        else:
            self.turbine_win.show()

    def toggle_log(self):
        if self.log_win.isVisible():
            self.log_win.hide()
        else:
            self.log_win.show()

    def toggle_console(self):
        if self.console_win.isVisible():
            self.console_win.hide()
        else:
            self.console_win.show()

    def sound_callback(self, outdata, frames, time, status):
        # 1. ALWAYS initialize the chunk with zeros right at the start
        # This acts as our safety net. If we're muted, it just stays dead silent.
        chunk = np.zeros(frames, dtype=np.float32)
        
        if not self.silence_sounds:
            # 2. Calculate turbine sound
            rpm = self.engine.current_rpm
            
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

            # 3. Add alarm sounds if any are active
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
                            phase = self.alarm_phases.get(freq, 0.0)
                            alarm_signal += np.sin(phase)
                            phase += 2 * np.pi * freq / self.engine.SAMPLE_RATE
                            self.alarm_phases[freq] = phase % (2 * np.pi)
                        
                        alarm_volume = 0.15
                        chunk[i] += (alarm_signal / len(active_freqs)) * alarm_volume
                
                self.alarm_sample_index = (self.alarm_sample_index + frames) % cycle_samples
            else:
                self.alarm_sample_index = 0
                self.alarm_phases.clear()
        else:
            # If muted, reset the alarm trackers so they don't get out of sync or pop when unmuted
            self.alarm_sample_index = 0
            self.alarm_phases.clear()
                
        # 4. This will now safely push out either your audio or pure silence
        outdata[:] = chunk.reshape(-1, 1)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HydroSimulator()
    window.show()
    sys.exit(app.exec())