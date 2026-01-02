import os
import joblib
import pandas as pd
import numpy as np

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFileDialog, QMessageBox, QTableWidget,
    QTableWidgetItem, QFrame, QDialog, QFormLayout
)

from PyQt6.QtCore import Qt
from ui.worker_evaluacion import WorkerEvaluacion



# ==========================================
# Etiquetas académicas
# ==========================================
ETIQUETAS = {
    "PERIODO": "Período académico",
    "SEXO": "Género",
    "OPC_INGRESO": "Opción de ingreso",
    "CIUDAD_COLEGIO": "Ciudad del colegio",
    "PROVINCIA_COLEGIO": "Provincia del colegio",
    "ANIO_BACHILLERATO": "Año de bachillerato",
    "MUNICIPIO": "Municipio",
    "NACIONALIDAD": "Nacionalidad",
    "ESTADO_CIVIL": "Estado civil",
    "EDAD": "Edad en el examen",
    "ANIOS_POST_BACH": "Años post bachillerato",
    "TRABAJO_COLEGIO": "Tipo de colegio",
    "MAYOR_EDAD": "Mayor de edad",
    "MIGRA_UNIVERSIDAD": "Migración universitaria",
    "PREDICCION": "Resultado esperado",
    "PROBABILIDAD": "Probabilidad de aprobar"
}


