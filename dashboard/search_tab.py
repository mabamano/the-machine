"""
dashboard/search_tab.py

EmergencySearchTab — PySide6 widget for searching surveillance footage
using facial recognition. Uses SearchWorker (QThread) to keep the UI
responsive during heavy ML inference and database queries.
"""

import sys
import os
import sqlite3

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog,
    QScrollArea, QLabel, QFrame, QGridLayout, QSizePolicy,
    QMessageBox, QGraphicsOpacityEffect,
)
from PySide6.QtCore import (
    Qt, QThread, Signal, QPropertyAnimation, QEasingCurve,
    QSequentialAnimationGroup, QTimer,
)
from PySide6.QtGui import QPixmap, QFont, QColor, QPainter, QBrush, QPen

# ---------------------------------------------------------------------------
# Safe import of project modules (graceful fallback for isolated testing)
# ---------------------------------------------------------------------------
try:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from face_recognition.main import FaceRecognitionModule
    from search_engine.matcher import SearchMatcher
    _IMPORTS_OK = True
except ImportError as _e:
    print(f"[search_tab] Warning: project imports unavailable — {_e}")
    _IMPORTS_OK = False


# ---------------------------------------------------------------------------
# SearchWorker — runs SearchMatcher in a background QThread
# ---------------------------------------------------------------------------

class SearchWorker(QThread):
    """
    Runs `SearchMatcher.search_for_target` in a dedicated thread so the
    PySide6 event loop never blocks during face detection / DB queries.

    Signals
    -------
    results_ready(list)   : emitted on success with the top-5 match dicts
    error_occurred(str)   : emitted on any exception, including 'No Face Detected'
    no_face_detected()    : emitted specifically when no face is found in the
                            uploaded image (special-cased for UI alert)
    """

    results_ready = Signal(list)
    error_occurred = Signal(str)
    no_face_detected = Signal()

    # Sentinel substring from SearchMatcher when no face found
    _NO_FACE_KEY = "no faces detected"

    def __init__(self, target_image_path: str, db_path: str = "surveillance_history.db",
                 parent=None):
        super().__init__(parent)
        self.target_image_path = target_image_path
        self.db_path = db_path

    # ------------------------------------------------------------------
    def run(self):
        if not _IMPORTS_OK:
            self.error_occurred.emit(
                "Project modules unavailable. "
                "Ensure face_recognition and search_engine are on PYTHONPATH."
            )
            return

        try:
            # Each thread gets its own model + DB connection (thread-safety)
            fr_module = FaceRecognitionModule(device="cpu")
            matcher = SearchMatcher(fr_module)

            # Resolve absolute DB path relative to the project root
            abs_db = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "..", self.db_path)
            )

            with sqlite3.connect(abs_db) as conn:
                matches = matcher.search_for_target(self.target_image_path, conn)

            self.results_ready.emit(matches)

        except ValueError as exc:
            msg = str(exc)
            if self._NO_FACE_KEY in msg.lower():
                self.no_face_detected.emit()
            else:
                self.error_occurred.emit(msg)
        except Exception as exc:  # noqa: BLE001
            self.error_occurred.emit(str(exc))


# ---------------------------------------------------------------------------
# ResultCard — a single thumbnail + metadata widget
# ---------------------------------------------------------------------------

