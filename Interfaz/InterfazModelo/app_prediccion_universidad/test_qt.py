from PyQt6.QtWidgets import QApplication, QLabel
import sys

app = QApplication(sys.argv)
label = QLabel("PyQt funciona correctamente")
label.show()
sys.exit(app.exec())
