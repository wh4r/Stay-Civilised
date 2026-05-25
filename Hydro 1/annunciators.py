from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt, QTimer
import numpy as np
import sounddevice as sd
import threading

class Annunciator(QLabel):
    def __init__(self, text, alert_color="red", persistent=True, sound_freq=None):
        super().__init__(text)
        self.alert_color = alert_color
        self.active = False
        self.needs_ack = False
        self.blink = False
        self.persistent = persistent
        self.sound_freq = sound_freq
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFixedSize(120, 40)
        self.update_style()
        
        # sound loop
        self.sound_timer = QTimer()
        self.sound_timer.timeout.connect(self._sound_if_active)
        self.sound_timer.start(500)  # beep every 500 ms

    # Plays sound
    def _sound_if_active(self):
        if self.active and self.sound_freq:
            self.play_sound(self.sound_freq)

    # Run to turn on/off the annunciator
    def set_state(self, active):
        """Set alarm state."""
        if self.persistent:
            if active and not self.active:
                self.needs_ack = True
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

    # Plays the sound at the given frequency
    def play_sound(self, freq, duration=0.2, volume=0.2):
        def _beep():
            fs = 44100
            t = np.linspace(0, duration, int(fs*duration), endpoint=False)
            wave = volume * np.sin(2 * np.pi * freq * t).astype(np.float32)
            sd.play(wave, fs)
            sd.wait()
        threading.Thread(target=_beep, daemon=True).start()

    # Updates the style of the annunciator
    def update_style(self):
        if self.active:
            bg = self.alert_color if self.blink else "#333333"
            fg = "white"
        elif self.persistent and self.needs_ack:
            bg = self.alert_color
            fg = "white"
        else:
            bg = "#333333"
            fg = "#666666"

        self.setStyleSheet(f"""
            background-color: {bg};
            color: {fg};
            border: 2px solid #555;
            font-weight: bold;
            border-radius: 4px;
        """)
