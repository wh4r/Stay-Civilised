from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt
from buttons import CustomButton
from gauges import UniversalGauge
from annunciators import Annunciator

class TurbineWindow(QWidget):
    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        self.setWindowTitle("Turbine Systems")
        self.setStyleSheet("background-color: #1a1a1a; color: white;")
        self.setFixedSize(1000, 700)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        main_layout.addWidget(QLabel("<h2>Turbine Panel</h2>", alignment=Qt.AlignmentFlag.AlignCenter))

        # --- Gauges ---
        gauge_layout = QHBoxLayout()
        self.rpm_gauge = UniversalGauge(title="RPM", unit="%", min_val=0, max_val=4000)
        self.excitation_guage = UniversalGauge(title="Excitation", unit="V", min_val=0, max_val=600)
        self.oil_temperature = UniversalGauge(title="Oil temp", unit="°", min_val=20, max_val=100)
        self.pump = UniversalGauge(title="Pump", unit="%", min_val=0, max_val=100)
        self.exchanger = UniversalGauge(title="Exchanger valve", unit="%", min_val=0, max_val=100)
        gauge_layout.addWidget(self.rpm_gauge)
        gauge_layout.addWidget(self.excitation_guage)
        gauge_layout.addWidget(self.oil_temperature)
        gauge_layout.addWidget(self.pump)
        gauge_layout.addWidget(self.exchanger)
        main_layout.addLayout(gauge_layout)
        main_layout.addWidget(self.create_separator())


        # --- Excitation ---
        excitation_group = QHBoxLayout()
        excitation_group.addWidget(QLabel("<b>EXCITATION</b>"))
        self.excitation_increase = CustomButton("+")
        self.excitation_stop = CustomButton("x")
        self.excitation_decrease = CustomButton("-")
        excitation_group.addWidget(self.excitation_decrease)
        excitation_group.addWidget(self.excitation_stop)
        excitation_group.addWidget(self.excitation_increase)
        main_layout.addLayout(excitation_group)

        # --- Pump select ---
        pump_select_group = QHBoxLayout()
        pump_select_group.addWidget(QLabel(" "))
        self.pump_elec = CustomButton("ELEC.")
        self.pump_shaft = CustomButton("SHAFT")
        self.pump_em = CustomButton("EM.")
        pump_select_group.addWidget(self.pump_elec)
        pump_select_group.addWidget(self.pump_shaft)
        pump_select_group.addWidget(self.pump_em)
        main_layout.addLayout(pump_select_group)

        # --- Oil pump ---
        pump_group = QHBoxLayout()
        pump_group.addWidget(QLabel("<b>ELEC. OIL PUMP</b>"))
        self.pump_increase = CustomButton("+")
        self.pump_stop = CustomButton("x")
        self.pump_decrease = CustomButton("-")
        pump_group.addWidget(self.pump_decrease)
        pump_group.addWidget(self.pump_stop)
        pump_group.addWidget(self.pump_increase)
        main_layout.addLayout(pump_group)

        # --- Heat exchanger ---
        exchanger_group = QHBoxLayout()
        exchanger_group.addWidget(QLabel("<b>HEAT EXCHANGER VALVE</b>"))
        self.exchanger_increase = CustomButton("+")
        self.exchanger_stop = CustomButton("x")
        self.exchanger_decrease = CustomButton("-")
        exchanger_group.addWidget(self.exchanger_decrease)
        exchanger_group.addWidget(self.exchanger_stop)
        exchanger_group.addWidget(self.exchanger_increase)
        main_layout.addLayout(exchanger_group)

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

        # Preheat
        preheat_layout = QHBoxLayout()
        self.preheat_annunc = Annunciator("PREHEAT", persistent=False)
        self.preheat_button = CustomButton("PREHEAT")
        
        preheat_layout.addWidget(self.preheat_annunc)
        preheat_layout.addWidget(self.preheat_button)

        main_layout.addLayout(preheat_layout)


        # --- Functions ---

        self.excitation_increase.clicked.connect(lambda: setattr(self.engine, 'excitation_direction', 1))
        self.excitation_stop.clicked.connect(lambda: setattr(self.engine, 'excitation_direction', 0))
        self.excitation_decrease.clicked.connect(lambda: setattr(self.engine, 'excitation_direction', -1))

        self.pump_elec.clicked.connect(lambda: setattr(self.engine, 'oil_pump_source', 0))
        self.pump_shaft.clicked.connect(lambda: setattr(self.engine, 'oil_pump_source', 1))
        self.pump_em.clicked.connect(lambda: setattr(self.engine, 'oil_pump_source', 2))

        self.pump_increase.clicked.connect(lambda: setattr(self.engine, 'oil_pump_direction', 1))
        self.pump_stop.clicked.connect(lambda: setattr(self.engine, 'oil_pump_direction', 0))
        self.pump_decrease.clicked.connect(lambda: setattr(self.engine, 'oil_pump_direction', -1))

        self.exchanger_increase.clicked.connect(lambda: setattr(self.engine, 'heat_exc_direction', 1))
        self.exchanger_stop.clicked.connect(lambda: setattr(self.engine, 'heat_exc_direction', 0))
        self.exchanger_decrease.clicked.connect(lambda: setattr(self.engine, 'heat_exc_direction', -1))

        self.decrease_drain.clicked.connect(lambda: setattr(self.engine, 'drain_direction', -1))
        self.stop_drain.clicked.connect(lambda: setattr(self.engine, 'drain_direction', 0))
        self.increase_drain.clicked.connect(lambda: setattr(self.engine, 'drain_direction', 1))

        self.decrease_bypass.clicked.connect(lambda: setattr(self.engine, 'bypass_direction', -1))
        self.stop_bypass.clicked.connect(lambda: setattr(self.engine, 'bypass_direction', 0))
        self.increase_bypass.clicked.connect(lambda: setattr(self.engine, 'bypass_direction', 1))


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


    
    def closeEvent(self, event):
        self.hide()
        event.ignore()
