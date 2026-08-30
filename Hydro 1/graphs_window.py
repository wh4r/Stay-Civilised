from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel

from graph import GraphWidget


class GraphsWindow(QWidget):
    """Window showing live historical graphs (demand + forebay level).

    Both graphs read their arrays from the engine's rolling history, so they
    display the past hour (60 samples, one per simulated minute).
    """

    def __init__(self, engine):
        super().__init__()
        self.engine = engine

        self.setWindowTitle("Historical Graphs")
        self.setStyleSheet("background-color: #121212; color: white;")
        self.resize(720, 360)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        self.setLayout(main_layout)

        main_layout.addWidget(QLabel("<h2>Historical Data (Past Hour)</h2>"))

        row = QHBoxLayout()
        self.demand_graph = GraphWidget("Demand", "kW", max_points=self.engine.HISTORY_LEN,
                                        color="#00ff9c")
        self.water_graph = GraphWidget("Forebay Level", "%", min_y=0, max_y=100,
                                       max_points=self.engine.HISTORY_LEN, color="#3aa0ff")
        row.addWidget(self.demand_graph)
        row.addWidget(self.water_graph)
        main_layout.addLayout(row, 1)

    def update_ui(self):
        self.demand_graph.set_data(self.engine.demand_history)
        self.water_graph.set_data(self.engine.water_history)

    def closeEvent(self, event):
        self.hide()
        event.ignore()
