from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt
from input import CustomInputField

class ConsoleWindow(QWidget):
    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        self.setWindowTitle("Debug console")
        self.setStyleSheet("background-color: #1a1a1a; color: white;")
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
        print(name)
        try:
            if name == "set_val":
                setattr(self.engine, command[1].strip(), command[2])
                self.text = f"{name} set to {command[1].strip()}"
                print('a')
            elif name == "damage":
                self.engine.damage = int(command[1].strip())
                self.text = f"Damage set to {command[1].strip()}"
                print('a')
            else:
                self.text = "Error: unrecognised command"
            self.result.setText(self.text)
        except Exception as e:
            self.result.setText(f"e")

    def closeEvent(self, event):
        self.hide()
        event.ignore()