import os
import pandas as pd

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame,
    QHBoxLayout, QGridLayout, QScrollArea
)
from PyQt6.QtCore import Qt


NUMERICAS_MODELO = {
    "PERIODO",
    "OPC_INGRESO",
    "EDAD",
    "ANIO_BACHILLERATO",
    "ANIOS_POST_BACH",
    "MAYOR_EDAD",
    "MIGRA_UNIVERSIDAD",
    "TASA_APR_COLEGIO",
}


class TabPerfilEst(QWidget):
    def __init__(self):
        super().__init__()

        # ===============================
        # Cargar dataset histórico
        # ===============================
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_path = os.path.join(base_dir, "data", "dataset_eda.csv")
        self.df = pd.read_csv(data_path)

        self.df["RESULTADO_FINAL"] = self.df["RESULTADO_FINAL"].astype(str)

        self.tasa_por_colegio = (
            self.df
            .groupby("NOMBRE_COLEGIO")["RESULTADO_FINAL"]
            .apply(lambda x: (x == "APR").mean())
        )

        self.datos_postulante = None
        self.probabilidad = None

        # ===============================
        # Layout raíz
        # ===============================
        root_layout = QVBoxLayout(self)

        # ===============================
        # Scroll Area
        # ===============================
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        root_layout.addWidget(scroll)

        # ===============================
        # Contenido dentro del scroll
        # ===============================
        content = QWidget()
        scroll.setWidget(content)

        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(16)

        # ===============================
        # Título
        # ===============================
        titulo = QLabel("Perfil Estadístico del Postulante")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setStyleSheet(
            "font-size:22px; font-weight:bold; color:#0B4F95;"
        )
        content_layout.addWidget(titulo)

        subtitulo = QLabel(
            "Análisis comparativo del postulante respecto al comportamiento histórico"
        )
        subtitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitulo.setStyleSheet("color:#555; font-size:13px;")
        content_layout.addWidget(subtitulo)

        # ===============================
        # Card principal
        # ===============================
        self.card = QFrame()
        self.card.setObjectName("card")

        self.card_layout = QVBoxLayout(self.card)
        self.card_layout.setSpacing(14)

        content_layout.addWidget(self.card)
        content_layout.addStretch()

        self.aplicar_estilos()

    # ==================================================
    # Recibir datos desde el modelo
    # ==================================================
    def actualizar_perfil(self, datos_postulante, probabilidad):
        self.datos_postulante = datos_postulante
        self.probabilidad = probabilidad
        self._calcular_estadisticas()

    # ==================================================
    # Construcción del perfil
    # ==================================================
    def _calcular_estadisticas(self):
        self._limpiar_card()

        def entero(valor):
            try:
                return int(valor)
            except (TypeError, ValueError):
                return "-"

        # ===============================
        # Resumen de riesgo
        # ===============================
        if self.probabilidad < 0.50:
            estado = "EN RIESGO"
            color = "#B02A37"
            fondo = "#F8D7DA"
            icono = "⚠️"
        else:
            estado = "FUERA DE RIESGO"
            color = "#1E7E34"
            fondo = "#D4EDDA"
            icono = "✅"

        resumen = QLabel(
            f"{icono} {estado}\n"
            f"Probabilidad estimada de aprobación: {self.probabilidad:.2%}"
        )
        resumen.setAlignment(Qt.AlignmentFlag.AlignCenter)
        resumen.setStyleSheet(f"""
            background-color: {fondo};
            color: {color};
            font-size: 18px;
            font-weight: bold;
            padding: 18px;
            border-radius: 12px;
        """)
        self.card_layout.addWidget(resumen)

        # ===============================
        # Características del postulante (2 columnas)
        # ===============================
        self._add_section("Características del postulante")

        grid = QGridLayout()
        grid.setHorizontalSpacing(40)
        grid.setVerticalSpacing(12)

        items = [
            ("Edad", f"{entero(self.datos_postulante.get('EDAD'))} años"),
            ("Periodo académico", entero(self.datos_postulante.get("PERIODO"))),
            ("Opción de ingreso", entero(self.datos_postulante.get("OPC_INGRESO"))),
            ("Año de egreso de bachillerato", entero(self.datos_postulante.get("ANIO_BACHILLERATO"))),
            ("Años posteriores al bachillerato", entero(self.datos_postulante.get("ANIOS_POST_BACH"))),
            (
                "Mayor de edad",
                "Sí" if self.datos_postulante.get("MAYOR_EDAD") == 1 else "No"
            ),
            (
                "Migración universitaria previa",
                "Sí" if self.datos_postulante.get("MIGRA_UNIVERSIDAD") == 1 else "No"
            ),
        ]

        for i, (k, v) in enumerate(items):
            lbl_k = QLabel(k)
            lbl_v = QLabel(str(v))
            lbl_v.setStyleSheet("font-weight:bold;")

            row = i // 2
            col = (i % 2) * 2

            grid.addWidget(lbl_k, row, col)
            grid.addWidget(lbl_v, row, col + 1)

        self.card_layout.addLayout(grid)
        self.card_layout.addSpacing(10)

        # ===============================
        # Comparación histórica
        # ===============================
        self._add_section("Comparación con el comportamiento histórico")

        for col in NUMERICAS_MODELO:
            valor = self.datos_postulante.get(col)

            if col == "TASA_APR_COLEGIO":
                promedio = self.tasa_por_colegio.mean()
                texto = f"{valor:.2%} (Promedio histórico: {promedio:.2%})"
            else:
                promedio = self.df[col].mean()
                texto = f"{entero(valor)} (Promedio histórico: {entero(promedio)})"

            self._add_kv(self._nombre_legible(col), texto)

    # ==================================================
    # Helpers UI
    # ==================================================
    def _add_section(self, titulo):
        lbl = QLabel(titulo)
        lbl.setStyleSheet("""
            font-size:16px;
            font-weight:bold;
            margin-top:18px;
            margin-bottom:6px;
            color:#0B4F95;
        """)
        self.card_layout.addWidget(lbl)

    def _add_kv(self, clave, valor):
        cont = QFrame()
        cont.setObjectName("item")

        ly = QHBoxLayout(cont)
        lbl_k = QLabel(clave)
        lbl_v = QLabel(str(valor))
        lbl_v.setStyleSheet("font-weight:bold;")

        ly.addWidget(lbl_k)
        ly.addStretch()
        ly.addWidget(lbl_v)

        self.card_layout.addWidget(cont)

    def _limpiar_card(self):
        while self.card_layout.count():
            item = self.card_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _nombre_legible(self, col):
        return {
            "PERIODO": "Periodo académico",
            "OPC_INGRESO": "Opción de ingreso",
            "EDAD": "Edad",
            "ANIO_BACHILLERATO": "Año de egreso de bachillerato",
            "ANIOS_POST_BACH": "Años posteriores al bachillerato",
            "MAYOR_EDAD": "Mayor de edad",
            "MIGRA_UNIVERSIDAD": "Migración universitaria previa",
            "TASA_APR_COLEGIO": "Tasa de aprobación del colegio",
        }.get(col, col)

    # ==================================================
    # Estilos
    # ==================================================
    def aplicar_estilos(self):
        self.setStyleSheet("""
            QFrame#card {
                background-color: #ffffff;
                border-radius: 16px;
                padding: 24px;
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
