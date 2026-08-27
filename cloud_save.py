import os
import json
import threading
import urllib.parse
import urllib.request
import urllib.error

from PyQt6.QtWidgets import (
    QApplication, QWidget, QFrame, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QGridLayout, QListWidget,
    QLineEdit, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPixmap, QRadialGradient

BASE_URL = "https://positron.my.id"
TOKEN_FILE = "cloud_token.txt"
FONT_FAMILY = "'Courier New', 'Consolas', 'Terminal', monospace"


class CloudSaveWindow(QWidget):
    api_done = pyqtSignal(object, str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Stay Civilised - Cloud Save")
        self.resize(900, 620)
        self.setMinimumSize(780, 540)

        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.saves_dir = os.path.join(self.base_dir, "Hydro 1", "saves")
        self.token_path = os.path.join(self.base_dir, TOKEN_FILE)

        dam_path = os.path.join(self.base_dir, "dam.png")
        if os.path.exists(dam_path):
            self.dam_pixmap = QPixmap(dam_path)
        else:
            self.dam_pixmap = QPixmap()

        self._pending_cb = None
        self._busy = False

        self.init_ui()
        self.api_done.connect(self.handle_api_result)
        self.load_saved_token()
        self.refresh_local_saves()

    def init_ui(self):
        main_layout = QGridLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

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

        shadow = QGraphicsDropShadowEffect(self.card)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setOffset(8, 8)
        self.card.setGraphicsEffect(shadow)

        card_outer_layout = QVBoxLayout(self.card)
        card_outer_layout.setContentsMargins(20, 20, 20, 20)

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

        screen_layout = QVBoxLayout(self.terminal_screen)
        screen_layout.setContentsMargins(30, 25, 30, 25)
        screen_layout.setSpacing(15)

        header_layout = QVBoxLayout()
        header_layout.setSpacing(4)

        title_label = QLabel("> CLOUD SAVE TERMINAL █")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(f"""
            font-family: {FONT_FAMILY};
            font-size: 26px;
            font-weight: bold;
            color: #33ff33;
            letter-spacing: 2px;
        """)
        header_layout.addWidget(title_label)

        subtitle_label = QLabel("[ REMOTE STORAGE LINK: positron.my.id ]")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet(f"""
            font-family: {FONT_FAMILY};
            font-size: 10px;
            font-weight: bold;
            color: #22aa22;
            letter-spacing: 1px;
        """)
        header_layout.addWidget(subtitle_label)

        screen_layout.addLayout(header_layout)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background-color: rgba(51, 255, 51, 0.3); max-height: 2px; border: none;")
        screen_layout.addWidget(sep)

        token_row = QHBoxLayout()
        token_row.setSpacing(10)

        token_label = QLabel("API TOKEN:")
        token_label.setStyleSheet(f"""
            font-family: {FONT_FAMILY};
            font-size: 12px;
            font-weight: bold;
            color: #33ff33;
        """)
        token_row.addWidget(token_label)

        self.token_input = QLineEdit()
        self.token_input.setPlaceholderText("Paste token from positron.my.id dashboard...")
        self.token_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.token_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: #020c03;
                border: 2px solid #22aa22;
                border-radius: 4px;
                color: #33ff33;
                font-family: {FONT_FAMILY};
                font-size: 12px;
                padding: 6px 10px;
            }}
        """)
        token_row.addWidget(self.token_input, 1)

        self.show_token_btn = QPushButton("SHOW")
        self.show_token_btn.setCheckable(True)
        self.show_token_btn.setStyleSheet(self.retro_button_style("#7a5c00", "#b3890a", "#3a2c00", "#ffc04d", "#ffd98a", "#241a00"))
        self.show_token_btn.toggled.connect(self.toggle_token_visibility)
        token_row.addWidget(self.show_token_btn)

        self.list_cloud_btn = QPushButton("REFREASH")
        self.list_cloud_btn.setStyleSheet(self.retro_button_style("#004a1a", "#006622", "#00220c", "#33ff33", "#66ff66", "#001a08"))
        self.list_cloud_btn.clicked.connect(self.refresh_cloud_files)
        token_row.addWidget(self.list_cloud_btn)

        screen_layout.addLayout(token_row)

        lists_row = QHBoxLayout()
        lists_row.setSpacing(20)

        local_col = QVBoxLayout()
        local_header = QLabel("LOCAL SAVES (Hydro 1/saves)")
        local_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        local_header.setStyleSheet(f"""
            font-family: {FONT_FAMILY};
            font-size: 11px;
            font-weight: bold;
            color: #22aa22;
        """)
        local_col.addWidget(local_header)

        self.local_list = QListWidget()
        self.local_list.setStyleSheet(self.list_style())
        local_col.addWidget(self.local_list)
        lists_row.addLayout(local_col)

        cloud_col = QVBoxLayout()
        cloud_header = QLabel("CLOUD FILES")
        cloud_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cloud_header.setStyleSheet(f"""
            font-family: {FONT_FAMILY};
            font-size: 11px;
            font-weight: bold;
            color: #22aa22;
        """)
        cloud_col.addWidget(cloud_header)

        self.cloud_list = QListWidget()
        self.cloud_list.setStyleSheet(self.list_style())
        cloud_col.addWidget(self.cloud_list)
        lists_row.addLayout(cloud_col)

        screen_layout.addLayout(lists_row, 1)

        action_row = QHBoxLayout()
        action_row.setSpacing(20)

        self.upload_btn = QPushButton("UPLOAD SELECTED >>")
        self.upload_btn.setStyleSheet(self.retro_button_style("#a31d1d", "#cc2424", "#550000", "#ff5555", "#ff7777", "#220000"))
        self.upload_btn.clicked.connect(self.do_upload)
        action_row.addWidget(self.upload_btn)

        self.download_btn = QPushButton("<< DOWNLOAD SELECTED")
        self.download_btn.setStyleSheet(self.retro_button_style("#a31d1d", "#cc2424", "#550000", "#ff5555", "#ff7777", "#220000"))
        self.download_btn.clicked.connect(self.do_download)
        action_row.addWidget(self.download_btn)

        screen_layout.addLayout(action_row)

        self.status_label = QLabel("STATUS: STANDBY")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet(f"""
            font-family: {FONT_FAMILY};
            font-size: 11px;
            font-weight: bold;
            color: #33ff33;
            min-height: 28px;
        """)
        screen_layout.addWidget(self.status_label)

        footer_label = QLabel("AUTH: BEARER TOKEN | ENDPOINTS: /api/stay-civilised/")
        footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer_label.setStyleSheet(f"""
            font-family: {FONT_FAMILY};
            font-size: 9px;
            color: #22aa22;
            font-weight: bold;
        """)
        screen_layout.addWidget(footer_label)

        main_layout.addWidget(self.card, 0, 0, Qt.AlignmentFlag.AlignCenter)

    def retro_button_style(self, base, hover, pressed_bg, border, border_hover, border_pressed):
        return f"""
            QPushButton {{
                background-color: {base};
                color: #ffffff;
                border: 3px solid;
                border-top-color: {border_hover};
                border-left-color: {border_hover};
                border-right-color: {border};
                border-bottom-color: {border};
                border-radius: 4px;
                font-family: {FONT_FAMILY};
                font-size: 12px;
                font-weight: bold;
                padding: 8px 14px;
            }}
            QPushButton:hover {{ background-color: {hover}; }}
            QPushButton:pressed {{
                background-color: {pressed_bg};
                padding: 10px 12px 6px 16px;
            }}
            QPushButton:disabled {{ color: #999999; border-color: #444444; background-color: #222222; }}
        """

    def list_style(self):
        return f"""
            QListWidget {{
                background-color: #020c03;
                border: 2px solid #22aa22;
                border-radius: 4px;
                color: #33ff33;
                font-family: {FONT_FAMILY};
                font-size: 12px;
                outline: none;
            }}
            QListWidget::item {{ padding: 5px; }}
            QListWidget::item:selected {{ background-color: #0a3a0a; color: #99ff99; }}
        """

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        if not self.dam_pixmap.isNull():
            img_aspect = self.dam_pixmap.width() / self.dam_pixmap.height()
            scaled_h = self.height()
            scaled_w = int(scaled_h * img_aspect)

            min_width = int(self.width() * 1.25)
            if scaled_w < min_width:
                scaled_w = min_width
                scaled_h = int(scaled_w / img_aspect)

            offset_x = -int((scaled_w - self.width()) / 2)
            offset_y = (self.height() - scaled_h) // 2
            painter.drawPixmap(offset_x, offset_y, scaled_w, scaled_h, self.dam_pixmap)
            painter.fillRect(self.rect(), QColor(1, 22, 2, 195))
        else:
            painter.fillRect(self.rect(), QColor(2, 20, 3))

        vignette = QRadialGradient(self.width() / 2, self.height() / 2, max(self.width(), self.height()) / 1.5)
        vignette.setColorAt(0.0, QColor(0, 0, 0, 0))
        vignette.setColorAt(0.7, QColor(0, 0, 0, 70))
        vignette.setColorAt(1.0, QColor(0, 0, 0, 230))
        painter.fillRect(self.rect(), vignette)

    def load_saved_token(self):
        try:
            if os.path.exists(self.token_path):
                with open(self.token_path, "r") as f:
                    token = f.read().strip()
                if token:
                    self.token_input.setText(token)
        except Exception as e:
            print("Failed to read stored token:", e)

    def store_token(self, token):
        try:
            with open(self.token_path, "w") as f:
                f.write(token)
        except Exception as e:
            print("Failed to store token:", e)

    def toggle_token_visibility(self, checked):
        self.token_input.setEchoMode(
            QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password
        )
        self.show_token_btn.setText("HIDE" if checked else "SHOW")

    def set_status(self, message, is_error=False):
        color = "#ff4444" if is_error else "#33ff33"
        self.status_label.setText(message)
        self.status_label.setStyleSheet(f"""
            font-family: {FONT_FAMILY};
            font-size: 11px;
            font-weight: bold;
            color: {color};
            min-height: 28px;
        """)

    def set_busy(self, busy):
        self._busy = busy
        for btn in (self.list_cloud_btn, self.upload_btn, self.download_btn):
            btn.setEnabled(not busy)

    def get_token(self):
        return self.token_input.text().strip()

    def refresh_local_saves(self):
        self.local_list.clear()
        if not os.path.exists(self.saves_dir):
            os.makedirs(self.saves_dir, exist_ok=True)
        files = [f for f in os.listdir(self.saves_dir) if f.endswith(".json")]
        for filename in sorted(files, reverse=True):
            self.local_list.addItem(filename)
        if self.local_list.count() == 0:
            self.local_list.addItem("--- No local save files ---")

    def refresh_cloud_files(self):
        token = self.get_token()
        if not token:
            self.set_status("STATUS: ERROR - ENTER AN API TOKEN FIRST", True)
            return
        self.store_token(token)
        self.set_busy(True)
        self.set_status("STATUS: FETCHING CLOUD FILE LIST...")
        self.api_call("/api/stay-civilised/list_files", "GET", None, self.on_list_done)

    def on_list_done(self, result, error):
        self.cloud_list.clear()
        if error:
            self.set_status(f"STATUS: LIST FAILED - {error}", True)
            return
        files = result.get("files", []) if isinstance(result, dict) else []
        for filename in files:
            self.cloud_list.addItem(filename)
        if self.cloud_list.count() == 0:
            self.cloud_list.addItem("--- No cloud save files ---")
        self.set_status(f"STATUS: FOUND {len(files)} CLOUD FILE(S)")

    def do_upload(self):
        item = self.local_list.currentItem()
        if not item:
            self.set_status("STATUS: ERROR - SELECT A LOCAL SAVE FIRST", True)
            return
        filename = item.text()
        filepath = os.path.join(self.saves_dir, filename)
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
        except Exception as e:
            self.set_status(f"STATUS: ERROR READING LOCAL FILE - {e}", True)
            return
        payload = dict(data)
        payload["_filename"] = filename
        self.set_busy(True)
        self.set_status(f"STATUS: UPLOADING {filename}...")
        self.api_call("/api/stay-civilised/save_file", "POST", payload,
                      lambda result, error, fn=filename: self.on_upload_done(result, error, fn))

    def on_upload_done(self, result, error, filename):
        if error:
            self.set_status(f"STATUS: UPLOAD FAILED - {error}", True)
            return
        self.set_status(f"STATUS: UPLOADED {filename} TO CLOUD")

    def do_download(self):
        item = self.cloud_list.currentItem()
        if not item:
            self.set_status("STATUS: ERROR - SELECT A CLOUD FILE FIRST", True)
            return
        filename = item.text()
        path = "/api/stay-civilised/get_file?filename=" + urllib.parse.quote(filename)
        self.set_busy(True)
        self.set_status(f"STATUS: DOWNLOADING {filename}...")
        self.api_call(path, "GET", None,
                      lambda result, error, fn=filename: self.on_download_done(result, error, fn))

    def on_download_done(self, result, error, filename):
        if error:
            self.set_status(f"STATUS: DOWNLOAD FAILED - {error}", True)
            return
        safe_name = os.path.basename(filename)
        if not safe_name.endswith(".json"):
            safe_name += ".json"
        filepath = os.path.join(self.saves_dir, safe_name)
        try:
            os.makedirs(self.saves_dir, exist_ok=True)
            with open(filepath, "w") as f:
                json.dump(result, f, indent=4)
        except Exception as e:
            self.set_status(f"STATUS: ERROR WRITING LOCAL FILE - {e}", True)
            return
        self.refresh_local_saves()
        if result == {}:
            self.set_status(f"STATUS: SAVED {safe_name} (WARNING: EMPTY/MISSING ON SERVER)", True)
        else:
            self.set_status(f"STATUS: DOWNLOADED {safe_name}")

    def api_call(self, path, method="GET", payload=None, callback=None):
        self._pending_cb = callback
        threading.Thread(target=self._worker, args=(path, method, payload), daemon=True).start()

    def _worker(self, path, method, payload):
        try:
            url = BASE_URL + path
            data = None
            headers = {
                "Accept": "application/json",
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/139.0.0.0 Safari/537.36"
                ),
            }
            if payload is not None:
                data = json.dumps(payload).encode("utf-8")
                headers["Content-Type"] = "application/json"
            token = self.get_token()
            if token:
                headers["Authorization"] = f"Bearer {token}"
            req = urllib.request.Request(url, data=data, method=method, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as resp:
                body = resp.read().decode("utf-8")
            result = json.loads(body) if body else {}
            self.api_done.emit(result, "")
        except urllib.error.HTTPError as e:
            try:
                detail = json.loads(e.read().decode("utf-8")).get("error", "")
            except Exception:
                detail = ""
            self.api_done.emit(None, f"HTTP {e.code} {detail}".strip())
        except Exception as e:
            self.api_done.emit(None, str(e))

    def handle_api_result(self, result, error):
        cb = self._pending_cb
        self._pending_cb = None
        self.set_busy(False)
        if cb:
            cb(result, error)

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh_local_saves()

    def closeEvent(self, event):
        self.hide()
        event.ignore()


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = CloudSaveWindow()
    window.show()
    sys.exit(app.exec())
