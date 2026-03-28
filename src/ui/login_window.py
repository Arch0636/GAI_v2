from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QMessageBox, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from ..auth.auth_manager import AuthManager
from .styles import get_dark_theme_stylesheet

class LoginWindow(QWidget):
    login_success = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.auth = AuthManager()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("GAI Pro - Login")
        self.setFixedSize(400, 500)
        self.setStyleSheet(get_dark_theme_stylesheet())

        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(15)

        title = QLabel("🚀 GAI Pro")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        self.label_mode = QLabel("Entre com suas credenciais")
        self.label_mode.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label_mode)

        self.edit_user = QLineEdit()
        self.edit_user.setPlaceholderText("Usuário")
        layout.addWidget(self.edit_user)

        self.edit_pass = QLineEdit()
        self.edit_pass.setPlaceholderText("Senha")
        self.edit_pass.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.edit_pass)

        self.edit_confirm = QLineEdit()
        self.edit_confirm.setPlaceholderText("Confirmar Senha")
        self.edit_confirm.setEchoMode(QLineEdit.EchoMode.Password)
        self.edit_confirm.setVisible(False)
        layout.addWidget(self.edit_confirm)

        self.btn_login = QPushButton("ENTRAR")
        self.btn_login.clicked.connect(self.handle_login)
        layout.addWidget(self.btn_login)

        self.btn_toggle = QPushButton("Criar nova conta")
        self.btn_toggle.setObjectName("btn_register")
        self.btn_toggle.clicked.connect(self.toggle_mode)
        layout.addWidget(self.btn_toggle)

        self.setLayout(layout)
        self.is_register = False

    def toggle_mode(self):
        self.is_register = not self.is_register
        if self.is_register:
            self.label_mode.setText("Crie sua conta gratuita")
            self.btn_login.setText("CADASTRAR")
            self.btn_toggle.setText("Já tenho uma conta")
            self.edit_confirm.setVisible(True)
        else:
            self.label_mode.setText("Entre com suas credenciais")
            self.btn_login.setText("ENTRAR")
            self.btn_toggle.setText("Criar nova conta")
            self.edit_confirm.setVisible(False)

    def handle_login(self):
        user = self.edit_user.text()
        pw = self.edit_pass.text()
        
        if not user or not pw:
            QMessageBox.warning(self, "Erro", "Preencha todos os campos!")
            return

        if self.is_register:
            confirm = self.edit_confirm.text()
            if pw != confirm:
                QMessageBox.warning(self, "Erro", "As senhas não coincidem!")
                return
            
            success, msg = self.auth.register(user, pw)
            if success:
                QMessageBox.information(self, "Sucesso", msg)
                self.toggle_mode()
            else:
                QMessageBox.critical(self, "Erro", msg)
        else:
            success, msg = self.auth.login(user, pw)
            if success:
                self.login_success.emit(user)
            else:
                QMessageBox.critical(self, "Erro", msg)
