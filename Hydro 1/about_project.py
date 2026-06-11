from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame
)

from PyQt6.QtGui import (
    QPixmap,
    QDesktopServices
)

from PyQt6.QtCore import (
    Qt,
    QUrl
)


class AboutWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("About")
        self.setStyleSheet("""
            QWidget {
                background-color: #1a1a1a;
                color: white;
            }

            QLabel {
                background: transparent;
                color: white;
            }

            QPushButton {
                background-color: #2d2d2d;
                color: white;
                border: 1px solid #555;
                border-radius: 6px;
                padding: 8px;
                min-height: 30px;
            }

            QPushButton:hover {
                background-color: #3a3a3a;
            }

            QPushButton:pressed {
                background-color: #555;
            }
        """)

        self.resize(700, 400)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # =====================================================
        # Logo
        # =====================================================

        logo = QLabel()
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        pixmap = QPixmap("logo.png")

        if not pixmap.isNull():
            logo.setPixmap(
                pixmap.scaled(
                    200,
                    200,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
            )
        else:
            logo.setText("logo.png not found")

        main_layout.addWidget(logo)

        # =====================================================
        # Title
        # =====================================================

        title = QLabel("Stay Civilised")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: white;
        """)

        main_layout.addWidget(title)

        subtitle = QLabel("Grid Management Simulator")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("""
            color: #b0b0b0;
            font-size: 14px;
        """)

        main_layout.addWidget(subtitle)

        # =====================================================
        # Separator
        # =====================================================

        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("background-color: #444;")

        main_layout.addWidget(separator)

        # =====================================================
        # Information
        # =====================================================

        info = QLabel(
            "Version: v0.4.0\n"
            "This is a demo version"
        )

        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info.setStyleSheet("""
            font-size: 14px;
            color: #58a6ff;
        """)

        main_layout.addWidget(info)

        # =====================================================
        # Description
        # =====================================================

        description = QLabel(
            "[placeholder]\n\n"
        )

        description.setWordWrap(True)
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setStyleSheet("""
            font-size: 13px;
            color: white;
        """)

        main_layout.addWidget(description)

        main_layout.addStretch()

        # =====================================================
        # Buttons
        # =====================================================

        button_layout = QHBoxLayout()

        github_button = QPushButton("GitHub")
        github_button.clicked.connect(
            lambda: QDesktopServices.openUrl(
                QUrl("https://github.com/wh4r/Stay-Civilised")
            )
        )

        website_button = QPushButton("Website")
        website_button.clicked.connect(
            lambda: QDesktopServices.openUrl(
                QUrl("https://notes-garden-one.vercel.app/7594")
            )
        )

        button_layout.addWidget(github_button)
        button_layout.addWidget(website_button)

        main_layout.addLayout(button_layout)

        # =====================================================
        # Footer
        # =====================================================

        footer = QLabel("Project Polaris")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet("""
            color: #888;
            font-size: 11px;
        """)

        main_layout.addWidget(footer)

    def closeEvent(self, event):
        self.hide()
        event.ignore()