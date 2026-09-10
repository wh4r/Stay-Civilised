from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt

class Annunciator(QLabel):
    def __init__(self, text, alert_color="red", persistent=True, sound_freq=None):
        """
        A custom styled annunciator.
        
        :param text: Text to display on the annunciator
        :param alert_color: Color of the annunciator when it is active
        :param persistent: Whether the annunciator needs to be acknowledged
        :param sound_freq: Frequency of sound played when annunciator is active
        """
        super().__init__(text)
        self.alert_color = alert_color
        self.active = False
        self.needs_ack = False
        self.blink = True
        self.persistent = persistent
        self.sound_freq = sound_freq
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFixedSize(120, 40)
        self.update_style()

    # Run to turn on/off the annunciator
    def set_state(self, active):
        """Set alarm state."""
        if self.persistent:
            if active and not self.active:
                self.needs_ack = True
        else:
            self.blink = True if active else False
        self.active = active
        self.update_style()

    # Resets annunciator
    def acknowledge(self):
        self.needs_ack = False
        self.update_style()

    # Blinks the annunciator
    def toggle_blink(self):
        if self.active:
            self.blink = not self.blink
        else:
            self.blink = False
        self.update_style()

    # Updates the style of the annunciator
    def update_style(self):
        if self.active:
            if self.blink:
                if self.alert_color == "red":
                    bg = "#cc2222"
                    fg = "white"
                elif self.alert_color == "orange":
                    bg = "#ccaa00"
                    fg = "#222222"
                elif self.alert_color == "green":
                    bg = "#22aa44"
                    fg = "white"
                else:
                    bg = "#888888"
                    fg = "white"
            else:
                bg = "#e0e0d8"
                fg = "#555555"
        elif self.persistent and self.needs_ack:
            if self.alert_color == "red":
                bg = "#cc2222"
                fg = "white"
            elif self.alert_color == "orange":
                bg = "#ccaa00"
                fg = "#222222"
            elif self.alert_color == "green":
                bg = "#22aa44"
                fg = "white"
            else:
                bg = "#888888"
                fg = "white"
        else:
            bg = "#e0e0d8"
            fg = "#888888"

        self.setStyleSheet(f"""
            background-color: {bg};
            color: {fg};
            border: 2px solid #333;
            font-weight: bold;
            border-radius: 2px;
        """)
