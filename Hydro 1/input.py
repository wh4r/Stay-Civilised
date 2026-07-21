from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton

class CustomInputField(QWidget):
    def __init__(self, placeholder_text="Enter value...", button_text="Set", color="#008080", callback=None):
        """
        A custom styled input field with a submit button.
        
        :param placeholder_text: Light gray text inside the empty box
        :param button_text: What the submit button says
        :param color: The theme color for the button (defaults to teal/teal-gray)
        :param callback: The function to run when submitted, receives the string value
        """
        super().__init__()
        self.callback = callback
        
        # Horizontal layout to keep the entry box and button side-by-side
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0) # stops it messing up your main layout margins
        layout.setSpacing(6)
        
        # 1. The Entry Field
        self.entry = QLineEdit()
        self.entry.setPlaceholderText(placeholder_text)
        self.entry.setStyleSheet("""
            QLineEdit {
                background-color: #1e1e1e;
                color: white;
                border: 2px solid #555;
                border-radius: 4px;
                padding: 8px;
                font-weight: bold;
            }
            QLineEdit:focus {
                border: 2px solid #888; /* lights up slightly when clicked into */
            }
        """)
        
        # 2. The Submit Button
        self.btn = QPushButton(button_text)
        self.btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: 1px solid #666;
                border-radius: 4px;
                padding: 8px 15px;
                font-weight: bold;
            }}
            QPushButton:pressed {{
                background-color: #222;
            }}
            QPushButton:hover {{
                border: 1px solid #999;
            }}
        """)
        
        # Hook up both the button click AND hitting 'Enter' in the text box to submit
        self.btn.clicked.connect(self.submit_value)
        self.entry.returnPressed.connect(self.submit_value)
        
        # Stuff them into the widget layout
        layout.addWidget(self.entry)
        layout.addWidget(self.btn)

    def set_placeholder(self, val):
        self.entry.setPlaceholderText(val)
        self.entry.update()

    def submit_value(self):
        text_val = self.entry.text()
        if self.callback:
            self.callback(text_val)
        
    def clear(self):
        self.entry.clear()