class ResultCard(QFrame):
    """Styled card displaying a sighting thumbnail, timestamp, and confidence."""

    def __init__(self, match: dict, base_dir: str, parent=None):
        super().__init__(parent)
        self.setFixedSize(210, 280)
        self.setStyleSheet("""
            QFrame {
                background-color: #161616;
                border: 1px solid #2a2a2a;
                border-radius: 12px;
            }
            QFrame:hover {
                border: 1px solid #00ffcc;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(6)

        # --- Thumbnail ---
        img_label = QLabel()
        img_label.setAlignment(Qt.AlignCenter)
        img_label.setFixedSize(188, 160)
        img_label.setStyleSheet(
            "background-color: #0d0d0d; border-radius: 8px; border: 1px solid #333;"
        )

        frame_path = match.get("frame_path", "")
        full_path = os.path.abspath(os.path.join(base_dir, frame_path)) if frame_path else ""

        if full_path and os.path.exists(full_path):
            pix = QPixmap(full_path).scaled(
                188, 160, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            img_label.setPixmap(pix)
        else:
            img_label.setText("🖼️\nFrame not found")
            img_label.setStyleSheet(
                img_label.styleSheet()
                + " color: #555; font-size: 12px; qproperty-alignment: AlignCenter;"
            )

        layout.addWidget(img_label)

        # --- Timestamp ---
        timestamp_raw = match.get("timestamp", "")
        ts_display = timestamp_raw[:19] if timestamp_raw else "Unknown time"
        ts_label = QLabel(f"🕐  {ts_display}")
        ts_label.setStyleSheet("color: #aaaaaa; font-size: 11px;")
        ts_label.setAlignment(Qt.AlignCenter)
        ts_label.setWordWrap(True)
        layout.addWidget(ts_label)

        # --- Confidence badge ---
        score = match.get("confidence_score", 0.0)
        pct = score * 100.0
        badge = _ConfidenceBadge(pct)
        layout.addWidget(badge, alignment=Qt.AlignCenter)

        # Subtle fade-in on creation
        effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(effect)
        anim = QPropertyAnimation(effect, b"opacity", self)
        anim.setDuration(350)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.start(QPropertyAnimation.DeleteWhenStopped)


class _ConfidenceBadge(QLabel):
    """Coloured confidence % pill — green > 70 %, amber 40-70 %, red below."""

    def __init__(self, pct: float, parent=None):
        super().__init__(parent)
        self.setText(f"  {pct:.1f}% match  ")
        if pct >= 70:
            bg, fg = "#003d2e", "#00ffcc"
        elif pct >= 40:
            bg, fg = "#3d2e00", "#ffcc00"
        else:
            bg, fg = "#3d0000", "#ff5555"
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {bg};
                color: {fg};
                border: 1px solid {fg};
                border-radius: 10px;
                font-size: 12px;
                font-weight: bold;
                padding: 2px 6px;
            }}
        """)
        self.setAlignment(Qt.AlignCenter)


# ---------------------------------------------------------------------------
# PulsingDot — animated status indicator
# ---------------------------------------------------------------------------

