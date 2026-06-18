import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QPushButton, QScrollArea
from PyQt6.QtCore import Qt
import platform

class LoadWindow(QWidget):
    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        self.setWindowTitle("Load Dialogue")
        self.setStyleSheet("background-color: #1a1a1a; color: white;")
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
                background-color: #121212;
                color: white;
                border: 2px solid #555;
                border-radius: 4px;
                padding: 5px;
                font-weight: bold;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #2a2a2a;
            }
            QListWidget::item:hover {
                background-color: #2a2a2a;
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
        
        self.btn_refresh = QPushButton("REFRESH LIST")
        self.btn_refresh.setStyleSheet("""
            QPushButton { background-color: #444; color: white; border-radius: 4px; padding: 10px; font-weight: bold; }
            QPushButton:hover { border: 1px solid #999; }
        """)
        self.btn_refresh.clicked.connect(self.populate_files)
        
        self.btn_load = QPushButton("LOAD SELECTED")
        self.btn_load.setStyleSheet("""
            QPushButton { background-color: #0066cc; color: white; border-radius: 4px; padding: 10px; font-weight: bold; }
            QPushButton:hover { border: 1px solid #999; }
        """)
        self.btn_load.clicked.connect(self.handle_load)

        button_layout.addWidget(self.btn_refresh)
        button_layout.addWidget(self.btn_load)
        main_layout.addLayout(button_layout)

        # Allow user to double-click an item in the list to load it instantly
        self.file_list.itemDoubleClicked.connect(self.handle_load)

        # Scan the folder right away when the window opens
        self.populate_files()

    def populate_files(self):
        """Scans the directory specified in the engine and lists all JSON saves."""
        self.file_list.clear()
        
        try:
            if not os.path.exists(self.save_path):
                os.makedirs(self.save_path)
            
            files = [f for f in os.listdir(self.save_path) if f.endswith('.json')]
            files.sort() # alphabetical sort so its clean
            
            if not files:
                self.file_list.addItem("--- No save files found ---")
                self.file_list.item(0).setFlags(Qt.ItemFlag.NoItemFlags) # make it unclickable
            else:
                self.file_list.addItems(files)
                
        except Exception as e:
            self.file_list.addItem(f"Error reading directory: {e}")

    def handle_load(self):
        """Grabs the highlighted file and throws it over to the engine to load."""
        selected_items = self.file_list.selectedItems()
        if not selected_items:
            return
            
        filename = selected_items[0].text()
        
        if filename.startswith("---") or filename.startswith("Error"):
            return
            
        if hasattr(self.engine, 'load_file'):
            self.engine.load_file(f"{self.save_path}{filename}")
            print(f"Loaded {self.save_path}{filename}")
            self.hide()
        else:
            print("code explode")

    def closeEvent(self, event):
        self.hide()
        event.ignore()