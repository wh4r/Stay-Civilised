import math
import random
from playsound3 import playsound
import platform
import json
from datetime import datetime
from simple_pid import PID

class SimulationEngine:
    def __init__(self):
        # Simulation variables
        # Weather
        self.external_temp = 21.0
        self.rain = False

        # TIMING
        self.sim_time = 0.0

        # WATER
        self.water_inflow = 50.0
        self.water_level = 70.0
        self.sync = False
        self.gate_opening = 0.0
        self.is_emergency = False
        self.gate_direction = 0.0

        # TURBINE
        # generator
        self.current_rpm = 0.0
        self.background_rpm = 0.0
        self.power = 0.0
        self.excitation = 0.0
        self.excitation_direction = 0.0
        self.friction_coefficient = 0
        # water
        self.turbine_inflow_variation = 0.0
        self.damage = 0.0
        self.flow_to_turbine = [0.0 for _ in range(50)]
        self.turbine_water_level = 0.0
        self.bypass_direction = 0.0
        self.bypass_opening = 0.0
        self.drain_direction = 0.0
        self.drain_opening = 0.0
        # sync
        self.gen_phase = 0.0
        self.grid_phase = 0.0
        self.phase_diff = 0.0
        self.phase_diff_prev = 0.0
        # oil
        self.oil_pump_direction = 0
        self.oil_pump_power = 0
        self.oil_pump_source = 0 # 0=ELEC., 1=SHAFT, 2=EM.
        self.oil_temperature = self.external_temp
        self.oil_preheater = False
        self.heat_exc_direction = 0
        self.heat_exc_flow = 0
        # auto
        self.auto_state = False
        self.auto_speed = 0.02


        # HYDRAULICS
        # Pumps
        self.pump1_state = 0  # 0: OFF, 1: STARTING, 2: RUNNING
        self.pump2_state = 0
        self.pump1_timer = 0.0
        self.pump2_timer = 0.0
        self.pump1_flow = 0.0
        self.pump2_flow = 0.0
        self.pump_selector = 1  # 1 or 2
        # Fans
        self.fan1_state = 0  # 0: OFF, 1: STARTING, 2: RUNNING
        self.fan2_state = 0
        self.fan1_timer = 0.0
        self.fan2_timer = 0.0
        # Preheaters
        self.pre1_on = False
        self.pre2_on = False
        # reservoir pressures
        self.res_press_1 = 0
        self.res_press_2 = 0
        self.res_outflow_1 = 0
        self.res_outflow_2 = 0
        # reservoir temperatures
        self.res_temp_1 = 20
        self.res_temp_2 = 20
        self.temp_decrease_timer_1 = 60
        self.temp_decrease_timer_2 = 60
        # coefficient
        self.hyd_coef = 0
        
        # BREAKERS
        # True = CLOSED (ON), False = OPEN (OFF)
        self.breaker_hv1s1 = False
        self.breaker_hv1s2 = False
        self.breaker_hv1ge = False
        self.breaker_hv1ga = False
        self.breaker_hv1gb = False
        self.breaker_dc1dca = False
        self.breaker_dc1dcb = False
        self.breaker_lv1dg = False
        self.breaker_lv1dgs = False
        self.breaker_lv1em = False
        self.ac_bus_a = False
        self.ac_bus_a_usage = 0
        self.ac_bus_b = False
        self.ac_bus_b_usage = 0
        self.dc_bus = False
        self.battery_charge = 5.0
        self.gen_island = False

        # EDG
        self.edg_started = False
        
        # Constants
        self.SAMPLE_RATE = 44100
        self.OS = platform.system()
        if self.OS == "Windows":
            self.path = "Hydro 1\\log.txt"
        elif self.OS == "Darwin":
            self.path = "Hydro 1/log.txt"
        else:
            print("The code is broken (or you're on linux)")
        self.pid = PID(0.005, 0.001, 0, setpoint=0, output_limits=(0, 100))

    def load_file(self, filepath=None):
        try:
            with open(filepath, 'r') as f:
                load_data = json.load(f)
                self.external_temp = load_data['external_temp']
                self.rain = load_data['rain']
                self.sim_time = load_data['sim_time']
                self.water_inflow = load_data['water_inflow']
                self.water_level = load_data['water_level']
                self.sync = load_data['sync']
                self.gate_opening = load_data['gate_opening']
                self.is_emergency = load_data['is_emergency']
                self.gate_direction = load_data['gate_direction']
                self.current_rpm = load_data['current_rpm']
                self.background_rpm = load_data['background_rpm']
                self.power = load_data['power']
                self.excitation = load_data['excitation']
                self.excitation_direction = load_data['excitation_direction']
                self.friction_coefficient = load_data['friction_coefficient']
                self.turbine_inflow_variation = load_data['turbine_inflow_variation']
                self.damage = load_data['damage']
                self.flow_to_turbine = load_data['flow_to_turbine']
                self.turbine_water_level = load_data['turbine_water_level']
                self.bypass_direction = load_data['bypass_direction']
                self.bypass_opening = load_data['bypass_opening']
                self.drain_direction = load_data['drain_direction']
                self.drain_opening = load_data['drain_opening']
                self.gen_phase = load_data['gen_phase']
                self.grid_phase = load_data['grid_phase']
                self.phase_diff = load_data['phase_diff']
                self.phase_diff_prev = load_data['phase_diff_prev']
                self.oil_pump_direction = load_data['oil_pump_direction']
                self.oil_pump_power = load_data['oil_pump_power']
                self.oil_temperature = load_data['oil_temperature']
                self.oil_preheater = load_data['oil_preheater']
                self.heat_exc_direction = load_data['heat_exc_direction']
                self.heat_exc_flow = load_data['heat_exc_flow']
                self.pump2_state = load_data['pump2_state']
                self.pump1_timer = load_data['pump1_timer']
                self.pump2_timer = load_data['pump2_timer']
                self.pump1_flow = load_data['pump1_flow']
                self.pump2_flow = load_data['pump2_flow']
                self.fan2_state = load_data['fan2_state']
                self.fan1_timer = load_data['fan1_timer']
                self.fan2_timer = load_data['fan2_timer']
                self.pre1_on = load_data['pre1_on']
                self.pre2_on = load_data['pre2_on']
                self.res_press_1 = load_data['res_press_1']
                self.res_press_2 = load_data['res_press_2']
                self.res_outflow_1 = load_data['res_outflow_1']
                self.res_outflow_2 = load_data['res_outflow_2']
                self.res_temp_1 = load_data['res_temp_1']
                self.res_temp_2 = load_data['res_temp_2']
                self.temp_decrease_timer_1 = load_data['temp_decrease_timer_1']
                self.temp_decrease_timer_2 = load_data['temp_decrease_timer_2']
                self.hyd_coef = load_data['hyd_coef']
                self.breaker_hv1s1 = load_data['breaker_hv1s1']
                self.breaker_hv1s2 = load_data['breaker_hv1s2']
                self.breaker_hv1ge = load_data['breaker_hv1ge']
                self.breaker_hv1ga = load_data['breaker_hv1ga']
                self.breaker_hv1gb = load_data['breaker_hv1gb']
                self.breaker_dc1dca = load_data['breaker_dc1dca']
                self.breaker_dc1dcb = load_data['breaker_dc1dcb']
                self.breaker_lv1dg = load_data['breaker_lv1dg']
                self.breaker_lv1dgs = load_data['breaker_lv1dgs']
                self.breaker_lv1em = load_data['breaker_lv1em']
                self.ac_bus_a = load_data['ac_bus_a']
                self.ac_bus_a_usage = load_data['ac_bus_a_usage']
                self.ac_bus_b = load_data['ac_bus_b']
                self.ac_bus_b_usage = load_data['ac_bus_b_usage']
                self.dc_bus = load_data['dc_bus']
                self.battery_charge = load_data['battery_charge']
                self.gen_island = load_data['gen_island']
                self.edg_started = load_data['edg_started']
        except Exception as e:
            print('explode', e)

    def save_file(self, filename=None):
        save_variables = {
            'external_temp': self.external_temp,
            'rain': self.rain,
            'sim_time': self.sim_time,
            'water_inflow': self.water_inflow,
            'water_level': self.water_level,
            'sync': self.sync,
            'gate_opening': self.gate_opening,
            'is_emergency': self.is_emergency,
            'gate_direction': self.gate_direction,
            'current_rpm': self.current_rpm,
            'background_rpm': self.background_rpm,
            'power': self.power,
            'excitation': self.excitation,
            'excitation_direction': self.excitation_direction,
            'friction_coefficient': self.friction_coefficient,
            'turbine_inflow_variation': self.turbine_inflow_variation,
            'damage': self.damage,
            'flow_to_turbine': self.flow_to_turbine,
            'turbine_water_level': self.turbine_water_level,
            'bypass_direction': self.bypass_direction,
            'bypass_opening': self.bypass_opening,
            'drain_direction': self.drain_direction,
            'drain_opening': self.drain_opening,
            'gen_phase': self.gen_phase,
            'grid_phase': self.grid_phase,
            'phase_diff': self.phase_diff,
            'phase_diff_prev': self.phase_diff_prev,
            'oil_pump_direction': self.oil_pump_direction,
            'oil_pump_power': self.oil_pump_power,
            'oil_temperature': self.oil_temperature,
            'oil_preheater': self.oil_preheater,
            'heat_exc_direction': self.heat_exc_direction,
            'heat_exc_flow': self.heat_exc_flow,
            'pump2_state': self.pump2_state,
            'pump1_timer': self.pump1_timer,
            'pump2_timer': self.pump2_timer,
            'pump1_flow': self.pump1_flow,
            'pump2_flow': self.pump2_flow,
            'fan2_state': self.fan2_state,
            'fan1_timer': self.fan1_timer,
            'fan2_timer': self.fan2_timer,
            'pre1_on': self.pre1_on,
            'pre2_on': self.pre2_on,
            'res_press_1': self.res_press_1,
            'res_press_2': self.res_press_2,
            'res_outflow_1': self.res_outflow_1,
            'res_outflow_2': self.res_outflow_2,
            'res_temp_1': self.res_temp_1,
            'res_temp_2': self.res_temp_2,
            'temp_decrease_timer_1': self.temp_decrease_timer_1,
            'temp_decrease_timer_2': self.temp_decrease_timer_2,
            'hyd_coef': self.hyd_coef,
            'breaker_hv1s1': self.breaker_hv1s1,
            'breaker_hv1s2': self.breaker_hv1s2,
            'breaker_hv1ge': self.breaker_hv1ge,
            'breaker_hv1ga': self.breaker_hv1ga,
            'breaker_hv1gb': self.breaker_hv1gb,
            'breaker_dc1dca': self.breaker_dc1dca,
            'breaker_dc1dcb': self.breaker_dc1dcb,
            'breaker_lv1dg': self.breaker_lv1dg,
            'breaker_lv1dgs': self.breaker_lv1dgs,
            'breaker_lv1em': self.breaker_lv1em,
            'ac_bus_a': self.ac_bus_a,
            'ac_bus_a_usage': self.ac_bus_a_usage,
            'ac_bus_b': self.ac_bus_b,
            'ac_bus_b_usage': self.ac_bus_b_usage,
            'dc_bus': self.dc_bus,
            'battery_charge': self.battery_charge,
            'gen_island': self.gen_island,
            'edg_started': self.edg_started
        }

        if not filename:
            filename = f"{self.path}{datetime.now().strftime("%Y%m%d_%H%M%S")}"
        else:
            filename = f"{self.path}{filename}"
        try:
            with open(filename, 'w') as f:
                json.dump(save_variables, f, indent=4)
            print(f"saved to {filename}")
        except Exception as e:
            print(f"file blew up: {e}")

    def read_log(self):
        with open(self.path, "r") as f:
            return f.readlines()

    def log(self, log = 'error'):
        with open(self.path, "a") as f:
            f.write(f"{round(self.sim_time, 5)}: {log}\n")

    def clear_log(self):
        with open(self.path, "w") as f:
            f.write("")

    
    def turbine_systems(self):
        self.oil_pump_power = max(0.0, min(100.0, self.oil_pump_power + self.oil_pump_direction)) if self.ac_bus_a else 0
        self.heat_exc_flow = max(0.0, min(100.0, self.heat_exc_flow + self.heat_exc_direction * self.hyd_coef))
        self.oil_temperature += (max(self.current_rpm-500, 0) / 2500) * (1/self.oil_temperature)
        if self.oil_preheater and self.ac_bus_a:
            self.oil_temperature += 0.1 * (1/self.oil_temperature)
        if self.oil_pump_source == 0 and self.ac_bus_a:
            self.oil_temperature -= (self.oil_pump_power/100) * (self.heat_exc_flow/100) * 0.1 * ((self.oil_temperature-self.external_temp)/100)
        elif self.oil_pump_source == 1:
            self.oil_temperature -= (self.current_rpm/300000) * (self.heat_exc_flow/100) * 0.1 * ((self.oil_temperature-self.external_temp)/100)
        elif self.dc_bus:
            self.oil_temperature -= (self.heat_exc_flow/100) * 0.3 * 0.1 * ((self.oil_temperature-self.external_temp)/100)

    def play_breaker_sound(self):
        if self.OS == "Windows":
            playsound("Hydro 1\\breaker.mp3", block=False)
        elif self.OS == "Darwin":
            playsound("Hydro 1/breaker.mp3", block=False)
        else:
            print("The code is broken (or you're on linux)")

    def oil_preheat(self):
        self.oil_preheater = not self.oil_preheater
    
    def update_battery(self):
        # charges and discharges the battery by checking if its connected
        if self.breaker_lv1em:
            if self.battery_charge > 0:
                self.battery_charge -= 0.1
            else:
                self.dc_bus = False
        elif self.breaker_dc1dca or self.breaker_dc1dcb:
            self.battery_charge += 0.05

    def update_res_temp(self):
        # increases temperature if preheater is on
        # decreases temeprature slowly untill it reaches ambient temperature
        # the decrease should be changed to be exponential
        if self.pre1_on:
            self.res_temp_1 += 0.1
        elif self.pump1_state > 0:
            pass
        elif self.res_temp_1 > self.external_temp:
            if self.temp_decrease_timer_1 > 0:
                self.temp_decrease_timer_1 -= 1
            else:
                self.res_temp_1 -= 0.1
                self.temp_decrease_timer_1 = 60
        
        if self.pre2_on:
            self.res_temp_2 += 0.1
        elif self.pump2_state > 0:
            pass
        elif self.res_temp_2 > self.external_temp:
            if self.temp_decrease_timer_2 > 0:
                self.temp_decrease_timer_2 -= 1
            else:
                self.res_temp_2 -= 0.1
                self.temp_decrease_timer_2 = 60

        if self.res_temp_1 > 42 or self.res_temp_1 < 35:
            self.pump1_state = 0
        if self.res_temp_2 > 42 or self.res_temp_2 < 35:
            self.pump2_state = 0

    def ac_bus_a_unpowered(self):
        # disables systems running on AC bus A when it is unpowered
        self.pump1_state = 0
        self.fan1_state = 0
        self.oil_pump_power = 0
    
    def ac_bus_b_unpowered(self):
        # disables systems running on AC bus B when it is unpowered
        self.pump2_state = 0
        self.fan2_state = 0
    
    def dc_bus_unpowered(self):
        # disables systems running on the DC bus when it is unpowered
        # disconnect auto controls here
        pass

    def breaker_event(self, state, breaker):
        # when a breaker is closed, this function ensures only one breaker powers each bys by disabling other breakers connected to the bus
        # bus A interlock
        if breaker == "breaker_hv1ga":
            self.breaker_hv1s1 = False
            self.breaker_hv1s2 = False
            self.breaker_lv1dg = False
            if state and self.gen_island:
                self.ac_bus_a = True
            else:
                self.ac_bus_a = False
                self.ac_bus_a_unpowered()
        elif breaker == "breaker_hv1s1":
            self.breaker_hv1s2 = False
            self.breaker_hv1ga = False
            self.breaker_lv1dg = False
            if state:
                self.ac_bus_a = True
            else:
                self.ac_bus_a = False
                self.ac_bus_a_unpowered()
        elif breaker == "breaker_hv1s2":
            self.breaker_hv1s1 = False
            self.breaker_hv1ga = False
            self.breaker_lv1dg = False
            if state:
                self.ac_bus_a = True
            else:
                self.ac_bus_a = False
                self.ac_bus_a_unpowered()
        elif breaker == "breaker_lv1dg":
            self.breaker_hv1s1 = False
            self.breaker_hv1s2 = False
            self.breaker_hv1ga = False
            if state and self.edg_started:
                self.ac_bus_a = True
            else:
                self.ac_bus_a = False
                self.ac_bus_a_unpowered()
        # DC bus interlock
        elif breaker == "breaker_dc1dca":
            self.breaker_dc1dcb = False
            self.breaker_lv1em = False
            if state and self.ac_bus_a:
                self.dc_bus = True
            else:
                self.dc_bus = False
                self.dc_bus_unpowered()
        elif breaker == "breaker_dc1dcb":
            self.breaker_dc1dca = False
            self.breaker_lv1em = False
            if state and self.ac_bus_b:
                self.dc_bus = True
            else:
                self.dc_bus = False
                self.dc_bus_unpowered()
        elif breaker == "breaker_lv1em":
            self.breaker_dc1dca = False
            self.breaker_dc1dcb = False
            if state and self.battery_charge>0:
                self.dc_bus = True
            else:
                self.dc_bus = False
                self.dc_bus_unpowered()
        self.play_breaker_sound()
        # bus b only has 1 input so no need for interlock


    def update_water_flow(self):
        # updates the amount of water flowing into the reservoir
        min_inflow = 70.0
        max_inflow = 100.0
        step = random.uniform(-0.5, 0.5)
        self.water_inflow += step
        if self.water_inflow < min_inflow + 5:
            self.water_inflow += 0.3
        elif self.water_inflow > max_inflow - 5:
            self.water_inflow -= 0.3
        if random.random() < 0.01:
            spike = random.uniform(-10, 10)
            self.water_inflow += spike
        self.water_inflow = max(min_inflow, min(max_inflow, self.water_inflow))

    def update_excitation(self):
        self.excitation += self.excitation_direction

    def update_flow_to_turbine(self):
        # updates the flow through the very long pipe
        self.flow_to_turbine[len(self.flow_to_turbine)-1] = self.gate_opening
        for i in range(0, len(self.flow_to_turbine)-1):
            self.flow_to_turbine[i] += (self.flow_to_turbine[i+1]-self.flow_to_turbine[i])

    def update_gate_pos(self):
        # opens/closes the gate
        if not self.is_emergency and self.gate_direction != 0:
            self.gate_opening = max(0.0, min(100.0, self.gate_opening + (self.gate_direction * 0.01 * (self.hyd_coef if self.gate_direction > 0 else 1))))
            if self.turbine_inflow_variation <= self.current_rpm/200:
                self.turbine_inflow_variation += 0.1
            self.auto_state = False

    def auto_turbine_control(self):
        self.pid.set_auto_mode(self.auto_state, last_output=self.gate_opening)
        last_pos = self.gate_opening
        if self.auto_state and self.hyd_coef >= 0.5 and not self.is_emergency:
            gate_target = self.pid(self.current_rpm, dt=0.1)
            gate_error = gate_target - last_pos
            clipped_change = max(-self.auto_speed, min(self.auto_speed, gate_error))
            self.gate_opening = last_pos + clipped_change

    def update_drain_bypass_pos(self):
        # updates turbine level when bypass or drain are opened
        self.drain_opening = max(0.0, min(100.0, self.drain_opening + (self.drain_direction * (self.hyd_coef if self.drain_direction > 0 else 1))))
        self.bypass_opening = max(0.0, min(100.0, self.bypass_opening + (self.bypass_direction * (self.hyd_coef if self.bypass_direction > 0 else 1))))

    def update_turbine_inflow(self):
        # determines how much turbulence is at the gate and thus fluctuations in flow
        if self.turbine_inflow_variation > 0.09:
            self.turbine_inflow_variation -= 0.02
        else:
            self.turbine_inflow_variation = 0.0

    def update_hydraulics(self):
        # updates the reservoir pressure when the pumps are starting/running
        if self.pump1_state == 2:
            inflow1 = 100
        elif self.pump1_state == 1:
            inflow1 = self.pump1_timer*10
        else:
            inflow1 = 0
        if self.pump2_state == 2:
            inflow2 = 100
        elif self.pump2_state == 1:
            inflow2 = self.pump1_timer*10
        else:
            inflow2 = 0
        self.res_press_1 += (100-self.res_press_1)*(inflow1-self.res_outflow_1)*0.00001
        self.res_press_2 += (100-self.res_press_2)*(inflow2-self.res_outflow_2)*0.00001
        if self.pump_selector == 1:
            self.hyd_coef = self.res_press_1/100
        elif self.pump_selector == 2:
            self.hyd_coef = self.res_press_2/100
        else:
            self.hyd_coef = 0
    

    def update_rpm(self):
        # calculates the turbine RPM
        # there are LOTS of calculations DO NOT TOUCH THIS FUNCTION

        self.friction_coefficient = (self.current_rpm*0.1)*(self.damage/10)
        # This is calculated using the damage, oil temperature, rpm

        high_accel = False
        if not self.sync:
            target_rpm = (self.flow_to_turbine[0] * 12.0 * 6 - self.friction_coefficient) if not self.is_emergency else 0.0
            if target_rpm - self.current_rpm > 100:
                high_accel = True
                self.add_damage()
            self.current_rpm += (target_rpm - self.current_rpm) * 0.01 + (math.sin(random.randint(10,20)*self.sim_time)*self.turbine_inflow_variation*0.03)
            self.gen_island = True if self.current_rpm > 2950 and self.current_rpm < 3050 else False
        else:
            self.gen_island = True
            target_rpm = 3000.0
            self.current_rpm += (target_rpm - self.current_rpm) * 0.1
            target_rpm = (self.flow_to_turbine[0] * 12.0) if not self.is_emergency else 0.0
            self.background_rpm += (target_rpm - self.background_rpm) * 0.005
        return high_accel

    def update_water_level(self):
        # Updates the reservoir water level very slowly
        water_outflow = self.gate_opening
        net_flow = self.water_inflow - water_outflow
        self.water_level += net_flow * 0.00001
        self.water_level = max(0.0, min(100.0, self.water_level))
        return water_outflow

    def update_synchroscope(self, dt=0.05):
        # calculates phase difference when turbine is not synced
        grid_freq = 50.0
        if not self.sync:
            freq = (self.current_rpm / 60.0) + (0.1 * math.sin(self.sim_time))
            self.grid_phase = (self.grid_phase + grid_freq * 360 * dt) % 360
            self.gen_phase = (self.gen_phase + freq * 360 * dt) % 360
            current_phase_diff = (self.gen_phase - self.grid_phase) % 360
            self.phase_diff = current_phase_diff
            return freq, current_phase_diff
        else:
            self.phase_diff = 0.0
            return 50.0, 0.0

    def update_power_output(self):
        # Calculates the power produced in MW
        # This must be updated to follow the equation P=pghQ where Q is flow rate in m^3

        if self.sync:
            self.power = ((self.background_rpm-3000)/700)*100
        else:
            self.power = 0.0
        return self.power

    def add_damage(self, amount=0.1):
        # adds damage
        # i have no idea why this exists but it does
        if self.damage < 100:
            self.damage += amount

    def damage_system(self):
        # explodes the turbine when it is very damaged
        # update this to scale as damage increases, higher change when higher damage
        if self.damage > 80 and random.randint(0, 50) == 0:
            self.is_emergency = True
            self.current_rpm = 0.0
            return True
        return False

    def update_systems(self, dt=0.05):
        # function to update the hydraulics pumps and their fans
        # Pump 1 state machine
        if self.pump1_state == 1:
            self.pump1_timer += dt
            if self.pump1_timer >= 10.0:
                self.pump1_state = 2
                self.pump1_timer = 0.0
        
        # Pump 2 state machine
        if self.pump2_state == 1:
            self.pump2_timer += dt
            if self.pump2_timer >= 10.0:
                self.pump2_state = 2
                self.pump2_timer = 0.0

        # Fan 1 state machine
        if self.fan1_state == 1:
            self.fan1_timer += dt
            if self.fan1_timer >= 10.0:
                self.fan1_state = 2
                self.fan1_timer = 0.0

        # Fan 2 state machine
        if self.fan2_state == 1:
            self.fan2_timer += dt
            if self.fan2_timer >= 10.0:
                self.fan2_state = 2
                self.fan2_timer = 0.0

    def start_pump(self, pump_num):
        # the name explains this
        if pump_num == 1 and self.pump1_state == 0 and self.res_temp_1 >= 35 and self.res_temp_1 <= 42 and self.fan1_state == 2 and self.ac_bus_a:
            self.pump1_state = 1
            self.pump1_timer = 0.0
        elif pump_num == 2 and self.pump2_state == 0 and self.res_temp_2 >= 35 and self.res_temp_2 <= 42 and self.fan2_state == 2 and self.ac_bus_b:
            self.pump2_state = 1
            self.pump2_timer = 0.0

    def stop_pump(self, pump_num):
        # the name explains this
        if pump_num == 1:
            self.pump1_state = 0
            self.pump1_timer = 0.0
        elif pump_num == 2:
            self.pump2_state = 0
            self.pump2_timer = 0.0

    def start_fan(self, fan_num):
        # the name explains this
        if fan_num == 1 and self.fan1_state == 0 and self.ac_bus_a:
            self.fan1_state = 1
            self.fan1_timer = 0.0
        elif fan_num == 2 and self.fan2_state == 0 and self.ac_bus_b:
            self.fan2_state = 1
            self.fan2_timer = 0.0

    def stop_fan(self, fan_num):
        # the name explains this
        if fan_num == 1:
            self.fan1_state = 0
            self.fan1_timer = 0.0
            self.pump1_state = 0
            self.pre1_on = False
        elif fan_num == 2:
            self.fan2_state = 0
            self.fan2_timer = 0.0
            self.pump2_state = 0
            self.pre2_on = False

    def update_turbine_water_level(self):
        # changes the turbine level when bypass or drain is active
        if self.current_rpm < 10:
            self.turbine_water_level += (self.bypass_opening * .01) - (self.drain_opening * .01)
        
        self.turbine_water_level = max(0.0, min(100.0, self.turbine_water_level))

    def update_pump_reservoir(self):
        # i have no idea what this function does. better not touch this.
        if self.pump2_state == 2:
            self.pump2_flow += (1.0 - self.pump2_flow) * 0.1
        else:
            self.pump2_flow += (0.0 - self.pump2_flow) * 0.1
        self.water_level += self.pump2_flow * 0.0001
        self.water_level = min(100.0, self.water_level)

    def check_interlock(self):
        # checks if something is running when its not supposed to
        if self.current_rpm < 10:
            return False
        elif self.bypass_opening > 0 or self.drain_opening > 0:
            return True
        return False