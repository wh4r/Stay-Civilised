from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt
from input import CustomInputField

class ConsoleWindow(QWidget):
    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        self.setWindowTitle("Debug console")
        self.setStyleSheet("background-color: #808080; color: #222222;")
        self.setFixedSize(500, 150)
        self.text = 'None'

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        main_layout.addWidget(QLabel("<h2>Console</h2>", alignment=Qt.AlignmentFlag.AlignCenter))

        layout = QHBoxLayout()

        self.name_input = CustomInputField(
            placeholder_text="Enter command...", 
            button_text="RUN", 
            color="#0066cc", 
            callback=lambda val: self.handle_variable_change(val)
        )
        layout.addWidget(self.name_input)
        main_layout.addLayout(layout)

        self.result = QLabel(self.text)
        main_layout.addWidget(self.result)

    def handle_variable_change(self, command):
        command = command.split(" ")
        name = command[0].strip()
        try:
            if name == "set_val":
                try:
                    setattr(self.engine, command[1].strip(), command[2])
                    self.text = f"{name} set to {command[1].strip()}"
                except Exception as e:
                    self.text = f"Error: {e}"
            elif name == "damage":
                self.engine.damage = int(command[1].strip())
                self.text = f"Damage set to {command[1].strip()}"
            else:
                self.text = "Error: unrecognised command"
            self.result.setText(self.text)
        except Exception as e:
            self.result.setText(f"Error: {e}")

    def closeEvent(self, event):
        self.hide()
        event.ignore()