from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QFrame, QSizePolicy)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QFont, QPalette, QColor

class LoginWindow(QWidget):
    authenticated = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("AI Surveillance - Login")
        self.setFixedSize(450, 550)
        self.setStyleSheet("""
            QWidget { background-color: #0d0d0d; color: #fff; font-family: 'Outfit', sans-serif; }
            QFrame#Container { background-color: #161616; border-radius: 20px; border: 1px solid #333; padding: 40px; }
            QLabel#Title { font-size: 28px; font-weight: bold; color: #00ffcc; margin-bottom: 5px; }
            QLabel#Subtitle { font-size: 14px; color: #777; margin-bottom: 30px; }
            QLineEdit { 
                background-color: #222; border: 1px solid #444; border-radius: 8px; 
                padding: 12px; font-size: 14px; color: #fff; margin-bottom: 20px;
            }
            QLineEdit:focus { border: 1px solid #00ffcc; background-color: #1a1a1a; }
            QPushButton { 
                background-color: #00ffcc; color: #000; font-weight: bold; 
                padding: 15px; border-radius: 8px; font-size: 16px; margin-top: 10px;
            }
            QPushButton:hover { background-color: #00ddbb; }
            QPushButton:pressed { background-color: #00aa99; }
            QLabel#Error { color: #ff5555; font-size: 12px; margin-top: 15px; }
        """)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        container = QFrame()
        container.setObjectName("Container")
        c_layout = QVBoxLayout(container)
        c_layout.setAlignment(Qt.AlignCenter)
        
        # Header
        title = QLabel("WELCOME BACK")
        title.setObjectName("Title")
        title.setAlignment(Qt.AlignCenter)
        subtitle = QLabel("Please sign in to continue")
        subtitle.setObjectName("Subtitle")
        subtitle.setAlignment(Qt.AlignCenter)
        
        c_layout.addWidget(title)
        c_layout.addWidget(subtitle)
        
        # Fields
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Username")
        self.user_input.setText("admin") # Pre-filled for development
        c_layout.addWidget(self.user_input)
        
        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Password")
        self.pass_input.setEchoMode(QLineEdit.Password)
        self.pass_input.setText("admin") # Pre-filled for development
        c_layout.addWidget(self.pass_input)
        
        self.btn_login = QPushButton("LOGIN")
        self.btn_login.clicked.connect(self._handle_login)
        c_layout.addWidget(self.btn_login)
        
        self.error_label = QLabel("")
        self.error_label.setObjectName("Error")
        self.error_label.setAlignment(Qt.AlignCenter)
        c_layout.addWidget(self.error_label)
        
        layout.addWidget(container)

    def _handle_login(self):
        user = self.user_input.text().strip()
        pwd = self.pass_input.text().strip()
        
        if user == "admin" and pwd == "admin":
            self.authenticated.emit(True)
        else:
            self.error_label.setText("Invalid credentials. Try admin/admin.")

if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())
