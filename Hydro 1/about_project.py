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
                background-color: #808080;
                color: #222222;
            }

            QLabel {
                background: transparent;
                color: #222222;
            }

            QPushButton {
                background-color: #6a6a6a;
                color: #222222;
                border: 2px solid #444;
                border-radius: 2px;
                padding: 8px;
                min-height: 30px;
            }

            QPushButton:hover {
                background-color: #7a7a7a;
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
            color: #222222;
        """)

        main_layout.addWidget(title)

        subtitle = QLabel("Grid Management Simulator")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("""
            color: #444444;
            font-size: 14px;
        """)

        main_layout.addWidget(subtitle)

        # =====================================================
        # Separator
        # =====================================================

        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("background-color: #555;")

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
            color: #333366;
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
            color: #222222;
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

        footer = QLabel("Poaitron")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet("""
            color: #555;
            font-size: 11px;
        """)

        main_layout.addWidget(footer)

    def closeEvent(self, event):
        self.hide()
        event.ignore()