from PyQt6.QtWidgets import QPushButton

class CustomButton(QPushButton):
    # Draws a button (link to function using lambda)
    def __init__(self, text, color="#444"):
        super().__init__(text)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: 1px solid #666;
                border-radius: 4px;
                padding: 10px;
                font-weight: bold;
            }}
            QPushButton:pressed {{
                background-color: #222;
            }}
            QPushButton:hover {{
                border: 1px solid #999;
            }}
        """)
