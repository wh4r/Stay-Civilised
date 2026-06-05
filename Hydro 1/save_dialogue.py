from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt
from input import CustomInputField

class SaveWindow(QWidget):
    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        self.setWindowTitle("Save Dialogue")
        self.setStyleSheet("background-color: #1a1a1a; color: white;")
        self.setFixedSize(500, 100)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        main_layout.addWidget(QLabel("<h2>Save file</h2>", alignment=Qt.AlignmentFlag.AlignCenter))

        layout = QHBoxLayout()

        # The callback can safely point to self.handle_variable_change now
        self.name_input = CustomInputField(
            placeholder_text="Filename...", 
            button_text="SAVE", 
            color="#0066cc", 
            callback=lambda val: self.handle_variable_change(val)
        )
        layout.addWidget(self.name_input)
        main_layout.addLayout(layout)

    # SHIFTED OUTSIDE: This is now a proper method of the TurbineWindow class
    def handle_variable_change(self, text_string):
        self.engine.save_file(f"{text_string}.json")
        self.hide()
        
    def closeEvent(self, event):
        self.hide()
        event.ignore()