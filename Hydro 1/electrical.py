from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QGridLayout,
    QSizePolicy
)

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

from buttons import CustomButton
from annunciators import Annunciator
from gauges import UniversalGauge


class ElectricalWindow(QWidget):

    def __init__(self, engine):
        super().__init__()

        self.engine = engine

        self.setWindowTitle("Breaker Panel")
        self.setStyleSheet("background-color: #121212; color: white;")
        self.setFixedSize(900, 470)

        # ================= MAIN LAYOUT =================
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)

        self.setLayout(main_layout)

        # ================= HORIZONTAL CONTENT =================
        content_layout = QHBoxLayout()
        content_layout.setSpacing(15)

        main_layout.addLayout(content_layout)

        # ======================================================
        # LEFT SIDE
        # ======================================================

        left_panel = QVBoxLayout()
        left_panel.setSpacing(8)

        content_layout.addLayout(left_panel, stretch=3)

        # Separator
        left_panel.addWidget(self.create_separator())

        # ================= HEADER =================
        header_layout = QHBoxLayout()
        panel_title = QLabel("<h2>ELECTRICAL BREAKER PANEL</h2>")
        panel_title.setStyleSheet("""
            color: #00e6e6;
            font-family: 'Segoe UI';
            font-weight: bold;
            margin-left: 12px;
        """)

        header_layout.addWidget(panel_title)
        header_layout.addStretch()
        self.battery_charge = UniversalGauge("DC Battery Charge",0,100,"%")

        self.battery_charge.setFixedSize(120, 120)
        header_layout.addWidget(self.battery_charge)
        left_panel.addLayout(header_layout)
        left_panel.addWidget(self.create_separator())

        # ================= GRID =================
        grid_layout = QGridLayout()

        grid_layout.setSpacing(8)
        grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        left_panel.addLayout(grid_layout)

        # ======================================================
        # RIGHT SIDE
        # ======================================================

        right_panel = QVBoxLayout()
        right_panel.setSpacing(12)

        content_layout.addLayout(right_panel, stretch=2)

        # ================= IMAGE =================
        self.sld_label = QLabel()

        pixmap = QPixmap("Hydro 1/elec_layout.png")

        if not pixmap.isNull():

            self.sld_label.setPixmap(
                pixmap.scaled(
                    420,
                    820,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
            )

        else:

            self.sld_label.setText(
                "<h2>[ Image elec_layout.png Not Found ]</h2>"
            )

            self.sld_label.setStyleSheet(
                "color: #ff3333;"
            )

        self.sld_label.setAlignment(
            Qt.AlignmentFlag.AlignTop
        )

        right_panel.addWidget(self.sld_label)

        # ======================================================
        # BREAKERS
        # ======================================================

        self.breakers_info = [
            # gen
            ("HV1GE", "breaker_hv1ge"),
            ("HV1GA", "breaker_hv1ga"),
            ("HV1GB", "breaker_hv1gb"),
            # startup
            ("HV1S1", "breaker_hv1s1"),
            ("HV1S2", "breaker_hv1s2"),
            # ac/dc
            ("DC1DCA", "breaker_dc1dca"),
            ("DC1DCB", "breaker_dc1dcb"),
            # edg
            ("LV1DG", "breaker_lv1dg"),
            ("LV1DGS", "breaker_lv1dgs"),
            # bat
            ("LV1EM", "breaker_lv1em"),
        ]

        self.status_indicators = {}

        # ======================================================
        # BUILD CARDS
        # ======================================================

        for idx, (label_text, var_name) in enumerate(self.breakers_info):

            card, status = self.create_breaker_card(
                label_text,
                var_name
            )

            # LAST BREAKER GOES UNDER IMAGE
            if idx == len(self.breakers_info) - 1:

                right_panel.addWidget(card)

            else:

                row = idx // 3
                col = idx % 3

                grid_layout.addWidget(card, row, col)

            self.status_indicators[var_name] = status

    # ==========================================================
    # BREAKER CARD
    # ==========================================================

    def create_breaker_card(self, label_text, var_name):
        card = QFrame()
        card.setFixedHeight(92)

        card.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Fixed
        )

        card.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border: 1px solid #333;
                border-radius: 5px;
                padding: 2px;
            }

            QFrame:hover {
                border: 1px solid #00cccc;
            }
        """)

        layout = QVBoxLayout(card)

        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)

        # ================= LABEL =================

        name_label = QLabel(f"<b>{label_text}</b>")

        name_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        name_label.setStyleSheet("""
            font-size: 10px;
            color: #dddddd;
            border: none;
            font-family: 'Segoe UI';
        """)

        layout.addWidget(name_label)

        # ================= STATUS =================

        status = Annunciator(
            label_text.split(" ")[0],
            "red",
            persistent=False
        )

        status.setFixedSize(110, 20)
        status_layout = QHBoxLayout()
        status_layout.addStretch()
        status_layout.addWidget(status)
        status_layout.addStretch()
        layout.addLayout(status_layout)

        # ================= BUTTONS =================

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(4)

        btn_close = CustomButton(
            "CLOSE",
            color="#800"
        )

        btn_open = CustomButton(
            "OPEN",
            color="#006633"
        )

        btn_close.setFixedHeight(18)
        btn_open.setFixedHeight(18)

        btn_close.setStyleSheet("""
            QPushButton {
                background-color: #880000;
                color: white;
                border: 1px solid #aa0000;
                border-radius: 3px;
                font-weight: bold;
                font-size: 9px;
            }

            QPushButton:hover {
                border: 1px solid #ff3333;
            }

            QPushButton:pressed {
                background-color: #550000;
            }
        """)

        btn_open.setStyleSheet("""
            QPushButton {
                background-color: #006633;
                color: white;
                border: 1px solid #008844;
                border-radius: 3px;
                font-weight: bold;
                font-size: 9px;
            }

            QPushButton:hover {
                border: 1px solid #33cc66;
            }

            QPushButton:pressed {
                background-color: #003311;
            }
        """)

        btn_layout.addWidget(btn_close)
        btn_layout.addWidget(btn_open)

        layout.addLayout(btn_layout)

        # ================= SIGNALS =================

        btn_close.clicked.connect(
            lambda: (
                setattr(self.engine, var_name, True),
                self.engine.breaker_event(True, var_name)
            )
        )

        btn_open.clicked.connect(
            lambda: (
                setattr(self.engine, var_name, False),
                self.engine.breaker_event(False, var_name)
            )
        )

        return card, status

    # ==========================================================
    # SEPARATOR
    # ==========================================================

    def create_separator(self):
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("""
            background-color: #2a2a2a;
            max-height: 1px;
        """)
        return line

    # ==========================================================
    # UPDATE UI
    # ==========================================================

    def update_ui(self):
        for var_name, status in self.status_indicators.items():
            val = getattr(self.engine, var_name, True)
            status.active = val
            status.blink = val
            status.update_style()
        self.battery_charge.set_value(
            self.engine.battery_charge
        )

    # ==========================================================
    # CLOSE EVENT
    # ==========================================================

    def closeEvent(self, event):
        self.hide()
        event.ignore()