import os
import pandas as pd
import numpy as np

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame, QHBoxLayout
)
from PyQt6.QtCore import Qt


class TabPerfilEst(QWidget):
    def __init__(self):
        super().__init__()

        # ===============================
        # Cargar dataset histórico
        # ===============================
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_path = os.path.join(base_dir, "data", "dataset_eda.csv")
        self.df = pd.read_csv(data_path)

        # Normalizar RESULTADO_FINAL
        self.df["RESULTADO_FINAL"] = self.df["RESULTADO_FINAL"].astype(str)

        # ===============================
        # Precalcular tasa histórica por colegio
        # ===============================
        self.tasa_por_colegio = (
            self.df
            .groupby("NOMBRE_COLEGIO")["RESULTADO_FINAL"]
            .apply(lambda x: (x == "APR").mean())
        )

        # ===============================
        # Datos del postulante
        # ===============================
        self.datos_postulante = None
        self.probabilidad = None

        # ===============================
        # Layout principal
        # ===============================
        layout = QVBoxLayout(self)

        titulo = QLabel("Perfil Estadístico del Postulante")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setStyleSheet("font-size:20px; font-weight:bold;")
        layout.addWidget(titulo)

        self.card = QFrame()
        self.card.setObjectName("card")
        self.card_layout = QVBoxLayout(self.card)

        layout.addWidget(self.card)
        layout.addStretch()

        self.setLayout(layout)
        self.aplicar_estilos()

    # ==================================================
    # Recibir datos desde TabModelo
    # ==================================================
    def actualizar_perfil(self, datos_postulante, probabilidad):
        self.datos_postulante = datos_postulante
        self.probabilidad = probabilidad
        self._calcular_estadisticas()

    # ==================================================
    # Cálculos estadísticos
    # ==================================================
    def _calcular_estadisticas(self):
        self._limpiar_card()

        nombre_colegio = self.datos_postulante.get("NOMBRE_COLEGIO")
        tasa_post = self.datos_postulante.get("TASA_APR_COLEGIO", 0.0)

        # ---------- Percentil real ----------
        tasas_validas = self.tasa_por_colegio.dropna()

        percentil = (
            (tasas_validas <= tasa_post).mean() * 100
            if not tasas_validas.empty
            else 0
        )

        promedio_tasa = tasas_validas.mean()

        # ---------- Años post bach ----------
        anios_post = self.datos_postulante.get("ANIOS_POST_BACH", 0)
        promedio_anios = self.df["ANIOS_POST_BACH"].mean()

        # ---------- Nivel de riesgo ----------
        if self.probabilidad < 0.30:
            riesgo = "ALTO 🔴"
        elif self.probabilidad < 0.60:
            riesgo = "MEDIO 🟠"
        else:
            riesgo = "BAJO 🟢"

        
        # Mostrar resultados
       
       
        self._add_item(
            "Percentil de tasa histórica del colegio",
            f"{percentil:.1f} %"
        )

        self._add_item(
            "Comparación de tasa de aprobación",
            f"Postulante: {tasa_post:.2%} | Promedio histórico: {promedio_tasa:.2%}"
        )

        self._add_item(
            "Comparación de años post bachillerato",
            f"Postulante: {anios_post} | Promedio histórico: {promedio_anios:.2f}"
        )

        self._add_item(
            "Nivel de riesgo estimado para rendir el examen",
            riesgo
        )

    
    # Utilidades UI
    def _add_item(self, titulo, valor):
        cont = QFrame()
        cont.setObjectName("item")

        ly = QHBoxLayout(cont)
        lbl_t = QLabel(titulo)
        lbl_v = QLabel(valor)

        lbl_t.setMinimumWidth(320)
        lbl_v.setStyleSheet("font-weight:bold;")

        ly.addWidget(lbl_t)
        ly.addWidget(lbl_v)

        self.card_layout.addWidget(cont)

    def _limpiar_card(self):
        while self.card_layout.count():
            item = self.card_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    # ==================================================
    # Estilos
    # ==================================================
    def aplicar_estilos(self):
        self.setStyleSheet("""
            QFrame#card {
                background-color: #ffffff;
                border-radius: 14px;
                padding: 20px;
                border: 2px solid #0B4F95;
            }

            QFrame#item {
                padding: 10px;
                border-bottom: 1px solid #e0e0e0;
            }

            QLabel {
                font-size: 14px;
                color: #0B4F95;
            }
        """)
