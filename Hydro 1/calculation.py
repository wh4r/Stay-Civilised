import math
import random
from playsound3 import playsound
import platform
import json
import sys
import os
from datetime import datetime
from simple_pid import PID
from pathlib import Path

class SimulationEngine:
    def __init__(self):
        # Simulation variables
        # Weather
        self.external_temp = 21.0
        self.rain = False

        # TIMING
        self.sim_time = 0.0
        self.timestamp = [1,0,0,0]
        self.prev_day=1

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

        # SPILLWAY
        self.spill_open_1 = 0
        self.spill_open_2 = 0
        self.spill_1 = 0
        self.spill_2 = 0

        # DEMAND
        self.current_demand = 0
        self.seed = 86557
        self.today_demand = []

        # Rolling history (demand + forebay level), sampled once per 30
        # simulated seconds, keeping a rolling 20-minute window.
        self.HISTORY_LEN = 120
        self.demand_history = []
        self.water_history = []
        self._last_history_period = -1

        # WIND FARM — 50 × 10 MW turbines
        self.wind_speed = 8.0
        self.wind_turbine_count = 50
        self.wind_turbine_rating = 10.0
        # 0=OFF, 1=STARTING (flashing), 2=RUNNING, 3=STOPPING (flashing)
        self.wind_turbines_state = [0] * 50
        self.wind_turbines_timer = [0.0] * 50
        self.wind_turbines_power = [0.0] * 50
        self.wind_total_power = 0.0
        self.wind_flash = False
        # per-turbine local wind offset (sensor vs. farm spread) — high inertia spatially
        self.wind_turbine_bias = [random.uniform(-1.5, 1.5) for _ in range(50)]

        # EDG
        self.edg_started = False

        # COAL POWER PLANTS — up to 2 units, each 0-100 MW
        self.coal_ramp_rate = 2.0   # MW per update step
        self.coal_plants = [
            {'running': False, 'power': 0.0, 'setpoint': 0.0, 'auto': False, 'max': 100.0},
            {'running': False, 'power': 0.0, 'setpoint': 0.0, 'auto': False, 'max': 100.0},
        ]
        self.coal_total_power = 0.0
        self.total_generation = 0.0

        # Constants
        self.SAMPLE_RATE = 44100
        self.OS = platform.system()
        if self.OS == "Windows":
            self.path = "Hydro 1\\"
        elif self.OS == "Darwin":
            self.path = "Hydro 1/"
        else:
            print("The code is broken (or you're on linux)")
        self.pid = PID(0.005, 0.001, 0, setpoint=0, output_limits=(0, 100))

        with open("demand\\day_001.txt" if self.OS=="Windows" else "demand/day_001.txt" if self.OS=="Darwin" else "", "r") as f:
            self.today_demand=f.readlines()

    def update_spillway(self):
        self.spill_1 = min(100, max(0, self.spill_1 + self.spill_open_1*self.hyd_coef))
        self.spill_2 = min(100, max(0, self.spill_2 + self.spill_open_2*self.hyd_coef))

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

                # TURBINE (auto)
                self.auto_state = load_data.get('auto_state', self.auto_state)
                self.auto_speed = load_data.get('auto_speed', self.auto_speed)
                self.oil_pump_source = load_data.get('oil_pump_source', self.oil_pump_source)

                # HYDRAULICS (supplementary)
                self.pump1_state = load_data.get('pump1_state', self.pump1_state)
                self.fan1_state = load_data.get('fan1_state', self.fan1_state)
                self.pump_selector = load_data.get('pump_selector', self.pump_selector)

                # SPILLWAY
                self.spill_open_1 = load_data.get('spill_open_1', self.spill_open_1)
                self.spill_open_2 = load_data.get('spill_open_2', self.spill_open_2)
                self.spill_1 = load_data.get('spill_1', self.spill_1)
                self.spill_2 = load_data.get('spill_2', self.spill_2)

                # DEMAND
                self.current_demand = load_data.get('current_demand', self.current_demand)
                self.seed = load_data.get('seed', self.seed)
                self.timestamp = load_data.get('timestamp', self.timestamp)
                self.prev_day = load_data.get('prev_day', self.prev_day)
                if 'today_demand' in load_data:
                    self.today_demand = load_data['today_demand']

                # HISTORY
                self.demand_history = load_data.get('demand_history', self.demand_history)
                self.water_history = load_data.get('water_history', self.water_history)
                self._last_history_period = load_data.get(
                    'last_history_period',
                    load_data.get('last_history_second',
                        load_data.get('last_history_minute', self._last_history_period))
                )

                # WIND FARM
                self.wind_speed = load_data.get('wind_speed', self.wind_speed)
                self.wind_turbines_state = load_data.get('wind_turbines_state', self.wind_turbines_state)
                self.wind_turbines_timer = load_data.get('wind_turbines_timer', self.wind_turbines_timer)
                self.wind_turbines_power = load_data.get('wind_turbines_power', self.wind_turbines_power)
                self.wind_total_power = load_data.get('wind_total_power', self.wind_total_power)
                self.wind_turbine_bias = load_data.get('wind_turbine_bias', self.wind_turbine_bias)
                # pad/truncate if count changed
                if len(self.wind_turbines_state) != self.wind_turbine_count:
                    self.wind_turbines_state = (self.wind_turbines_state + [0]*50)[:50]
                    self.wind_turbines_timer = (self.wind_turbines_timer + [0.0]*50)[:50]
                    self.wind_turbines_power = (self.wind_turbines_power + [0.0]*50)[:50]
                    self.wind_turbine_bias = (self.wind_turbine_bias + [0.0]*50)[:50]

                # COAL PLANTS
                loaded_coal = load_data.get('coal_plants', None)
                if isinstance(loaded_coal, list) and len(loaded_coal) == len(self.coal_plants):
                    for idx, data in enumerate(loaded_coal):
                        if isinstance(data, dict):
                            self.coal_plants[idx].update(data)
                self.coal_total_power = load_data.get('coal_total_power', self.coal_total_power)
                self.total_generation = load_data.get('total_generation', self.total_generation)
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
            'edg_started': self.edg_started,

            # TURBINE (auto)
            'auto_state': self.auto_state,
            'auto_speed': self.auto_speed,
            'oil_pump_source': self.oil_pump_source,

            # HYDRAULICS (supplementary)
            'pump1_state': self.pump1_state,
            'fan1_state': self.fan1_state,
            'pump_selector': self.pump_selector,

            # SPILLWAY
            'spill_open_1': self.spill_open_1,
            'spill_open_2': self.spill_open_2,
            'spill_1': self.spill_1,
            'spill_2': self.spill_2,

            # DEMAND
            'current_demand': self.current_demand,
            'seed': self.seed,
            'timestamp': self.timestamp,
            'prev_day': self.prev_day,
            'today_demand': self.today_demand,

            # HISTORY
            'demand_history': self.demand_history,
            'water_history': self.water_history,
            'last_history_period': self._last_history_period,

            # WIND FARM
            'wind_speed': self.wind_speed,
            'wind_turbines_state': self.wind_turbines_state,
            'wind_turbines_timer': self.wind_turbines_timer,
            'wind_turbines_power': self.wind_turbines_power,
            'wind_total_power': self.wind_total_power,
            'wind_turbine_bias': self.wind_turbine_bias,

            # COAL PLANTS
            'coal_plants': self.coal_plants,
            'coal_total_power': self.coal_total_power,
            'total_generation': self.total_generation
        }

        if not filename:
            if self.OS == "Windows":
                filename = f"{self.path}saves\\{datetime.now().strftime("%Y%m%d_%H%M%S")}"
            else:
                filename = f"{self.path}saves/{datetime.now().strftime("%Y%m%d_%H%M%S")}"
        else:
            filename = f"{self.path}{"saves\\" if self.OS == "Windows" else "saves/" if self.OS == "Darwin" else ""}{filename}"
        try:
            with open(filename, 'w') as f:
                json.dump(save_variables, f, indent=4)
            print(f"saved to {filename}")
        except Exception as e:
            print(f"file blew up: {e}")

    def read_log(self):
        if Path(f"{self.path}log.txt").is_file():
            with open(f"{self.path}log.txt", "r") as f:
                return f.readlines()
        else:
            Path("{self.path}log.txt").touch()

    def log(self, log = 'error'):
        with open(f"{self.path}log.txt", "a") as f:
            f.write(f"{round(self.sim_time, 5)}: {log}\n")

    def clear_log(self):
        with open(self.path, "w") as f:
            f.write("")

    
    def turbine_systems(self):
        self.oil_pump_power = max(0.0, min(100.0, self.oil_pump_power + self.oil_pump_direction)) if self.ac_bus_a else 0
        self.heat_exc_flow = max(0.0, min(100.0, self.heat_exc_flow + self.heat_exc_direction * self.hyd_coef))
        self.oil_temperature += (max(self.current_rpm-83.33, 0) / 416.67) * (1/self.oil_temperature)
        if self.oil_preheater and self.ac_bus_a:
            self.oil_temperature += 0.1 * (1/self.oil_temperature)
        if self.oil_pump_source == 0 and self.ac_bus_a:
            self.oil_temperature -= (self.oil_pump_power/100) * (self.heat_exc_flow/100) * 0.1 * ((self.oil_temperature-self.external_temp)/100)
        elif self.oil_pump_source == 1:
            self.oil_temperature -= (self.current_rpm/500) * (self.heat_exc_flow/100) * 0.1 * ((self.oil_temperature-self.external_temp)/100)
        elif self.dc_bus:
            self.oil_temperature -= (self.heat_exc_flow/100) * 0.3 * 0.1 * ((self.oil_temperature-self.external_temp)/100)

    def play_breaker_sound(self):
        if getattr(sys, "frozen", False):
            base = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
            playsound(os.path.join(base, "breaker.mp3"), block=False)
        elif self.OS == "Windows":
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

    def update_time(self):
        # updates the timestammp
        day = self.sim_time//86400
        hour = (self.sim_time-(day*86400))//3600
        minute = (self.sim_time-(day*86400)-(hour*3600))//60
        second = (self.sim_time-(day*86400)-(hour*3600)-(minute*60))
        self.timestamp = [day+1, hour, minute, second]

    def reload_demand_day(self):
        # Reloads today_demand from the demand file for the current day (used after loading a save)
        day = self.timestamp[0] if self.timestamp else 1
        sep = "\\" if self.OS == "Windows" else "/" if self.OS == "Darwin" else ""
        day_str = str(day).zfill(3)
        with open(f"demand{sep}day_{day_str}.txt", "r") as f:
            self.today_demand = f.readlines()
        self.prev_day = day

    def update_demand(self):
        # updates the demand
        if self.timestamp[0]!=self.prev_day:
            with open(f"demand{"\\" if self.OS == "Windows" else "/" if self.OS == "Darwin" else ""}day_{"0"*(3-len(str(self.timestamp[0])))}{self.timestamp[0]}.txt", "r") as f:
                self.today_demand = f.readlines()
        current_demand = float(self.today_demand[math.floor(self.timestamp[1]*60+self.timestamp[2])])
        next_demand = float(self.today_demand[min(math.floor(self.timestamp[1]*60+self.timestamp[2]+1), len(self.today_demand)-1)])
        self.current_demand = round(current_demand + (next_demand-current_demand)*(self.timestamp[3]/60), 2)
        if len(str(self.current_demand)) != 6:
            self.current_demand+=0.01
        self.prev_day = self.timestamp[0]

    def record_history(self):
        """Append one (demand, water_level) sample every update tick.

        The simulator runs near real-time (1 sim-sec per real second), so
        sampling each tick (~10 per second) lets the graph fill and scroll
        continuously instead of appearing frozen. HISTORY_LEN keeps a rolling
        window of the most recent samples; older ones scroll off to the left.
        """
        self.demand_history.append(self.current_demand)
        self.water_history.append(self.water_level)
        if len(self.demand_history) > self.HISTORY_LEN:
            self.demand_history.pop(0)
        if len(self.water_history) > self.HISTORY_LEN:
            self.water_history.pop(0)

    def clear_history(self):
        self.demand_history = []
        self.water_history = []
        self._last_history_period = -1

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
            self.flow_to_turbine[i] += (self.flow_to_turbine[i+1]-self.flow_to_turbine[i])*0.9

    def update_gate_pos(self):
        # opens/closes the gate
        if not self.is_emergency and self.gate_direction != 0:
            self.gate_opening = max(0.0, min(100.0, self.gate_opening + (self.gate_direction * 0.01 * (self.hyd_coef if self.gate_direction > 0 else 1))))
            if self.turbine_inflow_variation <= self.current_rpm/33.33:
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

        self.friction_coefficient = (self.current_rpm*0.6)*(self.damage/10)
        # This is calculated using the damage, oil temperature, rpm

        high_accel = False
        if not self.sync:
            target_rpm = ((self.flow_to_turbine[math.floor(self.gate_opening/100*40)]) * 12.0 - self.friction_coefficient) if not self.is_emergency else 0.0
            if target_rpm - self.current_rpm > 16.67:
                high_accel = True
                self.add_damage()
            self.current_rpm += (target_rpm - self.current_rpm) * 0.01 + (math.sin(random.randint(10,20)*self.sim_time)*self.turbine_inflow_variation*0.03)
            self.gen_island = True if self.current_rpm > 491.67 and self.current_rpm < 508.33 else False
        else:
            self.gen_island = True
            target_rpm = 500.0
            self.current_rpm += (target_rpm - self.current_rpm) * 0.1
            target_rpm = (self.flow_to_turbine[0] * 12.0) if not self.is_emergency else 0.0
            self.background_rpm += (target_rpm - self.background_rpm) * 0.005
        return high_accel

    def update_water_level(self):
        # Updates the reservoir water level very slowly
        water_outflow = (self.gate_opening + self.spill_1 + self.spill_2) * self.water_level/100
        net_flow = self.water_inflow - water_outflow
        self.water_level += net_flow * 0.00001
        self.water_level = max(0.0, min(100.0, self.water_level))
        return water_outflow

    def update_synchroscope(self, dt=0.05):
        # calculates phase difference when turbine is not synced
        grid_freq = 50.0
        if not self.sync:
            freq = (self.current_rpm / 10.0)
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
            self.power = ((self.background_rpm-500.0)/116.67)*100
        else:
            self.power = 0.0
        return self.power

    # ------------------------------------------------------------------
    # COAL POWER PLANTS
    # ------------------------------------------------------------------
    def update_coal_power(self):
        """Advance each coal plant's output.

        In auto mode a plant ramps its output toward the shortfall between the
        total grid demand and the power already supplied by hydro, wind and the
        other coal plants. In manual mode it holds the setpoint. Output ramps
        toward the target at COAL_RAMP_RATE and is clamped to [0, max].
        """
        total = 0.0
        for i, plant in enumerate(self.coal_plants):
            if not plant['running']:
                plant['power'] = 0.0
                continue

            if plant['auto']:
                other = self.power + self.wind_total_power
                for j, q in enumerate(self.coal_plants):
                    if j != i:
                        other += q['power']
                target = max(0.0, min(plant['max'], self.current_demand - other))
            else:
                target = plant['setpoint']

            diff = target - plant['power']
            step = max(-self.coal_ramp_rate, min(self.coal_ramp_rate, diff))
            plant['power'] = max(0.0, min(plant['max'], plant['power'] + step))
            total += plant['power']
        self.coal_total_power = total
        self.total_generation = self.power + self.wind_total_power + self.coal_total_power

    def coal_start(self, i):
        plant = self.coal_plants[i]
        plant['running'] = True
        if not plant['auto'] and plant['setpoint'] <= 0:
            plant['setpoint'] = 50.0
        self.log(f"Coal unit {i+1} started")

    def coal_stop(self, i):
        plant = self.coal_plants[i]
        plant['running'] = False
        plant['auto'] = False
        plant['power'] = 0.0
        self.log(f"Coal unit {i+1} stopped")

    def coal_set_power(self, i, mw):
        if not self.coal_plants[i]['running']:
            self.coal_start(i)
        self.coal_plants[i]['auto'] = False
        self.coal_plants[i]['setpoint'] = max(0.0, min(100.0, float(mw)))
        self.log(f"Coal unit {i+1} set to {self.coal_plants[i]['setpoint']:.1f} MW")

    def coal_set_auto(self, i, on=True):
        self.coal_plants[i]['auto'] = bool(on)
        self.log(f"Coal unit {i+1} auto = {'ON' if on else 'OFF'}")

    # Unit 1 wrappers (phone-friendly)
    def coal1_start(self): self.coal_start(0)
    def coal1_stop(self): self.coal_stop(0)
    def coal1_set_power(self, mw): self.coal_set_power(0, mw)
    def coal1_set_auto(self, on): self.coal_set_auto(0, on)

    # Unit 2 wrappers (phone-friendly)
    def coal2_start(self): self.coal_start(1)
    def coal2_stop(self): self.coal_stop(1)
    def coal2_set_power(self, mw): self.coal_set_power(1, mw)
    def coal2_set_auto(self, on): self.coal_set_auto(1, on)

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

    # --------------------------------------------------------------
    # WIND FARM
    # --------------------------------------------------------------
    def wind_power_for_speed(self, v):
        cut_in = 3.0
        rated = 12.0
        cut_out = 25.0
        if v < cut_in or v > cut_out:
            return 0.0
        if v >= rated:
            return self.wind_turbine_rating
        return self.wind_turbine_rating * ((v - cut_in) / (rated - cut_in)) ** 3

    def update_wind_speed(self, dt=0.1):
        step = random.uniform(-0.3, 0.3) * dt * 10
        self.wind_speed += step
        if self.wind_speed < 3.0:
            self.wind_speed += 0.3
        elif self.wind_speed > 16.0:
            self.wind_speed -= 0.3
        if random.random() < 0.005:
            self.wind_speed += random.uniform(-4, 4)
        self.wind_speed = max(0.0, min(30.0, self.wind_speed))

    def update_wind_turbines(self, dt=0.1):
        # slowly wander per-turbine local bias (spatial wind variation)
        for i in range(self.wind_turbine_count):
            self.wind_turbine_bias[i] += random.uniform(-0.04, 0.04) * dt
            if self.wind_turbine_bias[i] > 2.0:
                self.wind_turbine_bias[i] = 2.0
            elif self.wind_turbine_bias[i] < -2.0:
                self.wind_turbine_bias[i] = -2.0
        total = 0.0
        for i in range(self.wind_turbine_count):
            state = self.wind_turbines_state[i]
            timer = self.wind_turbines_timer[i]
            power = self.wind_turbines_power[i]
            if state == 1:  # STARTING — flash 50-70 s then go live
                timer -= dt
                if timer <= 0:
                    self.wind_turbines_state[i] = 2
                    self.wind_turbines_timer[i] = 0.0
                else:
                    self.wind_turbines_timer[i] = timer
                    power = 0.0
            elif state == 3:  # STOPPING — flash + high-inertia coast down
                timer -= dt
                # large rotor inertia — decay slowly toward 0
                tau_stop = 20.0
                power += (0.0 - power) * (dt / tau_stop)
                if power < 0.05:
                    power = 0.0
                if timer <= 0 and power <= 0.05:
                    self.wind_turbines_state[i] = 0
                    self.wind_turbines_timer[i] = 0.0
                    power = 0.0
                else:
                    self.wind_turbines_timer[i] = max(0.0, timer)
            elif state == 2:  # RUNNING — high rotational inertia
                local_wind = self.wind_speed + self.wind_turbine_bias[i] + random.uniform(-0.25, 0.25)
                local_wind = max(0.0, local_wind)
                target = self.wind_power_for_speed(local_wind)
                # torque/inertia → slow exponential approach
                tau = 28.0
                power += (target - power) * (dt / tau)
                # clamp tiny residual
                if abs(power - target) < 0.01:
                    power = target
            else:  # OFF
                power = 0.0
            self.wind_turbines_power[i] = max(0.0, power)
            total += self.wind_turbines_power[i]
        self.wind_total_power = total

    def wind_turbine_toggle(self, idx):
        if not 0 <= idx < self.wind_turbine_count:
            return
        state = self.wind_turbines_state[idx]
        if state == 0:  # OFF -> STARTING (random 50-70 s countdown)
            self.wind_turbines_state[idx] = 1
            self.wind_turbines_timer[idx] = float(random.randint(50, 70))
            self.wind_turbines_power[idx] = 0.0
        elif state == 2:  # RUNNING -> STOPPING
            self.wind_turbines_state[idx] = 3
            self.wind_turbines_timer[idx] = 60.0
        elif state in (1, 3):  # already flashing — ignore
            pass

    def toggle_wind_flash(self):
        self.wind_flash = not self.wind_flash

    def check_interlock(self):
        # checks if something is running when its not supposed to
        if self.current_rpm < 10:
            return False
        elif self.bypass_opening > 0 or self.drain_opening > 0:
            return True
        return False