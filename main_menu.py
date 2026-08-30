import sys
import os
import math
import subprocess
import random
import json
from PyQt6.QtWidgets import (
    QApplication, QWidget, QFrame, QLabel, QPushButton, 
    QVBoxLayout, QHBoxLayout, QGridLayout, QGraphicsDropShadowEffect,
    QProgressBar, QDialog, QInputDialog, QListWidget, QScrollArea,
    QMessageBox
)
from PyQt6.QtCore import Qt, QTimer, QUrl
from PyQt6.QtGui import QPainter, QPixmap, QColor, QFont, QIcon, QPen, QRadialGradient
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

from cloud_save import CloudSaveWindow
import demand_generator

class CRTOverlay(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 1. Subtle green-phosphor glow overlay over the screen widgets
        painter.fillRect(self.rect(), QColor(51, 255, 51, 25))
        
        # 2. Vignette to simulate CRT screen corner dimming over the widgets
        vignette = QRadialGradient(self.width() / 2, self.height() / 2, max(self.width(), self.height()) / 1.3)
        vignette.setColorAt(0.0, QColor(0, 0, 0, 0))
        vignette.setColorAt(0.7, QColor(0, 0, 0, 40))
        vignette.setColorAt(1.0, QColor(0, 0, 0, 160))
        painter.fillRect(self.rect(), vignette)

class MainMenuWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Stay Civilised - Main Menu")
        self.resize(1000, 650)
        self.setMinimumSize(900, 550)
        
        # 1. Load Assets
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.work_dir = os.getcwd()
        
        dam_path = os.path.join(self.base_dir, "dam.png")
        if os.path.exists(dam_path):
            self.dam_pixmap = QPixmap(dam_path)
        else:
            self.dam_pixmap = QPixmap()
            print(f"Warning: dam.png not found at {dam_path}")
            
        logo_path = os.path.join(self.base_dir, "logo.png")
        if os.path.exists(logo_path):
            self.logo_pixmap = QPixmap(logo_path)
        else:
            self.logo_pixmap = QPixmap()
            print(f"Warning: logo.png not found at {logo_path}")
            
        music_path = os.path.join(self.base_dir, "music.mp3")
        self.music_exists = os.path.exists(music_path)
        
        # 2. Setup Background Animation & Cursor Blink
        self.time_counter = 0.0
        self.blink_counter = 0
        self.blink_state = True
        self.is_loading = False
        
        self.bg_timer = QTimer(self)
        self.bg_timer.timeout.connect(self.update_background)
        self.bg_timer.start(16)  # ~60 FPS
        
        # 3. Setup Audio Loop
        if self.music_exists:
            self.player = QMediaPlayer()
            self.audio_output = QAudioOutput()
            self.player.setAudioOutput(self.audio_output)
            self.player.setSource(QUrl.fromLocalFile(music_path))
            self.audio_output.setVolume(0.6)  # Set moderate volume
            self.player.setLoops(QMediaPlayer.Loops.Infinite)
            self.player.play()
        else:
            print(f"Warning: music.mp3 not found at {music_path}")
            
        # 4. Process tracking
        self.sim_process = None
        self.poll_timer = None
        self.launch_args = []

        # Save path (relative to project root)
        if os.name == "nt":
            self.save_path = "Hydro 1\\saves\\"
        else:
            self.save_path = "Hydro 1/saves/"
        
        # 5. Build UI Layout
        self.init_ui()
        
        # 6. Create overlay for the terminal screen to cover widgets
        self.screen_overlay = CRTOverlay(self.terminal_screen)
        self.screen_overlay.setGeometry(self.terminal_screen.rect())
        self.screen_overlay.show()
        
    def init_ui(self):
        # Create main grid layout to center the card panel
        main_layout = QGridLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 1. Central card styled as 80s beige plastic console casing
        self.card = QFrame()
        self.card.setObjectName("MainCard")
        self.card.setStyleSheet("""
            QFrame#MainCard {
                background-color: #dcdcc6;
                border: 6px solid;
                border-top-color: #f7f7eb;
                border-left-color: #f7f7eb;
                border-right-color: #9d9d88;
                border-bottom-color: #9d9d88;
                border-radius: 8px;
            }
        """)
        
        # Retro drop shadow for physical casing
        shadow = QGraphicsDropShadowEffect(self.card)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setOffset(8, 8)
        self.card.setGraphicsEffect(shadow)
        
        # Outer bezel spacing layout
        card_outer_layout = QVBoxLayout(self.card)
        card_outer_layout.setContentsMargins(20, 20, 20, 20)
        
        # 2. Inner terminal screen (the CRT display face)
        self.terminal_screen = QFrame()
        self.terminal_screen.setObjectName("TerminalScreen")
        self.terminal_screen.setStyleSheet("""
            QFrame#TerminalScreen {
                background-color: #031405;
                border: 4px solid;
                border-top-color: #535348;
                border-left-color: #535348;
                border-right-color: #ffffff;
                border-bottom-color: #ffffff;
                border-radius: 4px;
            }
        """)
        card_outer_layout.addWidget(self.terminal_screen)
        
        # Inner screen layout for text and controls
        card_layout = QVBoxLayout(self.terminal_screen)
        card_layout.setContentsMargins(35, 35, 35, 35)
        card_layout.setSpacing(25)
        
        # Header - Game Title & Subtitle in Green Phosphor Glow
        header_layout = QVBoxLayout()
        header_layout.setSpacing(8)
        
        self.title_label = QLabel("> STAY CIVILISED █")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("""
            font-family: 'Courier New', 'Consolas', 'Terminal', monospace;
            font-size: 38px;
            font-weight: bold;
            color: #33ff33;
            letter-spacing: 2px;
        """)
        
        # Apply glowing phosphor effect
        title_glow = QGraphicsDropShadowEffect(self.title_label)
        title_glow.setBlurRadius(15)
        title_glow.setColor(QColor(51, 255, 51, 220))
        title_glow.setOffset(0, 0)
        self.title_label.setGraphicsEffect(title_glow)
        
        self.subtitle_label = QLabel("[ SYS STATUS: ONLINE | COUPLING: STANDBY ]")
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle_label.setStyleSheet("""
            font-family: 'Courier New', 'Consolas', 'Terminal', monospace;
            font-size: 11px;
            font-weight: bold;
            color: #22aa22;
            letter-spacing: 1px;
        """)
        
        header_layout.addWidget(self.title_label)
        header_layout.addWidget(self.subtitle_label)
        card_layout.addLayout(header_layout)
        
        # Decorative Separator Line (Phosphor grid style)
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background-color: rgba(51, 255, 51, 0.3); max-height: 2px; border: none;")
        card_layout.addWidget(sep)
        
        # Action Row (Logo, Telemetry, Launch Button)
        action_layout = QHBoxLayout()
        action_layout.setSpacing(30)
        
        # Left: logo.png in an oscilloscope frame
        logo_frame = QFrame()
        logo_frame.setObjectName("LogoFrame")
        logo_frame.setStyleSheet("""
            QFrame#LogoFrame {
                border: 2px solid #22aa22;
                background-color: #020c03;
                border-radius: 4px;
                padding: 4px;
            }
        """)
        logo_frame_layout = QVBoxLayout(logo_frame)
        logo_frame_layout.setContentsMargins(5, 5, 5, 5)
        
        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if not self.logo_pixmap.isNull():
            scaled_logo = self.logo_pixmap.scaled(110, 110, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.logo_label.setPixmap(scaled_logo)
        else:
            self.logo_label.setText("[ LOGO ]")
            self.logo_label.setStyleSheet("color: #33ff33; font-family: 'Courier New', monospace; font-weight: bold; font-size: 16px;")
            
        logo_frame_layout.addWidget(self.logo_label)
        action_layout.addWidget(logo_frame)
        
        # Middle: Diagnostics Telemetry Block
        self.telemetry_label = QLabel()
        self.telemetry_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.telemetry_label.setStyleSheet("""
            font-family: 'Courier New', 'Consolas', 'Terminal', monospace;
            font-size: 11px;
            color: #33ff33;
        """)
        self.telemetry_label.setText(
            "=== SYSTEM TELEMETRY ===\n"
            "CORE STATUS : STANDBY\n"
            "COOLANT TEMP: 38.6 °C\n"
            "PRESSURE    : 101.3 kPa\n"
            "GRID FLUX   : 0.00 kW\n"
            "ENCRYPTION  : SECURE"
        )
        action_layout.addWidget(self.telemetry_label)
        
        # Divider Line
        v_sep = QFrame()
        v_sep.setFrameShape(QFrame.Shape.VLine)
        v_sep.setStyleSheet("background-color: rgba(51, 255, 51, 0.2); max-width: 1px; border: none;")
        action_layout.addWidget(v_sep)
        
        # Right: Chunky Physical Pushbutton
        self.launch_btn = QPushButton("CONNECT")
        self.launch_btn.setStyleSheet("""
            QPushButton {
                background-color: #a31d1d;
                color: #ffffff;
                border: 4px solid;
                border-top-color: #ff5555;
                border-left-color: #ff5555;
                border-right-color: #550000;
                border-bottom-color: #550000;
                border-radius: 4px;
                font-family: 'Courier New', 'Consolas', 'Terminal', monospace;
                font-size: 18px;
                font-weight: bold;
                padding: 15px 30px;
                min-width: 160px;
                min-height: 80px;
            }
            QPushButton:hover {
                background-color: #cc2424;
                border-top-color: #ff7777;
                border-left-color: #ff7777;
                border-right-color: #660000;
                border-bottom-color: #660000;
            }
            QPushButton:pressed {
                background-color: #550000;
                border: 4px solid;
                border-top-color: #220000;
                border-left-color: #220000;
                border-right-color: #ff5555;
                border-bottom-color: #ff5555;
                padding: 17px 28px 13px 32px;
            }
        """)
        self.launch_btn.clicked.connect(self.launch_simulator)
        
        right_col = QVBoxLayout()
        right_col.setSpacing(10)
        right_col.addWidget(self.launch_btn)
        
        self.cloud_btn = QPushButton("CLOUD SAVE")
        self.cloud_btn.setStyleSheet("""
            QPushButton {
                background-color: #1a4a1a;
                color: #33ff33;
                border: 4px solid;
                border-top-color: #55aa55;
                border-left-color: #55aa55;
                border-right-color: #0a2a0a;
                border-bottom-color: #0a2a0a;
                border-radius: 4px;
                font-family: 'Courier New', 'Consolas', 'Terminal', monospace;
                font-size: 14px;
                font-weight: bold;
                padding: 8px 30px;
                min-width: 160px;
                max-height: 45px;
            }
            QPushButton:hover {
                background-color: #226622;
                border-top-color: #77cc77;
                border-left-color: #77cc77;
                border-right-color: #0c3a0c;
                border-bottom-color: #0c3a0c;
            }
            QPushButton:pressed {
                background-color: #0a2a0a;
                border: 4px solid;
                border-top-color: #051505;
                border-left-color: #051505;
                border-right-color: #55aa55;
                border-bottom-color: #55aa55;
                padding: 10px 28px 6px 32px;
            }
        """)
        self.cloud_btn.clicked.connect(self.open_cloud_save)
        right_col.addWidget(self.cloud_btn)
        
        action_layout.addLayout(right_col)
        
        card_layout.addLayout(action_layout)
        
        # Progress Bar (initially hidden)
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("LaunchProgressBar")
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("BOOT SEQUENCE: %p%")
        self.progress_bar.setStyleSheet("""
            QProgressBar#LaunchProgressBar {
                border: 2px solid #22aa22;
                border-radius: 4px;
                background-color: #020c03;
                text-align: center;
                color: #bd1300;
                font-family: 'Courier New', 'Consolas', 'Terminal', monospace;
                font-weight: bold;
                font-size: 12px;
                height: 25px;
            }
            QProgressBar#LaunchProgressBar::chunk {
                background-color: #33ff33;
                width: 12px;
                margin: 1px;
            }
        """)
        self.progress_bar.hide()
        card_layout.addWidget(self.progress_bar)

        # Footer - Small Status Text
        footer_label = QLabel("VERSION v0.4.0 - STAY CIVILISED PROJECT")
        footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer_label.setStyleSheet("""
            font-family: 'Courier New', 'Consolas', 'Terminal', monospace;
            font-size: 10px;
            color: #22aa22;
            font-weight: bold;
            margin-top: 10px;
        """)
        card_layout.addWidget(footer_label)
        
        # Add card to the main layout and center it
        main_layout.addWidget(self.card, 0, 0, Qt.AlignmentFlag.AlignCenter)
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'screen_overlay') and hasattr(self, 'terminal_screen'):
            self.screen_overlay.setGeometry(self.terminal_screen.rect())
            
    def update_background(self):
        # Update time counter for the scrolling animation
        self.time_counter += 0.003
        
        # Handle blinking block cursor
        self.blink_counter += 1
        if self.blink_counter >= 30:  # ~500ms
            self.blink_counter = 0
            self.blink_state = not self.blink_state
            cursor = "█" if self.blink_state else " "
            self.title_label.setText(f"> STAY CIVILISED {cursor}")
            
            # Slightly vary telemetry numbers
            if not self.is_loading:
                temp = 38.0 + random.uniform(0.5, 1.2)
                pressure = 101.2 + random.uniform(-0.3, 0.4)
                flux = random.choice([0.00, 0.00, 0.01, 0.00])
                self.telemetry_label.setText(
                    "=== SYSTEM TELEMETRY ===\n"
                    "CORE STATUS : STANDBY\n"
                    f"COOLANT TEMP: {temp:.1f} °C\n"
                    f"PRESSURE    : {pressure:.1f} kPa\n"
                    f"GRID FLUX   : {flux:.2f} kW\n"
                    "DIAGNOSTIC  : SECURE"
                )
            
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        
        # 1. Background image with monochrome green-phosphor display tint
        if not self.dam_pixmap.isNull():
            img_aspect = self.dam_pixmap.width() / self.dam_pixmap.height()
            scaled_h = self.height()
            scaled_w = int(scaled_h * img_aspect)
            
            min_width = int(self.width() * 1.25)
            if scaled_w < min_width:
                scaled_w = min_width
                scaled_h = int(scaled_w / img_aspect)
                
            max_scroll = scaled_w - self.width()
            t = (math.sin(self.time_counter) + 1.0) / 2.0
            offset_x = int(t * max_scroll)
            offset_y = (self.height() - scaled_h) // 2
            
            painter.drawPixmap(-offset_x, offset_y, scaled_w, scaled_h, self.dam_pixmap)
            
            # Heavy green-phosphor CRT tint mask overlay
            painter.fillRect(self.rect(), QColor(1, 22, 2, 195))
        else:
            # Fallback green terminal background
            painter.fillRect(self.rect(), QColor(2, 20, 3))
            
        # 2. Vignette / CRT curvature overlay
        vignette = QRadialGradient(self.width() / 2, self.height() / 2, max(self.width(), self.height()) / 1.5)
        vignette.setColorAt(0.0, QColor(0, 0, 0, 0))
        vignette.setColorAt(0.7, QColor(0, 0, 0, 70))
        vignette.setColorAt(1.0, QColor(0, 0, 0, 230))
        painter.fillRect(self.rect(), vignette)
            
    def open_cloud_save(self):
        if not hasattr(self, 'cloud_win'):
            self.cloud_win = CloudSaveWindow()
        self.cloud_win.show()
        self.cloud_win.raise_()
        self.cloud_win.activateWindow()

    def launch_simulator(self):
        # Prompt the user to either load a save or start a new game
        self.choose_session()

    def choose_session(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("START SESSION")
        dlg.setModal(True)
        dlg.setStyleSheet("""
            QDialog {
                background-color: #0a0f0a;
                color: #33ff33;
            }
            QLabel {
                color: #33ff33;
                font-family: 'Courier New', 'Consolas', 'Terminal', monospace;
                font-weight: bold;
            }
            QPushButton {
                background-color: #0d3b0d;
                color: #33ff33;
                border: 2px solid #33ff33;
                border-radius: 4px;
                padding: 14px 20px;
                font-family: 'Courier New', 'Consolas', 'Terminal', monospace;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #146314; }
            QPushButton:pressed { background-color: #082208; }
        """)
        layout = QVBoxLayout(dlg)
        layout.setSpacing(18)
        layout.addWidget(QLabel("> SELECT OPERATING MODE", alignment=Qt.AlignmentFlag.AlignCenter))

        new_btn = QPushButton("NEW GAME")
        load_btn = QPushButton("LOAD SAVE")
        layout.addWidget(new_btn)
        layout.addWidget(load_btn)

        def on_new():
            dlg.accept()
            self.start_new_game()

        def on_load():
            dlg.accept()
            self.load_save_game()

        new_btn.clicked.connect(on_new)
        load_btn.clicked.connect(on_load)
        dlg.exec()

    def start_new_game(self):
        # Prompt for a seed (default: random integer)
        default_seed = random.randint(10000, 99999)
        text, ok = QInputDialog.getText(
            self, "NEW GAME - SEED",
            "ENTER SIMULATION SEED\n(default is random):",
            text=str(default_seed)
        )
        if not ok:
            self.reset_menu_state()
            return
        try:
            seed = int(text.strip())
        except ValueError:
            QMessageBox.warning(self, "INVALID SEED", "Seed must be an integer.")
            self.reset_menu_state()
            return

        # (Re)generate the demand profile for this seed
        try:
            demand_generator.generate_demand(seed)
        except Exception as e:
            QMessageBox.critical(self, "DEMAND GENERATION FAILED", str(e))
            self.reset_menu_state()
            return

        self.launch_args = ["--new", "--seed", str(seed)]
        self.start_boot_sequence()

    def load_save_game(self):
        # List available saves and let the user pick one
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)
        files = sorted([f for f in os.listdir(self.save_path) if f.endswith('.json')])
        if not files:
            QMessageBox.information(self, "NO SAVES", "No save files found.\nStart a new game instead.")
            self.reset_menu_state()
            return

        dlg = QDialog(self)
        dlg.setWindowTitle("LOAD SAVE")
        dlg.setModal(True)
        dlg.resize(420, 360)
        dlg.setStyleSheet("""
            QDialog { background-color: #0a0f0a; color: #33ff33; }
            QLabel { color: #33ff33; font-family: 'Courier New', monospace; font-weight: bold; }
            QListWidget {
                background-color: #061006; color: #33ff33; border: 2px solid #33ff33;
                border-radius: 4px; font-family: 'Courier New', monospace; padding: 4px;
            }
            QListWidget::item { padding: 8px; }
            QListWidget::item:selected { background-color: #146314; }
            QPushButton {
                background-color: #0d3b0d; color: #33ff33; border: 2px solid #33ff33;
                border-radius: 4px; padding: 10px; font-family: 'Courier New', monospace; font-weight: bold;
            }
            QPushButton:hover { background-color: #146314; }
        """)
        layout = QVBoxLayout(dlg)
        layout.addWidget(QLabel("> SELECT SAVE FILE", alignment=Qt.AlignmentFlag.AlignCenter))
        save_list = QListWidget()
        save_list.addItems(files)
        layout.addWidget(save_list)
        btn_layout = QHBoxLayout()
        cancel_btn = QPushButton("CANCEL")
        load_btn = QPushButton("LOAD")
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(load_btn)
        layout.addLayout(btn_layout)

        def do_load():
            item = save_list.currentItem()
            if not item:
                return
            dlg.accept()
            self.finish_load_save(item.text())

        cancel_btn.clicked.connect(dlg.reject)
        load_btn.clicked.connect(do_load)

        def on_double_click(item):
            self.finish_load_save(item.text())
            dlg.accept()

        save_list.itemDoubleClicked.connect(on_double_click)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            dlg.deleteLater()

    def finish_load_save(self, filename):
        save_file = os.path.join(self.save_path, filename)
        try:
            with open(save_file, 'r') as f:
                data = json.load(f)
            seed = int(data.get('seed', 86557))
        except Exception as e:
            QMessageBox.critical(self, "LOAD FAILED", f"Could not read save file:\n{e}")
            self.reset_menu_state()
            return

        # Regenerate the demand profile from the save's seed
        try:
            demand_generator.generate_demand(seed)
        except Exception as e:
            QMessageBox.critical(self, "DEMAND GENERATION FAILED", str(e))
            self.reset_menu_state()
            return

        self.launch_args = ["--load", save_file.replace("\\", "/")]
        self.start_boot_sequence()

    def start_boot_sequence(self):
        # Start mock boot loading sequence
        self.is_loading = True
        self.launch_btn.setEnabled(False)
        self.launch_btn.setText("LOADING...")
        self.progress_bar.setValue(0)
        self.progress_bar.show()

        self.loading_progress = 0
        self.loading_timer = QTimer(self)
        self.loading_timer.timeout.connect(self.advance_loading)
        self.loading_timer.start(100)

    def advance_loading(self):
        # Increment progress dynamically
        self.loading_progress += random.randint(2, 5)
        if self.loading_progress >= 100:
            self.loading_progress = 100
            self.progress_bar.setValue(100)
            self.loading_timer.stop()
            self.finalize_launch()
            return
            
        self.progress_bar.setValue(self.loading_progress)
        
        # Update subtitle text
        if self.loading_progress < 25:
            self.subtitle_label.setText("[ SYS STATUS: INITIALISING SECURE CONNECTION... ]")
        elif self.loading_progress < 50:
            self.subtitle_label.setText("[ SYS STATUS: INITIALIZING SIMULATION... ]")
        elif self.loading_progress < 75:
            self.subtitle_label.setText("[ SYS STATUS: SYNCHRONIZING GRID DATA... ]")
        else:
            self.subtitle_label.setText("[ SYS STATUS: MEETING THE DEMAND... ]")
            
        # Update telemetry log with boot steps
        log_lines = []
        if self.loading_progress >= 15:
            log_lines.append("CORE BOOT      : OK")
        else:
            log_lines.append("CORE BOOT      : STARTING")
            
        if self.loading_progress >= 40:
            log_lines.append("PRESSURE VALVE : OPEN")
        elif self.loading_progress >= 15:
            log_lines.append("PRESSURE VALVE : CONNECTING")
            
        if self.loading_progress >= 65:
            log_lines.append("GRID FLUX CAP  : CHARGED")
        elif self.loading_progress >= 40:
            log_lines.append("GRID FLUX CAP  : SYNCING")
            
        if self.loading_progress >= 88:
            log_lines.append("SIM COUPLING   : ENGAGED")
        elif self.loading_progress >= 65:
            log_lines.append("SIM COUPLING   : NEGOTIATING")
            
        while len(log_lines) < 4:
            log_lines.append("")
            
        flux_val = (self.loading_progress / 100.0) * 1250.0 + random.uniform(-10.0, 10.0)
        if flux_val < 0.0:
            flux_val = 0.0
        self.telemetry_label.setText(
            "=== BOOT TELEMETRY ===\n"
            f"{log_lines[0]}\n"
            f"{log_lines[1]}\n"
            f"{log_lines[2]}\n"
            f"{log_lines[3]}\n"
            f"GRID FLUX   : {flux_val:.2f} kW"
        )

    def finalize_launch(self):
        # Pause background music
        if self.music_exists and hasattr(self, 'player'):
            self.player.pause()
            
        # Hide the main menu
        self.hide()
        
        # Launch simulator.py with working directory remaining at project root
        try:
            launch_cmd = [sys.executable, "Hydro 1/simulator.py"] + self.launch_args
            self.sim_process = subprocess.Popen(launch_cmd)
            
            # Start QTimer to poll for completion
            self.poll_timer = QTimer(self)
            self.poll_timer.timeout.connect(self.check_simulator_status)
            self.poll_timer.start(500)
        except Exception as e:
            print("Error launching simulator:", e)
            self.reset_menu_state()

    def reset_menu_state(self):
        self.is_loading = False
        self.launch_args = []
        self.progress_bar.hide()
        self.progress_bar.setValue(0)
        self.launch_btn.setEnabled(True)
        self.launch_btn.setText("LAUNCH")
        self.subtitle_label.setText("[ SYS STATUS: ONLINE | CONNECTION: STANDBY ]")
        
        # Reset telemetry text to standby
        self.telemetry_label.setText(
            "=== SYSTEM TELEMETRY ===\n"
            "CORE STATUS : STANDBY\n"
            "COOLANT TEMP: 38.6 °C\n"
            "PRESSURE    : 101.3 kPa\n"
            "GRID FLUX   : 0.00 kW\n"
            "DIAGNOSTIC  : SECURE"
        )
        
        self.showMaximized()
        if self.music_exists and hasattr(self, 'player'):
            self.player.play()
            
    def check_simulator_status(self):
        if self.sim_process and self.sim_process.poll() is not None:
            # Process has finished
            self.poll_timer.stop()
            self.poll_timer = None
            self.sim_process = None
            
            # Restore main menu and UI states
            self.reset_menu_state()
                
    def closeEvent(self, event):
        # Stop background music loop
        if self.music_exists and hasattr(self, 'player'):
            self.player.stop()
            
        # Terminate simulator if still running
        if self.sim_process and self.sim_process.poll() is None:
            self.sim_process.terminate()
            
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainMenuWindow()
    window.showMaximized()
    sys.exit(app.exec())
