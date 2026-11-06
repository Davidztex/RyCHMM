"""
main.py
=======
Punto de entrada principal para el Reconocedor y Clasificador de Caracteres HMM 2D/3D.
Universidad de los Llanos - Procesos Estocásticos (603504) - 5.° Semestre.

Uso:
    python main.py
"""

import os
import sys

# Asegurar que el directorio raíz del proyecto esté en el path de Python
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMessageBox

from engine.hmm_engine import MultiCharacterClassifier, SPANISH_ALPHABET
from gui.main_window import MainWindow


def main():
    # Configuración de escalado para pantallas de alta densidad (HiDPI)
    if hasattr(Qt.ApplicationAttribute, "AA_EnableHighDpiScaling"):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    if hasattr(Qt.ApplicationAttribute, "AA_UseHighDpiPixmaps"):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName("HMM Character Recognizer 2D/3D")
    app.setOrganizationName("Universidad de los Llanos")

    models_dir = os.path.join(BASE_DIR, "data", "models")
    icons_dir = os.path.join(BASE_DIR, "data", "icons")

    # Inicializar clasificador multiclase y cargar modelos pre-entrenados offline
    classifier = MultiCharacterClassifier(SPANISH_ALPHABET)
    loaded_count = classifier.load_models_from_dir(models_dir)

    if loaded_count < 27:
        print(f"[Aviso] Se cargaron {loaded_count}/27 modelos pre-entrenados. Ejecutando entrenamiento automático...")
        from training.train_models import train_all_models
        classifier = train_all_models(output_dir=models_dir)
        loaded_count = len(classifier.models)

    print(f"[Sistema] {loaded_count} modelos HMM cargados exitosamente.")
    print("[Sistema] Iniciando interfaz gráfica de usuario en PyQt6...")

    window = MainWindow(classifier, icons_dir=icons_dir)
    window.showMaximized()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
