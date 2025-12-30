import os
import joblib
import pickle
import pandas as pd

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QComboBox, QMessageBox, QFormLayout,
    QHBoxLayout, QFrame
)

# ===============================
# Etiquetas amigables
# ===============================
ETIQUETAS_COLUMNAS = {
    "PERIODO": "Período de la gestión académica",
    "SEXO": "Género del postulante",
    "OPC_INGRESO": "Opción de ingreso",
    "CIUDAD_COLEGIO": "Ciudad del colegio",
    "PROVINCIA_COLEGIO": "Provincia del colegio",
    "ANIO_BACHILLERATO": "Año de egreso de bachillerato",
    "MUNICIPIO": "Municipio de residencia",
    "NACIONALIDAD": "Nacionalidad",
    "ESTADO_CIVIL": "Estado civil",
    "EDAD": "Edad del postulante en el examen",
    "ANIOS_POST_BACH": "Años posteriores al bachillerato",
    "TRABAJO_COLEGIO": "Tipo de colegio",
    "MAYOR_EDAD": "Mayor de edad",
    "MIGRA_UNIVERSIDAD": "Migración universitaria previa",
}
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


class TabModelo(QWidget):
    def __init__(self):
        super().__init__()

        # Layout centrado
        self.main_layout = QHBoxLayout()
        self.card = QFrame()
        self.card.setObjectName("card")

        self.layout = QVBoxLayout(self.card)
        self.form = QFormLayout()

        self.layout.addLayout(self.form)
        self.main_layout.addStretch()
        self.main_layout.addWidget(self.card)
        self.main_layout.addStretch()

        self.cargar_artifactos()

        self.inputs = {}
        self.crear_inputs()

        # Info tasa colegio
        self.label_tasa_info = QLabel("Tasa de aprobación del colegio: ---")
        self.layout.addWidget(self.label_tasa_info)

        # Botón
        self.btn_predecir = QPushButton("Predecir Resultado")
        self.btn_predecir.clicked.connect(self.predecir)
        self.layout.addWidget(self.btn_predecir)

        # Resultado
        self.label_resultado = QLabel("Resultado: ---")
        self.layout.addWidget(self.label_resultado)

        self.setLayout(self.main_layout)
        self.aplicar_estilos()

    
    # Cargar modelo y datos
    
    def cargar_artifactos(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_path = os.path.join(base_dir, "data", "dataset_eda.csv")
        self.df_ref = pd.read_csv(data_path)

        self.tasa_por_colegio = (
            self.df_ref
            .groupby("NOMBRE_COLEGIO")["RESULTADO_FINAL"]
            .apply(lambda x: (x == "APR").mean())
            .to_dict()
        )

        self.modelo = joblib.load("model/modelo_XGBOOST.joblib")

        with open("model/columnas_modelo.pkl", "rb") as f:
            self.columnas_modelo = pickle.load(f)

        with open("model/cat_features.pkl", "rb") as f:
            self.cat_features = pickle.load(f)

        self.tasa_actual = 0.0

    
    # Crear inputs
    
    def crear_inputs(self):
        
        combo_colegio = QComboBox()
        colegios = sorted(
            self.df_ref["NOMBRE_COLEGIO"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )
        combo_colegio.addItems(colegios)
        combo_colegio.setCurrentIndex(-1)
        combo_colegio.currentTextChanged.connect(self.actualizar_tasa_colegio)

        self.form.addRow(QLabel("Nombre del colegio"), combo_colegio)
        self.combo_colegio = combo_colegio  # no va al modelo

        # Variables reales del modelo
        for col in self.columnas_modelo:
            # VARIABLES QUE NO SE MUESTRAN
            if col in ["RESULTADO_FINAL", "AREA_CARRERA"]:
                continue

            
        # VARIABLES QUE NO SE MUESTRAN
            if col in ["RESULTADO_FINAL", "AREA_CARRERA"]:
                continue

            if col == "TASA_APR_COLEGIO":
                continue  

            label = ETIQUETAS_COLUMNAS.get(col, col)

            if col == "ANIO_BACHILLERATO":
                combo = QComboBox()
                combo.addItems([str(a) for a in range(1995, 2011)])
                combo.setCurrentIndex(-1)
            
            elif col == "EDAD":
                combo = QComboBox()
                combo.addItems([str(e) for e in range(15, 43)])
                combo.setCurrentIndex(-1)

            elif col == "ANIOS_POST_BACH":
                combo = QComboBox()
                combo.addItems(["0", "1", "2", "3", "4", "5"])
                combo.setCurrentIndex(-1)

            elif col == "MAYOR_EDAD":
                combo = QComboBox()
                combo.addItem("No", 0)
                combo.addItem("Sí", 1)
                combo.setCurrentIndex(-1)

            elif col == "MIGRA_UNIVERSIDAD":
                combo = QComboBox()
                combo.addItem("No", 0)
                combo.addItem("Sí", 1)
                combo.setCurrentIndex(-1)

            else:
                combo = QComboBox()
                valores = (
                    self.df_ref[col]
                    .dropna()
                    .astype(str)
                    .sort_values()
                    .unique()
                    .tolist()
                )
                combo.addItems(valores)
                combo.setCurrentIndex(-1)

            self.form.addRow(QLabel(label), combo)
            self.inputs[col] = combo

    
    # Actualizar tasa
    
    def actualizar_tasa_colegio(self, nombre):
        tasa = self.tasa_por_colegio.get(nombre)
        if tasa is not None:
            self.tasa_actual = float(tasa)
            self.label_tasa_info.setText(
                f"Tasa de aprobación del colegio: {self.tasa_actual:.2%}"
            )
        else:
            self.tasa_actual = 0.0
            self.label_tasa_info.setText(
                "Tasa de aprobación del colegio: No disponible"
            )

   
    # Predicción
   
    def predecir(self):
        try:
            datos = {}

            for col, widget in self.inputs.items():
                if widget.currentIndex() == -1:
                    raise ValueError(f"Seleccione un valor para {col}")

                
                if col in ["MAYOR_EDAD", "MIGRA_UNIVERSIDAD"]:
                    datos[col] = int(widget.currentData())

                elif col in NUMERICAS_MODELO:
                    datos[col] = float(widget.currentText())

                else:
                    datos[col] = widget.currentText()

            
            datos["TASA_APR_COLEGIO"] = float(self.tasa_actual)

            # Construir DataFrame
            df = pd.DataFrame([datos])
            df = df.reindex(columns=self.columnas_modelo, fill_value=0)

            
            pred = self.modelo.predict(df)[0]
            proba = self.modelo.predict_proba(df)[0][1]

            self.mostrar_resultado(pred, proba)

            
            if hasattr(self, "tab_perfil") and hasattr(self, "tabs_widget"):
                self.tab_perfil.actualizar_perfil(datos, proba)

                
                self.tabs_widget.setCurrentIndex(
                    self.tabs_widget.indexOf(self.tab_perfil)
                )

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    
    # Mostrar resultado
    
    def mostrar_resultado(self, pred, proba):
        if pred == 1:
            texto = "APROBADO ✅"
            color = "#1E7E34"
        else:
            texto = "NO APROBADO ❌"
            color = "#B02A37"

        texto += f"  (Probabilidad: {proba:.2%})"

        self.label_resultado.setText(texto)
        self.label_resultado.setStyleSheet(
            f"""
            background-color: #f4f6f8;
            color: {color};
            font-size: 16px;
            font-weight: bold;
            padding: 12px;
            border-radius: 8px;
            """
        )

    
    # Estilos
    def aplicar_estilos(self):
        self.setStyleSheet("""
            QFrame#card {
                border: 2px solid #0B4F95;
                border-radius: 14px;
                padding: 24px;
                min-width: 520px;
            }
            QLabel {
                color: #0B4F95;
                font-weight: 600;
            }
            QComboBox {
                padding: 6px;
                border-radius: 6px;
                border: 1px solid #0B4F95;
            }
            QPushButton {
                background-color: #0B4F95;
                color: white;
                padding: 10px;
                border-radius: 8px;
                font-weight: bold;
            }
        """)
    def set_tab_perfil(self, tab_perfil, tab_widget):
        self.tab_perfil = tab_perfil
        self.tab_widget = tab_widget
