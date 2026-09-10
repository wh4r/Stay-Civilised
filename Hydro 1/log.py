import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QPushButton, QScrollArea
from PyQt6.QtCore import Qt
import platform

class LogWindow(QWidget):
    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        self.setWindowTitle("Load Dialogue")
        self.setStyleSheet("background-color: #808080; color: #222222;")
        self.setFixedSize(500, 400) # bit taller to fit the list nicely

        this_os = platform.system()
        if this_os == "Windows":
            self.save_path = "Hydro 1\\saves\\"
        elif this_os == "Darwin":
            self.save_path = "Hydro 1/saves/"
        else:
            print("The code is broken (or you're on linux)")
            self.save_path = ''

        # Main layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        main_layout.addWidget(QLabel("<h2>Load Simulation Save</h2>", alignment=Qt.AlignmentFlag.AlignCenter))

        # 1. Create the List Widget to hold the files
        self.file_list = QListWidget()
        self.file_list.setStyleSheet("""
            QListWidget {
                background-color: #6a6a6a;
                color: #222222;
                border: 2px solid #444;
                border-radius: 2px;
                padding: 5px;
                font-weight: bold;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #555;
            }
            QListWidget::item:hover {
                background-color: #7a7a7a;
            }
            QListWidget::item:selected {
                background-color: #0066cc;
                color: white;
            }
        """)

        # 2. Wrap it inside a QScrollArea so it can handle a massive list of saves
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.file_list)
        scroll_area.setStyleSheet("border: none; background: transparent;")
        main_layout.addWidget(scroll_area)

        # 3. Bottom controls (Refresh and Load buttons)
        button_layout = QHBoxLayout()
        
        self.btn_refresh = QPushButton("REFRESH")
        self.btn_refresh.setStyleSheet("""
            QPushButton { background-color: #555; color: white; border-radius: 2px; padding: 10px; font-weight: bold; border: 2px solid #444; }
            QPushButton:hover { border: 2px solid #888; }
        """)
        self.btn_refresh.clicked.connect(self.populate_files)

        button_layout.addWidget(self.btn_refresh)
        main_layout.addLayout(button_layout)

        # Scan the folder right away when the window opens
        self.populate_files()

    def populate_files(self):
        """Scans the directory specified in the engine and lists all JSON saves."""
        self.file_list.clear()

        log = self.engine.read_log()

        if not log:
            self.file_list.addItem("--- No logs found ---")
            self.file_list.item(0).setFlags(Qt.ItemFlag.NoItemFlags)
        else:
            self.file_list.addItems(log)

    def closeEvent(self, event):
        self.hide()
        event.ignore()