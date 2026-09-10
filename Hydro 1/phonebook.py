import json
import os
import sys

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QTextBrowser
from PyQt6.QtCore import Qt
from buttons import CustomButton


def _resource_path(name):
    """Resolves a bundled data file when frozen with PyInstaller."""
    if getattr(sys, "frozen", False):
        base = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
        return os.path.join(base, name)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), name)

class PhoneWindow(QWidget):
    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        self.setWindowTitle("Phone")
        self.setStyleSheet("background-color: #1a1a1a; color: white;")
        self.setMinimumSize(760, 520)

        phonebook_path = _resource_path("phonebook.json")
        with open(phonebook_path, "r") as f:
            self.phonebook = json.load(f)

        self.dialed = ""
        self.contact = None
        self.node_key = ""

        # Numeric input mode (used to type a value, e.g. coal plant MW)
        self.input_mode = False
        self.input_func = ""
        self.input_value = ""

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        main_layout.addWidget(QLabel("<h2>Phone</h2>", alignment=Qt.AlignmentFlag.AlignCenter))
        main_layout.addWidget(self.create_separator())

        content_layout = QHBoxLayout()
        main_layout.addLayout(content_layout)

        # PHONEBOOK LAYOUT
        phonebook_layout = QVBoxLayout()
        content_layout.addLayout(phonebook_layout, 1)

        phonebook_layout.addWidget(QLabel("<h4>Phonebook</h4>", alignment=Qt.AlignmentFlag.AlignCenter))
        for entry in self.phonebook:
            label = QLabel(f"<a style='color:#003366; text-decoration:none' href='{entry['number']}'>{entry['name']} - {entry['number']}</a>")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.linkActivated.connect(self.set_dial)
            phonebook_layout.addWidget(label)

        phonebook_layout.addSpacing(15)
        phonebook_layout.addWidget(self.create_separator())

        # DIAL LAYOUT
        self.display = QLabel("_")
        self.display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.display.setStyleSheet("background-color: #6a6a6a; border: 2px solid #444; border-radius: 2px; padding: 8px; font-family: Consolas, monospace; font-size: 18px; color: #222222;")
        phonebook_layout.addWidget(self.display)

        dial_layout = QVBoxLayout()
        numpad_row_1 = QHBoxLayout()
        self.numpad_7 = CustomButton("7")
        self.numpad_8 = CustomButton("8")
        self.numpad_9 = CustomButton("9")
        numpad_row_1.addWidget(self.numpad_7)
        numpad_row_1.addWidget(self.numpad_8)
        numpad_row_1.addWidget(self.numpad_9)
        dial_layout.addLayout(numpad_row_1)

        numpad_row_2 = QHBoxLayout()
        self.numpad_4 = CustomButton("4")
        self.numpad_5 = CustomButton("5")
        self.numpad_6 = CustomButton("6")
        numpad_row_2.addWidget(self.numpad_4)
        numpad_row_2.addWidget(self.numpad_5)
        numpad_row_2.addWidget(self.numpad_6)
        dial_layout.addLayout(numpad_row_2)

        numpad_row_3 = QHBoxLayout()
        self.numpad_1 = CustomButton("1")
        self.numpad_2 = CustomButton("2")
        self.numpad_3 = CustomButton("3")
        numpad_row_3.addWidget(self.numpad_1)
        numpad_row_3.addWidget(self.numpad_2)
        numpad_row_3.addWidget(self.numpad_3)
        dial_layout.addLayout(numpad_row_3)

        numpad_row_4 = QHBoxLayout()
        self.numpad_call = CustomButton("☏", "#080")
        self.numpad_0 = CustomButton("0")
        self.numpad_end = CustomButton("⌫", "#800")
        numpad_row_4.addWidget(self.numpad_end)
        numpad_row_4.addWidget(self.numpad_0)
        numpad_row_4.addWidget(self.numpad_call)
        dial_layout.addLayout(numpad_row_4)

        phonebook_layout.addLayout(dial_layout)
        phonebook_layout.addStretch()

        for btn in [self.numpad_0, self.numpad_1, self.numpad_2, self.numpad_3,
                    self.numpad_4, self.numpad_5, self.numpad_6,
                    self.numpad_7, self.numpad_8, self.numpad_9]:
            btn.clicked.connect(lambda _, b=btn.text(): self.press_digit(b))

        self.numpad_call.clicked.connect(self.start_call)
        self.numpad_end.clicked.connect(self.end_call)

        # CHAT BOX
        chat_layout = QVBoxLayout()
        content_layout.addLayout(chat_layout, 2)

        self.chat_header = QLabel("<h4>Messaging</h4>", alignment=Qt.AlignmentFlag.AlignCenter)
        chat_layout.addWidget(self.chat_header)

        self.chat_box = QTextBrowser()
        self.chat_box.setOpenExternalLinks(False)
        self.chat_box.setStyleSheet("""
            QTextBrowser {
                background-color: #6a6a6a;
                border: 2px solid #444;
                border-radius: 2px;
                color: #222222;
                padding: 6px;
            }
        """)
        chat_layout.addWidget(self.chat_box, 1)

        # OPTIONS BELOW THE CHAT BOX
        options_layout = QHBoxLayout()
        self.option_1 = CustomButton("1")
        self.option_2 = CustomButton("2")
        self.option_3 = CustomButton("3")
        options_layout.addWidget(self.option_1)
        options_layout.addWidget(self.option_2)
        options_layout.addWidget(self.option_3)
        chat_layout.addLayout(options_layout)

        self.option_1.clicked.connect(lambda: self.press_option(1))
        self.option_2.clicked.connect(lambda: self.press_option(2))
        self.option_3.clicked.connect(lambda: self.press_option(3))

        self.reset_chat()
        self.update_options()

    # --- Functions ---
    def set_dial(self, number=None):
        if not self.contact and number is not None:
            self.dialed = str(number)
            self.display.setText(self.dialed or "_")

    def press_digit(self, digit):
        if self.input_mode:
            if len(self.input_value) < 3:
                trial = self.input_value + digit
                if int(trial) <= 100:
                    self.input_value = trial
                    self.display.setText(self.input_value)
            self.update_options()
            return
        if not self.contact and len(self.dialed) < 12:
            self.dialed += digit
            self.display.setText(self.dialed)

    def start_call(self):
        if self.input_mode:
            self.confirm_input()
            return
        if self.contact:
            return
        for entry in self.phonebook:
            if entry["number"] == self.dialed:
                self.contact = entry
                self.node_key = "1"
                self.chat_header.setText(f"<h4>{entry['name']}</h4>")
                self.display.setText(entry["number"])
                self.engine.log(f"Called {entry['name']} ({entry['number']})")
                self.show_node("1")
                return
        self.system_note(f"Number {self.dialed} not recognised.")
        self.engine.log(f"Call failed - unknown number {self.dialed}")

    def end_call(self):
        if self.input_mode:
            self.exit_input()
        if self.contact:
            self.system_note(f"Call ended.")
            self.engine.log(f"Hung up on {self.contact['name']}")
        self.contact = None
        self.node_key = ""
        self.chat_header.setText("<h4>Messaging</h4>")
        self.dialed = ""
        self.display.setText(self.dialed)
        self.update_options()

    def reset_chat(self):
        self.chat_box.clear()
        self.system_note("Dial a number to start a conversation.")

    def press_option(self, index):
        if self.input_mode:
            if index == 1:
                self.confirm_input()
            elif index == 2:
                self.input_value = self.input_value[:-1]
                self.display.setText(self.input_value or "_")
                self.update_options()
            elif index == 3:
                self.system_note("Input cancelled.")
                self.exit_input()
                self.end_call()
            return
        node = self.get_node(self.node_key)
        option_text = node.get(f"option{index}") if node else None
        if not option_text or not self.contact:
            return
        self.outgoing_note(str(index))
        self.node_key += str(index)
        self.show_node(self.node_key)

    def get_node(self, key):
        chat = self.contact["chat"] if self.contact else {}
        return chat.get(key, {})

    def show_node(self, key):
        node = self.get_node(key)
        if not node:
            self.end_call()
            return

        if node.get("input"):
            self.start_input(node)
            return

        if node.get("function"):
            self.run_function(node)
            self.end_call()
            return

        text = node.get("text", "")
        if text:
            self.incoming_note(text)

        has_options = any(node.get(f"option{i}") for i in range(1, 4))
        if not has_options:
            self.end_call()
            return
        self.update_options()

    def run_function(self, node):
        func_name = node.get("name", "")
        arg = node.get("arg")
        func = getattr(self.engine, func_name, None)
        if not callable(func):
            self.system_note(f"'{func_name}' is not available yet.")
            self.engine.log(f"Phone function missing: {func_name}")
            return
        try:
            try:
                value = float(arg)
            except (TypeError, ValueError):
                value = arg
            if arg is None:
                func()
            else:
                func(value)
            self.engine.log(f"{func_name}({value}) via phone")
        except Exception as e:
            self.system_note(f"Error calling '{func_name}': {e}")
            self.engine.log(f"Phone function error: {func_name}: {e}")

    def update_options(self):
        if self.input_mode:
            self.set_input_options()
            return
        node = self.get_node(self.node_key)
        for i, button in enumerate([self.option_1, self.option_2, self.option_3], start=1):
            option_text = node.get(f"option{i}", "") if node else ""
            button.setText(option_text or f"{i}")
            button.setEnabled(bool(option_text) and bool(self.contact))

    # --- Numeric input mode ---
    def start_input(self, node):
        self.input_mode = True
        self.input_func = node.get("name", "")
        self.input_value = ""
        self.display.setText("_")
        text = node.get("text", "")
        if text:
            self.incoming_note(text)
        self.prompt_note("Use the keypad to enter a value (0-100), then confirm.")
        self.set_input_options()

    def set_input_options(self):
        self.option_1.setText("✓ CONFIRM")
        self.option_2.setText("⌫")
        self.option_3.setText("CANCEL")
        for btn in (self.option_1, self.option_2, self.option_3):
            btn.setEnabled(True)
        if not self.input_value:
            self.option_1.setEnabled(False)

    def exit_input(self):
        self.input_mode = False
        self.input_func = ""
        self.input_value = ""
        self.display.setText(self.dialed or "_")

    def confirm_input(self):
        if not self.input_value:
            self.system_note("Enter a value first.")
            return
        value = float(self.input_value)
        func = getattr(self.engine, self.input_func, None)
        if callable(func):
            try:
                func(value)
                self.engine.log(f"{self.input_func}({value}) via phone")
                self.outgoing_note(f"{self.input_value} MW")
                self.system_note("Done.")
            except Exception as e:
                self.system_note(f"Error calling '{self.input_func}': {e}")
                self.engine.log(f"Phone function error: {self.input_func}: {e}")
        else:
            self.system_note(f"'{self.input_func}' is not available yet.")
        self.exit_input()
        self.end_call()

    def prompt_note(self, text):
        html = text.replace("\n", "<br>")
        self.append_bubble(html, align="center", bg="#555555")


    def incoming_note(self, text):
        html = text.replace("\n", "<br>")
        self.append_bubble(html, align="left", bg="#4a5a6a")

    def outgoing_note(self, text):
        html = text.replace("\n", "<br>")
        self.append_bubble(html, align="right", bg="#3a6a5a")

    def system_note(self, text):
        html = text.replace("\n", "<br>")
        self.append_bubble(html, align="center", bg="#555555")

    def append_bubble(self, html, align="left", bg="#26323f"):
        bubble = f'<table width="100%" cellspacing="0" cellpadding="4"><tr><td align="{align}"><span style="background-color:{bg}; color:#ffffff;">{html}</span></td></tr></table>'
        self.chat_box.append(bubble)
        self.chat_box.verticalScrollBar().setValue(self.chat_box.verticalScrollBar().maximum())
        self.update_options()

    def create_separator(self):
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("background-color: #555;")
        return line

    def closeEvent(self, event):
        self.hide()
        event.ignore()