class TabEvaluarEsts(QWidget):
    def __init__(self):
        super().__init__()

        # Layout principal
      
        self.layout = QVBoxLayout(self)

        titulo = QLabel("Evaluación Masiva de Postulantes")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setStyleSheet("font-size:20px; font-weight:bold;")
        self.layout.addWidget(titulo)
        
        # Card
     
        self.card = QFrame()
        self.card.setObjectName("card")
        card_layout = QVBoxLayout(self.card)

        self.btn_cargar = QPushButton("📂 Cargar archivo Excel (.xlsx)")
        self.btn_cargar.clicked.connect(self.cargar_excel)
        card_layout.addWidget(self.btn_cargar)

        self.tabla = QTableWidget()
        card_layout.addWidget(self.tabla)

        self.layout.addWidget(self.card)
                
        # Cargar modelo y dataset base

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        self.modelo = joblib.load(
            os.path.join(base_dir, "model", "modelo_XGBOOST.joblib")
        )

        with open(os.path.join(base_dir, "model", "columnas_modelo.pkl"), "rb") as f:
            self.columnas_modelo = joblib.load(f)

        self.df_hist = pd.read_csv(
            os.path.join(base_dir, "data", "dataset_eda.csv")
        )

        self.tasa_por_colegio = (
            self.df_hist
            .groupby("NOMBRE_COLEGIO")["RESULTADO_FINAL"]
            .apply(lambda x: (x == "APR").mean())
            .to_dict()
        )
       
        self.df_resultados = None

        self.aplicar_estilos()
    
    # Cargar Excel
    
    def cargar_excel(self):
        ruta, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar archivo Excel", "", "Excel (*.xlsx)"
        )

        if not ruta:
            return

        self.btn_cargar.setEnabled(False)
        self.tabla.setRowCount(0)

        self.worker = WorkerEvaluacion(
            ruta,
            self.modelo,
            self.columnas_modelo,
            self.tasa_por_colegio
        )

        self.worker.terminado.connect(self.mostrar_resultados)
        self.worker.error.connect(self.mostrar_error)
        self.worker.start()

    # Preparar datos

    def preparar_datos(self, df):

        df["FECHA_NAC"] = pd.to_datetime(df["FECHA_NAC"], errors="coerce")

      
        df["EDAD"] = df.apply(
            lambda fila: fila["ANIO"] - fila["FECHA_NAC"].year
            - ((1, 1) < (fila["FECHA_NAC"].month, fila["FECHA_NAC"].day))
            if pd.notnull(fila["FECHA_NAC"]) else np.nan,
            axis=1
        )

        df["EDAD"] = (
            pd.to_numeric(df["EDAD"], errors="coerce")
            .fillna(0)
            .astype(int)
        )

        df["MAYOR_EDAD"] = (df["EDAD"] >= 18).astype(int)

     
        
        df["ANIOS_POST_BACH"] = (
            df["ANIO"] - df["ANIO_BACHILLERATO"]
        )

        df["ANIOS_POST_BACH"] = (
            pd.to_numeric(df["ANIOS_POST_BACH"], errors="coerce")
            .fillna(0)
            .astype(int)
        )
        
        df["TRABAJO_COLEGIO"] = (
            df["TRABAJA"].fillna("NO").astype(str) + "_" +
            df["TIPO_COLEGIO"].fillna("DESCONOCIDO").astype(str)
        )

        df["MIGRA_UNIVERSIDAD"] = (
            (df["CIUDAD_COLEGIO"] != "COCHABAMBA") |
            (df["PROVINCIA_COLEGIO"] != "COCHABAMBA (CERCADO)")
        ).astype(int)

        df["TASA_APR_COLEGIO"] = (
            df["NOMBRE_COLEGIO"]
            .map(self.tasa_por_colegio)
            .fillna(0.0)
        )

        return df
    
    # Predicción
    
    def predecir(self, df):
        X = df.reindex(columns=self.columnas_modelo, fill_value=0)

        pred = self.modelo.predict(X)
        proba = self.modelo.predict_proba(X)[:, 1]

        df["PREDICCION"] = np.where(pred == 1, "FUERA DE RIESGO","EN RIESGO")
        df["PROBABILIDAD"] = proba

        self.df_resultados = df
        self.mostrar_tabla(df)

       # Tabla resumida
    def mostrar_resultados(self, df):
        
        self.btn_cargar.setEnabled(True)
        self.df_resultados = df.reset_index(drop=True)

        columnas = [
            "SEXO", "EDAD", "NOMBRE_COLEGIO",
            "PREDICCION", "PROBABILIDAD", "PERFIL"
        ]

        self.tabla.setRowCount(len(df))
        self.tabla.setColumnCount(len(columnas))
        self.tabla.setHorizontalHeaderLabels(columnas)

        for i, row in self.df_resultados.iterrows():
            for j, col in enumerate(columnas):
                                
                if col == "PERFIL":
                    btn = QPushButton("Ver perfil")
                    btn.setStyleSheet("""
                        QPushButton {
                            background-color: #0B4F95;
                            color: white;
                            border-radius: 8px;
                            padding: 14px 14p
                            
                            font-weight: bold;
                            font-size: 12px;
                        }
                        QPushButton:hover {
                            background-color: #4A90E2;
                        }
                    """)
                    btn.clicked.connect(lambda _, idx=i: self.ver_perfil(idx))
                    self.tabla.setCellWidget(i, j, btn)
                    self.tabla.setRowHeight(i, 44)
                    continue

                # ---------------------------
                # DATOS NORMALES
                # ---------------------------
                valor = row[col]
                if col == "PROBABILIDAD":
                    valor = f"{valor:.2%}"

                item = QTableWidgetItem(str(valor))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

               
                if col == "PREDICCION":
                    if valor == "FUERA DE RIESGO":
                        item.setForeground(Qt.GlobalColor.darkGreen)
                    else:
                        item.setForeground(Qt.GlobalColor.red)


                self.tabla.setItem(i, j, item)

        self.tabla.resizeColumnsToContents()
        
        col_perfil = columnas.index("PERFIL")
        self.tabla.setColumnWidth(col_perfil, 120)
    
    # Perfil individual
    def ver_perfil(self, idx):
        fila = self.df_resultados.iloc[idx]

        dialog = QDialog(self)
        dialog.setWindowTitle("Perfil del Postulante")
        dialog.resize(520, 600)

        layout = QVBoxLayout(dialog)
        layout.setSpacing(16)

        # ===============================
        # ENCABEZADO – RESULTADO
        # ===============================
        prob = fila.get("PROBABILIDAD", 0)
        riesgo = fila.get("PREDICCION", "")

        if riesgo == "FUERA DE RIESGO":
            color = "#1E7E34"
            fondo = "#D4EDDA"
            icono = "✅"
        else:
            color = "#B02A37"
            fondo = "#F8D7DA"
            icono = "⚠️"

        header = QLabel(
            f"{icono} {riesgo}\n"
            f"Probabilidad estimada de aprobación: {prob:.2%}"
        )
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet(f"""
            background-color: {fondo};
            color: {color};
            font-size: 16px;
            font-weight: bold;
            padding: 14px;
            border-radius: 10px;
        """)
        layout.addWidget(header)

        # ===============================
        # FUNCIÓN AUXILIAR PARA SECCIONES
        # ===============================
        def add_section(title):
            lbl = QLabel(title)
            lbl.setStyleSheet("""
                font-size:15px;
                font-weight:bold;
                color:#0B4F95;
                margin-top:10px;
            """)
            layout.addWidget(lbl)

        def add_item(clave, valor):
            row = QHBoxLayout()
            lbl_k = QLabel(clave)
            lbl_v = QLabel(str(valor))

            lbl_k.setMinimumWidth(220)
            lbl_v.setStyleSheet("font-weight:bold;")

            row.addWidget(lbl_k)
            row.addStretch()
            row.addWidget(lbl_v)
            layout.addLayout(row)

        # ===============================
        # DATOS ACADÉMICOS
        # ===============================
        add_section("Datos académicos")

        add_item("Período académico", fila.get("PERIODO"))
        add_item("Opción de ingreso", fila.get("OPC_INGRESO"))
        add_item("Nombre del colegio", fila.get("NOMBRE_COLEGIO"))
        add_item("Ciudad del colegio", fila.get("CIUDAD_COLEGIO"))
        add_item("Provincia del colegio", fila.get("PROVINCIA_COLEGIO"))
        add_item("Año de bachillerato", fila.get("ANIO_BACHILLERATO"))
        add_item("Tipo de colegio", fila.get("TRABAJO_COLEGIO"))

        # ===============================
        # DATOS PERSONALES
        # ===============================
        add_section("Datos personales")

        add_item("Género", fila.get("SEXO"))
        add_item("Edad en el examen", fila.get("EDAD"))
        add_item("Estado civil", fila.get("ESTADO_CIVIL"))
        add_item("Nacionalidad", fila.get("NACIONALIDAD"))
        add_item(
            "Mayor de edad",
            "Sí" if fila.get("MAYOR_EDAD") == 1 else "No"
        )
        add_item(
            "Migración universitaria",
            "Sí" if fila.get("MIGRA_UNIVERSIDAD") == 1 else "No"
        )
        add_item("Años post bachillerato", fila.get("ANIOS_POST_BACH"))

        layout.addStretch()
        dialog.exec()

    def mostrar_error(self, mensaje):
        self.btn_cargar.setEnabled(True)
        QMessageBox.critical(self, "Error", mensaje)
    def aplicar_estilos(self):
        self.setStyleSheet("""
            /* ===============================
            CARD PRINCIPAL
            =============================== */
            QFrame#card {
                background-color: #FFFFFF;
                border-radius: 16px;
                padding: 24px;
                border: 2px solid #0B4F95;
            }

            /* ===============================
            TÍTULOS
            =============================== */
            QLabel {
                font-size: 14px;
                color: #0B4F95;
            }

            /* ===============================
            BOTÓN PRINCIPAL
            =============================== */
            QPushButton {
                background-color: #0B4F95;
                color: white;
                border-radius: 10px;
                padding: 10px 16px;
                font-weight: bold;
                font-size: 14px;
            }

            QPushButton:hover {
                background-color: #4A90E2;
            }

            QPushButton:disabled {
                background-color: #A0A0A0;
                color: #EAEAEA;
            }

            /* ===============================
            TABLA
            =============================== */
            QTableWidget {
                background-color: #FFFFFF;
                border: 1px solid #DADADA;
                gridline-color: #E0E0E0;
                selection-background-color: #E6F0FA;
                selection-color: #000000;
                alternate-background-color: #F7F9FC;
                font-size: 13px;
            }

            QTableWidget::item {
                padding: 6px;
            }

            QTableWidget::item:selected {
                background-color: #E6F0FA;
                color: #000000;
            }

            /* ===============================
            CABECERAS DE TABLA
            =============================== */
            QHeaderView::section {
                background-color: #F0F4F8;
                color: #0B4F95;
                font-weight: bold;
                padding: 8px;
                border: none;
                border-bottom: 2px solid #0B4F95;
            }

            QHeaderView::section:first {
                border-top-left-radius: 8px;
            }

            QHeaderView::section:last {
                border-top-right-radius: 8px;
            }

            /* ===============================
            BOTÓN "VER PERFIL" EN TABLA
            =============================== */
            QTableWidget QPushButton {
                background-color: #0B4F95;
                color: white;
                border-radius: 6px;
                padding: 4px 10px;
                font-size: 12px;
            }

            QTableWidget QPushButton:hover {
                background-color: #4A90E2;
            }
        """)


    