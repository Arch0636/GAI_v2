def get_dark_theme_stylesheet():
    return """
        QWidget {
            background-color: #2b2b2b;
            color: #e0e0e0;
            font-family: 'Segoe UI', Arial;
            font-size: 13px;
        }
        QGroupBox {
            border: 2px solid #3d3d3d;
            border-radius: 8px;
            margin-top: 10px;
            padding-top: 10px;
            font-weight: bold;
            color: #f0f0f0;
        }
        QPushButton {
            background-color: #0d6efd;
            border: none;
            border-radius: 4px;
            padding: 8px;
            color: white;
            font-weight: bold;
        }
        QPushButton:hover { background-color: #0b5ed7; }
        QPushButton:disabled { background-color: #4d4d4d; color: #a0a0a0; }
        QPushButton#btn_stop { background-color: #dc3545; }
        QPushButton#btn_stop:hover { background-color: #bb2d3b; }
        QPushButton#btn_save { background-color: #198754; }
        QPushButton#btn_save:hover { background-color: #157347; }
        
        QLineEdit, QComboBox, QSpinBox {
            background-color: #3d3d3d;
            border: 1px solid #555;
            border-radius: 4px;
            padding: 5px;
            color: white;
        }
        QTextEdit {
            background-color: #1e1e1e;
            border: 1px solid #3d3d3d;
            border-radius: 4px;
            font-family: 'Consolas', monospace;
            padding: 5px;
        }
        QProgressBar {
            border: 1px solid #3d3d3d;
            border-radius: 4px;
            text-align: center;
            color: white;
            background-color: #3d3d3d;
        }
        QProgressBar::chunk {
            background-color: #198754;
            border-radius: 4px;
        }
        QTabWidget::pane { border: 1px solid #3d3d3d; border-radius: 8px; }
        QTabBar::tab {
            background: #3d3d3d;
            padding: 10px;
            margin-right: 2px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            color: #e0e0e0;
        }
        QTabBar::tab:selected { background: #0d6efd; color: white; }
        QLabel#title { font-size: 24px; font-weight: bold; color: #0d6efd; margin-bottom: 10px; }
        QLabel#subtitle { font-size: 16px; color: #a0a0a0; }
        QCheckBox { spacing: 5px; }
        QCheckBox::indicator { width: 16px; height: 16px; }
        QCheckBox::indicator:checked { background-color: #0d6efd; border: 1px solid #0d6efd; }
        QCheckBox::indicator:unchecked { background-color: #3d3d3d; border: 1px solid #555; }
    """
