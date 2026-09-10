from PyQt6.QtWidgets import QPushButton

class CustomButton(QPushButton):
    # Draws a button (link to function using lambda)
    def __init__(self, text, color="#555"):
        """
        A custom styled button.
        
        :param text: Text to display on the button
        :param color: Colour of the button
        """
        super().__init__(text)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: 2px solid #333;
                border-radius: 2px;
                padding: 10px;
                font-weight: bold;
            }}
            QPushButton:pressed {{
                background-color: #222;
                border: 1px solid #111;
            }}
            QPushButton:hover {{
                border: 2px solid #888;
            }}
        """)
