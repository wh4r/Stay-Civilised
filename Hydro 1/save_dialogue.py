from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt
from input import CustomInputField

class SaveWindow(QWidget):
    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        self.setWindowTitle("Save Dialogue")
        self.setStyleSheet("background-color: #808080; color: #222222;")
        self.setFixedSize(500, 100)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        main_layout.addWidget(QLabel("<h2>Save file</h2>", alignment=Qt.AlignmentFlag.AlignCenter))

        layout = QHBoxLayout()

        self.name_input = CustomInputField(
            placeholder_text="Filename...", 
            button_text="SAVE", 
            color="#0066cc", 
            callback=lambda val: self.handle_variable_change(val)
        )
        layout.addWidget(self.name_input)
        main_layout.addLayout(layout)

    def handle_variable_change(self, text_string):
        self.engine.save_file(f"{text_string}.json")
        self.hide()
        
    def closeEvent(self, event):
        self.hide()
        event.ignore()