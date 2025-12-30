import os
import pandas as pd

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QGroupBox,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QScrollArea, QDialog, QPushButton, QHBoxLayout,
    QFileDialog
)
from PyQt6.QtCore import Qt

from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors


class TabEDA(QWidget):
    def __init__(self):
        super().__init__()

        # ===============================
        # Cargar dataset
        # ===============================
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_path = os.path.join(base_dir, "data", "dataset_eda.csv")
        self.df = pd.read_csv(data_path)

        # ===============================
        # Scroll principal
        # ===============================
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        container = QWidget()
        main_layout = QVBoxLayout(container)

        # ===============================
        # Título
        # ===============================
        titulo = QLabel("Descripción General del Dataset")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setStyleSheet("font-size:20px; font-weight:bold;")
        main_layout.addWidget(titulo)

        # ===============================
        # Botón dataset completo
        # ===============================
        btn_ver_dataset = QPushButton("Ver dataset completo")
        btn_ver_dataset.setFixedWidth(260)
        btn_ver_dataset.setStyleSheet("""
            QPushButton {
                padding: 8px;
                font-weight: bold;
                background-color: #4a90e2;
                color: white;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #357abd;
            }
        """)
        btn_ver_dataset.clicked.connect(self._mostrar_dataset_completo)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(btn_ver_dataset)
        btn_layout.addStretch()
        main_layout.addLayout(btn_layout)

        # ===============================
        # Secciones EDA
        # ===============================
        main_layout.addWidget(
            self._seccion_tabla(
                "Columnas existentes en el dataset",
                pd.DataFrame({"Columnas": self.df.columns})
            )
        )

        main_layout.addWidget(
            self._seccion_tabla(
                "Tipo de datos de las variables",
                self.df.dtypes.reset_index().rename(
                    columns={"index": "Variable", 0: "Tipo"}
                )
            )
        )

        main_layout.addWidget(
            self._seccion_tabla(
                "Cantidad de datos por columna",
                self.df.count().reset_index().rename(
                    columns={"index": "Variable", 0: "Cantidad"}
                )
            )
        )

        main_layout.addWidget(
            self._seccion_tabla(
                "Descripción general de los datos",
                self.df.describe(include="all").reset_index()
            )
        )

        nulos = self.df.isnull().sum().reset_index()
        nulos.columns = ["Variable", "Valores Nulos"]
        main_layout.addWidget(
            self._seccion_tabla(
                "Cantidad de valores nulos por columna",
                nulos
            )
        )

        porcentaje = (self.df.isnull().sum() / len(self.df) * 100).round(2)
        porcentaje = porcentaje.reset_index()
        porcentaje.columns = ["Variable", "Porcentaje Nulos (%)"]
        main_layout.addWidget(
            self._seccion_tabla(
                "Porcentaje de valores nulos por columna",
                porcentaje
            )
        )

        
        scroll.setWidget(container)

        layout_final = QVBoxLayout(self)
        layout_final.addWidget(scroll)

    # ==================================================
    # Crear sección desplegable con tabla + botones
    # ==================================================
    def _seccion_tabla(self, titulo, dataframe):
        group = QGroupBox(titulo)
        group.setCheckable(True)
        group.setChecked(False)

        layout = QVBoxLayout()

        tabla = QTableWidget()
        tabla.setRowCount(len(dataframe))
        tabla.setColumnCount(len(dataframe.columns))
        tabla.setHorizontalHeaderLabels(dataframe.columns.astype(str))

        for i in range(len(dataframe)):
            for j, col in enumerate(dataframe.columns):
                tabla.setItem(i, j, QTableWidgetItem(str(dataframe.iloc[i, j])))

        tabla.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        tabla.setMinimumHeight(300)

        # Botones
        btn_expandir = QPushButton("Expandir")
        btn_descargar = QPushButton("Descargar PDF")

        botones = QHBoxLayout()
        botones.addStretch()
        botones.addWidget(btn_expandir)
        botones.addWidget(btn_descargar)

        layout.addLayout(botones)
        layout.addWidget(tabla)
        group.setLayout(layout)

        btn_expandir.clicked.connect(
            lambda: self._mostrar_pantalla_completa(titulo, dataframe)
        )
        btn_descargar.clicked.connect(
            lambda: self._descargar_pdf(titulo, dataframe)
        )

        return group

    # ==================================================
    # Pantalla completa
    # ==================================================
    def _mostrar_pantalla_completa(self, titulo, dataframe):
        dialog = QDialog(self)
        dialog.setWindowTitle(titulo)
        dialog.resize(1800, 600)

        layout = QVBoxLayout(dialog)

        tabla = QTableWidget()
        tabla.setRowCount(len(dataframe))
        tabla.setColumnCount(len(dataframe.columns))
        tabla.setHorizontalHeaderLabels(dataframe.columns.astype(str))

        for i in range(len(dataframe)):
            for j, col in enumerate(dataframe.columns):
                tabla.setItem(i, j, QTableWidgetItem(str(dataframe.iloc[i, j])))

        tabla.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        btn_descargar = QPushButton("Descargar PDF")
        btn_cerrar = QPushButton("Cerrar")

        botones = QHBoxLayout()
        botones.addStretch()
        botones.addWidget(btn_descargar)
        botones.addWidget(btn_cerrar)

        layout.addLayout(botones)
        layout.addWidget(tabla)

        btn_cerrar.clicked.connect(dialog.close)
        btn_descargar.clicked.connect(
            lambda: self._descargar_pdf(titulo, dataframe)
        )

        dialog.exec()

    # ==================================================
    # Descargar PDF
    # ==================================================
    def _descargar_pdf(self, titulo, dataframe):
        archivo, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar PDF",
            f"{titulo}.pdf",
            "PDF (*.pdf)"
        )

        if not archivo:
            return

        doc = SimpleDocTemplate(
            archivo,
            pagesize=landscape(A4),
            rightMargin=20,
            leftMargin=20,
            topMargin=20,
            bottomMargin=20
        )

        data = [dataframe.columns.tolist()] + dataframe.values.tolist()

        tabla = Table(data, repeatRows=1)
        tabla.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#4a90e2")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))

        doc.build([tabla])

    # ==================================================
    # Dataset completo
    # ==================================================
    def _mostrar_dataset_completo(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Dataset completo")
        dialog.resize(1200, 650)

        layout = QVBoxLayout(dialog)

        tabla = QTableWidget()
        tabla.setRowCount(len(self.df))
        tabla.setColumnCount(len(self.df.columns))
        tabla.setHorizontalHeaderLabels(self.df.columns.astype(str))

        for i in range(len(self.df)):
            for j, col in enumerate(self.df.columns):
                tabla.setItem(i, j, QTableWidgetItem(str(self.df.iloc[i, j])))

        tabla.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )

        layout.addWidget(tabla)
        dialog.exec()
