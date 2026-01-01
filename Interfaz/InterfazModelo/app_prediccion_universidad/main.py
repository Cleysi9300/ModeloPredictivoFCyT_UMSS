import sys
import os
import ctypes

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from ui.main_window import MainWindow


def main():
    # ===============================
    # Identidad de la aplicación (Windows)
    # ===============================
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
        "umss.prediccion.universitaria.v1"
    )

    app = QApplication(sys.argv)

    # ===============================
    # Nombre institucional
    # ===============================
    app.setApplicationName("Sistema de Predicción Universitaria")
    app.setOrganizationName("Universidad Mayor de San Simón")

    # ===============================
    # Icono institucional
    # ===============================
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    ICON_PATH = os.path.join(BASE_DIR, "assets", "logo_umss_1.png")
    app.setWindowIcon(QIcon(ICON_PATH))

    # ===============================
    # Ventana principal
    # ===============================
    ventana = MainWindow()
    ventana.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
