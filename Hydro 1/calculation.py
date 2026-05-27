import math
import random
import numpy as np
from playsound3 import playsound

class SimulationEngine:
    def __init__(self):
        # Simulation variables

        # timing
        self.sim_time = 0.0

        # generation
        self.gen_phase = 0.0
        self.grid_phase = 0.0
        self.phase_diff = 0.0
        self.phase_diff_prev = 0.0

        #water
        self.water_inflow = 50.0
        self.water_level = 70.0
        self.sync = False
        self.gate_opening = 0.0
        self.is_emergency = False
        self.gate_direction = 0.0

        # turbine
        self.current_rpm = 0.0
        self.background_rpm = 0.0
        self.power = 0.0
        self.turbine_inflow_variation = 0.0
        self.damage = 0.0
        self.flow_to_turbine = [0.0 for _ in range(50)]
        self.turbine_water_level = 0.0
        self.bypass_direction = 0.0
        self.bypass_opening = 0.0
        self.drain_direction = 0.0
        self.drain_opening = 0.0
        self.excitation = 0.0
        self.excitation_direction = 0.0
        self.friction_coefficient = 0


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
        
        # Breakers: True = CLOSED (ON), False = OPEN (OFF)
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
        self.battery_charge = 5.0  # Battery charge level (0-100%)
        self.gen_island = False

        # EDG
        self.edg_started = False
        
        # Constants
        self.SAMPLE_RATE = 44100
    
    def update_battery(self):
        if self.breaker_lv1em:
            if self.battery_charge > 0:
                self.battery_charge -= 0.1
            else:
                self.dc_bus = False
        elif self.breaker_dc1dca or self.breaker_dc1dcb:
            self.battery_charge += 0.05

    def update_res_temp(self):
        if self.pre1_on:
            self.res_temp_1 += 0.1
        elif self.pump1_state > 0:
            pass
        else:
            if self.temp_decrease_timer_1 > 0:
                self.temp_decrease_timer_1 -= 1
            else:
                self.res_temp_1 -= 0.1
                self.temp_decrease_timer_1 = 60
        
        if self.pre2_on:
            self.res_temp_2 += 0.1
        elif self.pump2_state > 0:
            pass
        else:
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
        self.pump1_state = 0
        self.fan1_state = 0
    
    def ac_bus_b_unpowered(self):
        self.pump2_state = 0
        self.fan2_state = 0
    
    def dc_bus_unpowered(self):
        # disconnect auto controls here
        pass

    def breaker_event(self, state, breaker):
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
        print(type, breaker)
        playsound("Hydro 1\\breaker.mp3", block=False)
        # bus b only has 1 input so no need for interlock


    def update_water_flow(self):
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
        self.flow_to_turbine[len(self.flow_to_turbine)-1] = self.gate_opening
        for i in range(0, len(self.flow_to_turbine)-1):
            self.flow_to_turbine[i] += (self.flow_to_turbine[i+1]-self.flow_to_turbine[i])

    def update_gate_pos(self):
        if not self.is_emergency and self.gate_direction != 0:
            self.gate_opening = max(0.0, min(100.0, self.gate_opening + (self.gate_direction * 0.01 * (self.hyd_coef if self.gate_direction > 0 else 1))))
            if self.turbine_inflow_variation <= self.current_rpm/200:
                self.turbine_inflow_variation += 0.1

    def update_drain_bypass_pos(self):
        self.drain_opening = max(0.0, min(100.0, self.drain_opening + (self.drain_direction * (self.hyd_coef if self.drain_direction > 0 else 1))))
        self.bypass_opening = max(0.0, min(100.0, self.bypass_opening + (self.bypass_direction * (self.hyd_coef if self.bypass_direction > 0 else 1))))

    def update_turbine_inflow(self):
        if self.turbine_inflow_variation > 0.09:
            self.turbine_inflow_variation -= 0.02
        else:
            self.turbine_inflow_variation = 0.0

    def update_hydraulics(self):
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
        self.friction_coefficient = self.current_rpm*0.1
        # This is calculated using the damage, oil quality, rpm

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
        water_outflow = self.gate_opening
        net_flow = self.water_inflow - water_outflow
        self.water_level += net_flow * 0.00001
        self.water_level = max(0.0, min(100.0, self.water_level))
        return water_outflow

    def update_synchroscope(self, dt=0.05):
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
        if self.sync:
            self.power = ((self.background_rpm-3000)/700)*100
        else:
            self.power = 0.0
        return self.power

    def add_damage(self, amount=0.1):
        if self.damage < 100:
            self.damage += amount

    def damage_system(self):
        if self.damage > 80 and random.randint(0, 50) == 0:
            self.is_emergency = True
            self.current_rpm = 0.0
            return True
        return False

    def update_systems(self, dt=0.05):
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
        if pump_num == 1 and self.pump1_state == 0 and self.res_temp_1 >= 35 and self.res_temp_1 <= 42 and self.fan1_state == 2 and self.ac_bus_a:
            self.pump1_state = 1
            self.pump1_timer = 0.0
        elif pump_num == 2 and self.pump2_state == 0 and self.res_temp_2 >= 35 and self.res_temp_2 <= 42 and self.fan2_state == 2 and self.ac_bus_b:
            self.pump2_state = 1
            self.pump2_timer = 0.0

    def stop_pump(self, pump_num):
        if pump_num == 1:
            self.pump1_state = 0
            self.pump1_timer = 0.0
        elif pump_num == 2:
            self.pump2_state = 0
            self.pump2_timer = 0.0

    def start_fan(self, fan_num):
        if fan_num == 1 and self.fan1_state == 0 and self.ac_bus_a:
            self.fan1_state = 1
            self.fan1_timer = 0.0
        elif fan_num == 2 and self.fan2_state == 0 and self.ac_bus_b:
            self.fan2_state = 1
            self.fan2_timer = 0.0

    def stop_fan(self, fan_num):
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
        if self.current_rpm < 10:
            self.turbine_water_level += (self.bypass_opening * .01) - (self.drain_opening * .01)
        
        self.turbine_water_level = max(0.0, min(100.0, self.turbine_water_level))

    def update_pump_reservoir(self):
        # Pump 2 increases reservoir level only when RUNNING (state 2)
        if self.pump2_state == 2:
            self.pump2_flow += (1.0 - self.pump2_flow) * 0.1
        else:
            self.pump2_flow += (0.0 - self.pump2_flow) * 0.1
        self.water_level += self.pump2_flow * 0.0001
        self.water_level = min(100.0, self.water_level)

    def check_interlock(self):
        if self.current_rpm < 10:
            return False
        elif self.bypass_opening > 0 or self.drain_opening > 0:
            return True
        return False
