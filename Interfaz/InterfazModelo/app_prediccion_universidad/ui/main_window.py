from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QTabWidget
)

from ui.tab_eda import TabEDA
from ui.tab_modelo import TabModelo
from ui.tab_perfil_est import TabPerfilEst
from ui.tab_evaluar_ests import TabEvaluarEsts


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Sistema de Predicción Universitaria")
        self.setGeometry(100, 100, 1200, 750)

        self.tabs = QTabWidget()
      
        self.tabs.setStyleSheet("""
            QWidget {
                font-family: "Segoe UI";
                font-size: 13px;
                background-color: #FFFFFF;
            }

            QLabel {
                color: #0B4F95;
            }

            QPushButton {
                background-color: #0B4F95;
                color: white;
                border-radius: 8px;
                padding: 8px 14px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #4A90E2;
            }

            QTabWidget::pane {
                border: none;
            }

            QTabBar::tab {
                background: #F4F6F8;
                color: #0B4F95;
                padding: 10px 22px;
                margin-right: 3px;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                font-weight: bold;
            }

            QTabBar::tab:selected {
                background: #0B4F95;
                color: white;
            }

            QTabBar::tab:hover {
                background: #4A90E2;
                color: white;
            }
        """)

      
        self.tab_eda = TabEDA()
        self.tab_modelo = TabModelo()
        self.tab_perfil = TabPerfilEst()
        self.tab_evaluar = TabEvaluarEsts()
        
        # Agregar pestañas 
        
        self.tabs.addTab(self.tab_eda, "EDA")
        self.tabs.addTab(self.tab_modelo, "Modelo Predictivo")
        self.tabs.addTab(self.tab_perfil, "Perfil Estadístico")
        self.tabs.addTab(self.tab_evaluar, "Evaluación Masiva")
       
        # Comunicación entre pestañas
        
        self.tab_modelo.tab_perfil = self.tab_perfil
        self.tab_modelo.tab_widget = self.tabs
        
        # Layout central
        
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.addWidget(self.tabs)

        self.setCentralWidget(container)


