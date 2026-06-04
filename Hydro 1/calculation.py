import math
import random
from playsound3 import playsound
import platform

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

    def play_breaker_sound(self):
        if self.OS == "Windows":
            playsound("Hydro 1\\breaker.mp3", block=False)
        elif self.OS == "Darwin":
            playsound("Hydro 1/breaker.mp3", block=False)
        else:
            print("The code is broken (or you're on linux)")

    def save_file(self, filename):
        pass

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
        # i have no idea why this is here but the code will explode if this is removed
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