class _PulsingDot(QWidget):
    """Tiny pulsating circle shown while a search is in progress."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(12, 12)
        self._opacity = 1.0
        effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(effect)
        self._anim = QPropertyAnimation(effect, b"opacity", self)
        self._anim.setDuration(700)
        self._anim.setStartValue(1.0)
        self._anim.setEndValue(0.2)
        self._anim.setLoopCount(-1)
        self._anim.setEasingCurve(QEasingCurve.InOutSine)

    def start(self):
        self._anim.start()

    def stop(self):
        self._anim.stop()

    def paintEvent(self, event):  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setBrush(QBrush(QColor("#00ffcc")))
        p.setPen(QPen(Qt.NoPen))
        p.drawEllipse(1, 1, 10, 10)


# ---------------------------------------------------------------------------
# EmergencySearchTab — main widget
# ---------------------------------------------------------------------------

class EmergencySearchTab(QWidget):
    """
    Full-featured emergency person-search tab.

    Layout
    ------
    ┌──────────────────────────────────────────────────────┐
    │  🚨 EMERGENCY SEARCH                      [header]  │
    ├──────────────┬───────────────────────────────────────┤
    │ Upload panel │  Potential Sightings (QScrollArea)    │
    │  [preview]   │  [ResultCard] [ResultCard] …          │
    │  [Upload btn]│                                       │
    │  [status]    │                                       │
    └──────────────┴───────────────────────────────────────┘
    """

    # DB path relative to project root; override if needed
    DB_PATH = "surveillance_history.db"

    def __init__(self, parent=None):
        super().__init__(parent)
        self._search_worker: SearchWorker | None = None
        self._base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self._build_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(20)

        # ---- Header row ----
        header_row = QHBoxLayout()

        title = QLabel("🚨  EMERGENCY SEARCH")
        title.setStyleSheet(
            "color: #ff3333; font-size: 22px; font-weight: bold; letter-spacing: 2px;"
        )
        header_row.addWidget(title)
        header_row.addStretch()

        subtitle = QLabel("Facial recognition · last 24 hours")
        subtitle.setStyleSheet("color: #555; font-size: 13px;")
        header_row.addWidget(subtitle)

        root.addLayout(header_row)

        # Thin red accent divider
        divider = QFrame()
        divider.setFixedHeight(2)
        divider.setStyleSheet("background: qlineargradient("
                              "x1:0,y1:0,x2:1,y2:0,"
                              "stop:0 #ff3333, stop:1 transparent);")
        root.addWidget(divider)

        # ---- Content row ----
        content_row = QHBoxLayout()
        content_row.setSpacing(20)

        content_row.addWidget(self._build_control_panel())
        content_row.addWidget(self._build_results_panel(), stretch=1)

        root.addLayout(content_row)

    def _build_control_panel(self) -> QFrame:
        panel = QFrame()
        panel.setFixedWidth(290)
        panel.setStyleSheet("""
            QFrame {
                background-color: #111111;
                border: 1px solid #222;
                border-radius: 14px;
            }
        """)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(18, 20, 18, 20)
        layout.setSpacing(14)
        layout.setAlignment(Qt.AlignTop)

        # Section label
        lbl = QLabel("TARGET PHOTO")
        lbl.setStyleSheet("color: #555; font-size: 11px; letter-spacing: 2px;")
        layout.addWidget(lbl)

        # Image preview box
        self._preview = QLabel()
        self._preview.setAlignment(Qt.AlignCenter)
        self._preview.setFixedSize(254, 220)
        self._preview.setText("No photo selected")
        self._preview.setStyleSheet("""
            QLabel {
                color: #444;
                background-color: #0d0d0d;
                border: 2px dashed #2a2a2a;
                border-radius: 10px;
                font-size: 13px;
            }
        """)
        layout.addWidget(self._preview)

        # Upload button
        self._upload_btn = QPushButton("⬆   Upload Photo")
        self._upload_btn.setFixedHeight(46)
        self._upload_btn.setCursor(Qt.PointingHandCursor)
        self._upload_btn.setStyleSheet("""
            QPushButton {
                background-color: #cc0000;
                color: #fff;
                font-weight: bold;
                font-size: 14px;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover  { background-color: #e60000; }
            QPushButton:pressed { background-color: #990000; }
            QPushButton:disabled { background-color: #3a1a1a; color: #666; }
        """)
        self._upload_btn.clicked.connect(self._on_upload)
        layout.addWidget(self._upload_btn)

        # Status row (dot + text)
        status_row = QHBoxLayout()
        status_row.setSpacing(8)

        self._dot = _PulsingDot()
        self._dot.setVisible(False)
        status_row.addWidget(self._dot)

        self._status = QLabel("Ready — upload a photo to begin.")
        self._status.setStyleSheet("color: #555; font-size: 12px;")
        self._status.setWordWrap(True)
        status_row.addWidget(self._status, stretch=1)

        layout.addLayout(status_row)
        layout.addStretch()

        return panel

    def _build_results_panel(self) -> QFrame:
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background-color: #111111;
                border: 1px solid #222;
                border-radius: 14px;
            }
        """)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        # Panel header
        header_row = QHBoxLayout()
        s_title = QLabel("Potential Sightings")
        s_title.setStyleSheet("color: #aaa; font-size: 16px; font-weight: bold;")
        header_row.addWidget(s_title)
        header_row.addStretch()

        self._count_badge = QLabel("")
        self._count_badge.setStyleSheet("""
            QLabel {
                background-color: #1e1e1e;
                color: #666;
                border-radius: 10px;
                padding: 2px 10px;
                font-size: 12px;
            }
        """)
        header_row.addWidget(self._count_badge)
        layout.addLayout(header_row)

        # Scroll area
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setStyleSheet("""
            QScrollArea { background: transparent; border: none; }
            QScrollBar:vertical {
                background: #111; width: 6px; border-radius: 3px;
            }
            QScrollBar::handle:vertical {
                background: #333; border-radius: 3px;
            }
            QScrollBar::handle:vertical:hover { background: #00ffcc; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
        """)

        self._scroll_content = QWidget()
        self._scroll_content.setStyleSheet("background: transparent;")
        self._grid = QGridLayout(self._scroll_content)
        self._grid.setContentsMargins(4, 4, 4, 4)
        self._grid.setSpacing(14)
        self._grid.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        self._scroll.setWidget(self._scroll_content)
        layout.addWidget(self._scroll)

        # Empty-state placeholder (shown before any search)
        self._empty_label = QLabel("Upload a photo above to search surveillance records.")
        self._empty_label.setAlignment(Qt.AlignCenter)
        self._empty_label.setStyleSheet("color: #333; font-size: 14px;")
        self._grid.addWidget(self._empty_label, 0, 0, 1, 3)

        return panel

    # ------------------------------------------------------------------
    # Slots / handlers
    # ------------------------------------------------------------------

    def _on_upload(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Photo", "",
            "Images (*.png *.jpg *.jpeg *.bmp *.webp)"
        )
        if not path:
            return

        # Show preview thumbnail
        pix = QPixmap(path).scaled(254, 220, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self._preview.setPixmap(pix)
        self._preview.setStyleSheet(
            "background-color: #0d0d0d; border: 2px solid #333; border-radius: 10px;"
        )

        # Clear previous results
        self._clear_results()
        self._set_searching(True)

        # Launch worker
        self._search_worker = SearchWorker(path, self.DB_PATH)
        self._search_worker.results_ready.connect(self._on_results)
        self._search_worker.error_occurred.connect(self._on_error)
        self._search_worker.no_face_detected.connect(self._on_no_face)
        self._search_worker.start()

    def _on_results(self, matches: list):
        self._set_searching(False)
        self._clear_results()

        count = len(matches)
        self._count_badge.setText(f"{count} result{'s' if count != 1 else ''}")
        self._count_badge.setStyleSheet("""
            QLabel {
                background-color: #003d2e;
                color: #00ffcc;
                border-radius: 10px;
                padding: 2px 10px;
                font-size: 12px;
                font-weight: bold;
            }
        """)

        if not matches:
            self._status.setText("Search complete — no sightings in the last 24 hours.")
            self._status.setStyleSheet("color: #666; font-size: 12px;")
            lbl = QLabel("🔍  No sightings found in the last 24 hours.")
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("color: #444; font-size: 14px;")
            self._grid.addWidget(lbl, 0, 0, 1, 3)
            return

        self._status.setText(f"Done — {count} potential sighting(s) found.")
        self._status.setStyleSheet("color: #00ffcc; font-size: 12px;")

        cols = 3
        for idx, match in enumerate(matches):
            card = ResultCard(match, self._base_dir)
            row, col = divmod(idx, cols)
            self._grid.addWidget(card, row, col)

    def _on_no_face(self):
        """Show a clear, friendly QMessageBox when no face is detected."""
        self._set_searching(False)
        self._status.setText("No face detected in the uploaded image.")
        self._status.setStyleSheet("color: #ff8800; font-size: 12px;")
        self._count_badge.setText("")

        dlg = QMessageBox(self)
        dlg.setWindowTitle("No Face Detected")
        dlg.setIcon(QMessageBox.Warning)
        dlg.setText(
            "<b style='font-size:15px;'>No face detected</b>"
        )
        dlg.setInformativeText(
            "The uploaded image does not contain a recognisable face.\n\n"
            "Please try a clear, front-facing photograph with good lighting."
        )
        dlg.setStandardButtons(QMessageBox.Ok)
        dlg.setStyleSheet("""
            QMessageBox {
                background-color: #111;
                color: #eee;
            }
            QLabel { color: #eee; }
            QPushButton {
                background-color: #cc0000;
                color: #fff;
                border-radius: 6px;
                padding: 6px 20px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #e60000; }
        """)
        dlg.exec()

    def _on_error(self, msg: str):
        self._set_searching(False)
        self._status.setText(f"Error: {msg}")
        self._status.setStyleSheet("color: #ff4444; font-size: 12px;")
        self._count_badge.setText("")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _set_searching(self, active: bool):
        self._upload_btn.setEnabled(not active)
        self._dot.setVisible(active)
        if active:
            self._dot.start()
            self._status.setText("Searching database…")
            self._status.setStyleSheet("color: #00ffcc; font-size: 12px;")
        else:
            self._dot.stop()

    def _clear_results(self):
        while self._grid.count():
            item = self._grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()


# ---------------------------------------------------------------------------
# Standalone test entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Dark palette for standalone test
    window = QWidget()
    window.setWindowTitle("Emergency Search — Standalone Test")
    window.setStyleSheet("background-color: #0d0d0d; color: #eee; font-family: 'Outfit', sans-serif;")
    window.resize(1100, 680)

    lay = QVBoxLayout(window)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.addWidget(EmergencySearchTab())

    window.show()
    sys.exit(app.exec())
