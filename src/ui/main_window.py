import os
import json
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFileDialog, QTextEdit, QCheckBox, QComboBox, QProgressBar, QSpinBox,
    QGroupBox, QFormLayout, QTabWidget, QLineEdit, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QTextCursor
from ..core.generator import GeneratorThread
from ..ui.styles import get_dark_theme_stylesheet

class MainWindow(QWidget):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.destino_selecionado = ""
        self.profiles_path = "gai_pro/config/profiles.json"
        self.init_ui()
        self.load_profiles()

    def init_ui(self):
        self.setWindowTitle(f"GAI Pro v2.2 - Olá, {self.username}")
        self.setMinimumSize(700, 800)
        
        self.setStyleSheet(get_dark_theme_stylesheet())

        main_layout = QVBoxLayout()

        # Cabeçalho e Perfis
        header_layout = QHBoxLayout()
        header = QLabel("🚀 GAI Pro v2.2")
        header.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        header_layout.addWidget(header)
        
        profile_group = QGroupBox("Perfis de Geração")
        profile_layout = QHBoxLayout()
        self.combo_profiles = QComboBox()
        self.btn_load_profile = QPushButton("Carregar")
        self.btn_load_profile.clicked.connect(self.load_selected_profile)
        self.btn_save_profile = QPushButton("Salvar")
        self.btn_save_profile.setObjectName("btn_save")
        self.btn_save_profile.clicked.connect(self.save_current_profile)
        self.btn_del_profile = QPushButton("Excluir")
        self.btn_del_profile.setObjectName("btn_stop")
        self.btn_del_profile.clicked.connect(self.delete_profile)
        
        profile_layout.addWidget(self.combo_profiles)
        profile_layout.addWidget(self.btn_load_profile)
        profile_layout.addWidget(self.btn_save_profile)
        profile_layout.addWidget(self.btn_del_profile)
        profile_group.setLayout(profile_layout)
        header_layout.addWidget(profile_group)
        main_layout.addLayout(header_layout)

        # Tabs
        self.tabs = QTabWidget()
        
        # Tab Config
        tab_config = QWidget()
        config_layout = QVBoxLayout()
        
        # Destino
        group_dest = QGroupBox("Localização")
        dest_layout = QHBoxLayout()
        self.edit_dest = QLineEdit()
        self.edit_dest.setReadOnly(True)
        btn_browse = QPushButton("Procurar...")
        btn_browse.clicked.connect(self.selecionar_pasta)
        dest_layout.addWidget(self.edit_dest)
        dest_layout.addWidget(btn_browse)
        group_dest.setLayout(dest_layout)
        config_layout.addWidget(group_dest)

        # Parâmetros
        group_params = QGroupBox("Parâmetros")
        form = QFormLayout()
        self.spin_pastas = QSpinBox()
        self.spin_pastas.setRange(1, 500)
        self.spin_pastas.setValue(10)
        self.spin_pastas.setToolTip("Número de pastas principais a serem criadas.")
        self.spin_arquivos = QSpinBox()
        self.spin_arquivos.setRange(1, 10000)
        self.spin_arquivos.setValue(100)
        self.spin_arquivos.setToolTip("Número de arquivos a serem criados dentro de cada pasta.")
        self.combo_nomes = QComboBox()
        self.combo_nomes.addItems(["Aleatório", "Sequencial", "Timestamp"])
        self.combo_nomes.setToolTip("Define o padrão de nomes para os arquivos gerados.")
        self.edit_exts = QLineEdit()
        self.edit_exts.setPlaceholderText("txt, json, csv...")
        self.edit_exts.setToolTip("Extensões de arquivo separadas por vírgula (ex: txt, json, pdf). Vazio para usar padrão.")
        
        form.addRow("Pastas:", self.spin_pastas)
        form.addRow("Arquivos por Pasta:", self.spin_arquivos)
        form.addRow("Padrão Nomes:", self.combo_nomes)
        form.addRow("Extensões:", self.edit_exts)
        group_params.setLayout(form)
        config_layout.addWidget(group_params)

        # Opções
        group_opts = QGroupBox("Opções Extras")
        opts_layout = QVBoxLayout()
        self.check_sub = QCheckBox("Criar subpastas aleatórias")
        self.check_sub.setToolTip("Cria subpastas adicionais dentro de cada pasta principal.")
        self.check_dist = QCheckBox("Distribuir arquivos em subpastas")
        self.check_dist.setToolTip("Distribui os arquivos entre a pasta principal e suas subpastas.")
        self.check_1kb = QCheckBox("Forçar tamanho fixo de 1 KB (Rápido)")
        self.check_1kb.setChecked(True)
        self.check_1kb.setToolTip("Gera arquivos com tamanho fixo de 1KB, o que é mais rápido.")
        self.check_dates = QCheckBox("Randomizar datas de criação/modificação")
        self.check_dates.setToolTip("Define datas de criação e modificação aleatórias para os arquivos.")
        self.check_av = QCheckBox("🛡️ Incluir arquivos de teste para Antivírus (EICAR)")
        self.check_av.setToolTip("Gera arquivos inofensivos que disparam alertas de antivírus para testar a proteção.")
        self.check_av.setStyleSheet("color: #ffc107; font-weight: bold;")
        
        limit_layout = QHBoxLayout()
        limit_layout.addWidget(QLabel("Limite de Tamanho Total:"))
        self.combo_limit = QComboBox()
        self.combo_limit.addItems(["Sem limite", "10 MB", "100 MB", "500 MB", "1 GB", "5 GB"])
        limit_layout.addWidget(self.combo_limit)
        opts_layout.addLayout(limit_layout)

        self.check_dry = QCheckBox("🔍 MODO SIMULAÇÃO (Dry Run)")
        self.check_dry.setToolTip("Não cria arquivos, apenas calcula estatísticas.")
        self.check_dry.setStyleSheet("color: #0dcaf0; font-weight: bold;")
        
        opts_layout.addWidget(self.check_sub)
        opts_layout.addWidget(self.check_dist)
        opts_layout.addWidget(self.check_1kb)
        opts_layout.addWidget(self.check_dates)
        opts_layout.addWidget(self.check_av)
        opts_layout.addWidget(self.check_dry)
        group_opts.setLayout(opts_layout)
        config_layout.addWidget(group_opts)
        
        tab_config.setLayout(config_layout)
        self.tabs.addTab(tab_config, "Configurações")

        # Tab Log
        tab_log = QWidget()
        log_layout = QVBoxLayout()
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        log_layout.addWidget(self.console)
        tab_log.setLayout(log_layout)
        self.tabs.addTab(tab_log, "Console")

        main_layout.addWidget(self.tabs)

        # Status e Progresso
        self.prog_bar = QProgressBar()
        main_layout.addWidget(self.prog_bar)
        self.label_status = QLabel("Pronto")
        self.label_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.label_status)

        # Botões
        btn_layout = QHBoxLayout()
        self.btn_start = QPushButton("🚀 INICIAR")
        self.btn_start.setFixedHeight(50)
        self.btn_start.clicked.connect(self.iniciar)
        self.btn_stop = QPushButton("🛑 PARAR")
        self.btn_stop.setObjectName("btn_stop")
        self.btn_stop.setFixedHeight(50)
        self.btn_stop.setEnabled(False)
        self.btn_stop.clicked.connect(self.parar)
        
        btn_layout.addWidget(self.btn_start)
        btn_layout.addWidget(self.btn_stop)
        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)

    def selecionar_pasta(self):
        p = QFileDialog.getExistingDirectory(self, "Selecionar Pasta")
        if p:
            self.destino_selecionado = p
            self.edit_dest.setText(p)

    def load_profiles(self):
        os.makedirs("gai_pro/config", exist_ok=True)
        if not os.path.exists(self.profiles_path):
            with open(self.profiles_path, 'w') as f:
                json.dump({}, f)
        
        with open(self.profiles_path, 'r') as f:
            profiles = json.load(f)
            self.combo_profiles.clear()
            self.combo_profiles.addItems(profiles.keys())

    def save_current_profile(self):
        name, ok = QFileDialog.getSaveFileName(self, "Salvar Perfil", "", "JSON (*.json)") # Just use a simple dialog
        # Simplificando para demonstração:
        from PyQt6.QtWidgets import QInputDialog
        name, ok = QInputDialog.getText(self, "Salvar Perfil", "Nome do perfil:")
        if ok and name:
            with open(self.profiles_path, 'r') as f:
                profiles = json.load(f)
            
            profiles[name] = self.get_config()
            with open(self.profiles_path, 'w') as f:
                json.dump(profiles, f, indent=4)
            self.load_profiles()
            self.combo_profiles.setCurrentText(name)

    def load_selected_profile(self):
        name = self.combo_profiles.currentText()
        if not name: return
        with open(self.profiles_path, 'r') as f:
            profiles = json.load(f)
            config = profiles.get(name)
            if config:
                self.set_config(config)

    def delete_profile(self):
        name = self.combo_profiles.currentText()
        if not name: return
        with open(self.profiles_path, 'r') as f:
            profiles = json.load(f)
        if name in profiles:
            del profiles[name]
            with open(self.profiles_path, 'w') as f:
                json.dump(profiles, f, indent=4)
            self.load_profiles()

    def get_config(self):
        exts = [e.strip() for e in self.edit_exts.text().split(',') if e.strip()]
        return {
            'destino': self.destino_selecionado,
            'total_pastas': self.spin_pastas.value(),
            'arquivos_por_pasta': self.spin_arquivos.value(),
            'padrao_nome': self.combo_nomes.currentText(),
            'extensoes_custom': exts,
            'usar_subpastas': self.check_sub.isChecked(),
            'distribuir': self.check_dist.isChecked(),
            'limite_1kb': self.check_1kb.isChecked(),
            'random_dates': self.check_dates.isChecked(),
            'av_test': self.check_av.isChecked(),
            'dry_run': self.check_dry.isChecked(),
            'limite_bytes': self._parse_limit_text(self.combo_limit.currentText())
        }

    def set_config(self, c):
        self.destino_selecionado = c.get('destino', '')
        self.edit_dest.setText(self.destino_selecionado)
        self.spin_pastas.setValue(c.get('total_pastas', 10))
        self.spin_arquivos.setValue(c.get('arquivos_por_pasta', 100))
        self.combo_nomes.setCurrentText(c.get('padrao_nome', 'Aleatório'))
        self.edit_exts.setText(", ".join(c.get('extensoes_custom', [])))
        self.check_sub.setChecked(c.get('usar_subpastas', False))
        self.check_dist.setChecked(c.get('distribuir', False))
        self.check_1kb.setChecked(c.get('limite_1kb', True))
        self.check_dates.setChecked(c.get('random_dates', False))
        self.check_av.setChecked(c.get('av_test', False))
        self.check_dry.setChecked(c.get('dry_run', False))
        # Set limite de tamanho
        limite_bytes_val = c.get('limite_bytes')
        if limite_bytes_val is not None:
            # Encontrar a string correspondente no combo_limit
            for i in range(self.combo_limit.count()):
                item_text = self.combo_limit.itemText(i)
                if self._parse_limit_text(item_text) == limite_bytes_val:
                    self.combo_limit.setCurrentIndex(i)
                    break
        else:
            self.combo_limit.setCurrentText('Sem limite')


    def iniciar(self):
        config = self.get_config()
        if not config['destino'] and not config['dry_run']:
            if not config["dry_run"]:
                QMessageBox.warning(self, "Erro", "Selecione o destino!")
                return

        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.console.clear()
        self.tabs.setCurrentIndex(1)
        self.prog_bar.setValue(0)
        
        self.thread = GeneratorThread(config)
        self.thread.progresso.connect(lambda m: self.console.append(m))
        self.thread.status_barra.connect(self.atualizar_status)
        self.thread.finalizado.connect(self.finalizar)
        self.thread.start()

    def atualizar_status(self, p, t):
        self.prog_bar.setValue(p)
        self.label_status.setText(t)

    def parar(self):
        if self.thread:
            self.thread.stop()
            self.btn_stop.setEnabled(False)
            self.label_status.setText("Parando... aguarde o ciclo atual.")

    def finalizar(self, r):
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        msg = f"<b>Geração {r['status']}!</b><br><br>"
        if r['dry_run']: msg += "<i>(Modo Simulação)</i><br>"
        msg += f"Pastas: {r['pastas']}<br>Arquivos: {r['arquivos']}<br>Tamanho: {r['tamanho_mb']:.2f} MB<br>Tempo: {r['tempo']:.2f}s"
        QMessageBox.information(self, "Fim", msg)
        self.label_status.setText("Pronto")

    def _parse_limit_text(self, limit_text):
        if limit_text == "Sem limite":
            return None
        valor, unidade = limit_text.split()
        fator = {"MB": 1024**2, "GB": 1024**3}
        return int(valor) * fator[unidade]
