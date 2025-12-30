from PyQt6.QtCore import QThread, pyqtSignal
import pandas as pd
import numpy as np

class WorkerEvaluacion(QThread):
    terminado = pyqtSignal(pd.DataFrame)
    error = pyqtSignal(str)

    def __init__(self, ruta_excel, modelo, columnas_modelo, tasa_por_colegio):
        super().__init__()
        self.ruta_excel = ruta_excel
        self.modelo = modelo
        self.columnas_modelo = columnas_modelo
        self.tasa_por_colegio = tasa_por_colegio

    def run(self):
        try:
            df = pd.read_excel(self.ruta_excel)

            
            # Limpieza y features
            
            df["FECHA_NAC"] = pd.to_datetime(df["FECHA_NAC"], errors="coerce")

            df["EDAD"] = (
                df["ANIO"] - df["FECHA_NAC"].dt.year
            ).fillna(0).astype(int)

            df["MAYOR_EDAD"] = (df["EDAD"] >= 18).astype(int)

            df["ANIOS_POST_BACH"] = (
                df["ANIO"] - df["ANIO_BACHILLERATO"]
            ).where(df["ANIO_BACHILLERATO"] != 0, 0).fillna(0).astype(int)

            df["TRABAJO_COLEGIO"] = (
                df["TRABAJA"].astype(str) + "_" + df["TIPO_COLEGIO"].astype(str)
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

            
            # Predicción
            
            X = df.reindex(columns=self.columnas_modelo, fill_value=0)

            pred = self.modelo.predict(X)
            proba = self.modelo.predict_proba(X)[:, 1]

            df["PREDICCION"] = np.where(pred == 1, "APROBADO", "NO APROBADO")
            df["PROBABILIDAD"] = proba

            self.terminado.emit(df)

        except Exception as e:
            self.error.emit(str(e))
