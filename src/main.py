import sys
import os

# Adiciona o diretório atual ao path para importações relativas funcionarem se rodar main.py diretamente
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import QApplication
from gai_pro.ui.login_window import LoginWindow
from gai_pro.ui.main_window import MainWindow

class GAIApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.login_win = LoginWindow()
        self.main_win = None
        
        # Conectar sinal de sucesso no login
        self.login_win.login_success.connect(self.show_main_window)

    def run(self):
        self.login_win.show()
        sys.exit(self.app.exec())

    def show_main_window(self, username):
        self.login_win.close()
        self.main_win = MainWindow(username)
        self.main_win.show()

if __name__ == "__main__":
    # Garantir que os diretórios necessários existam
    os.makedirs("gai_pro/data/log", exist_ok=True)
    os.makedirs("gai_pro/config", exist_ok=True)
    
    gai_app = GAIApp()
    gai_app.run()
