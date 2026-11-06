"""
export_zip.py
=============
Empaqueta el proyecto completo en un archivo comprimido (.zip)
para entrega oficial al docente (yerson.porras@unillanos.edu.co)
según la Sección 5.1 de la especificación.
"""

import os
import zipfile

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ZIP_OUTPUT = os.path.join(BASE_DIR, "HMM_ProyectoFinal_Unillanos.zip")

EXCLUDE_DIRS = {"__pycache__", ".git", ".idea", ".vscode", "venv", ".venv"}
EXCLUDE_EXTS = {".pyc", ".pyo", ".zip"}


def create_submission_zip():
    print(f"Empaquetando proyecto en: {ZIP_OUTPUT}")
    file_count = 0

    with zipfile.ZipFile(ZIP_OUTPUT, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(BASE_DIR):
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in EXCLUDE_EXTS:
                    continue
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, BASE_DIR)
                zipf.write(full_path, os.path.join("hmm_recognizer", rel_path))
                file_count += 1

    size_mb = os.path.getsize(ZIP_OUTPUT) / (1024 * 1024)
    print(f"[OK] Paquete ZIP creado exitosamente: {file_count} archivos incluidos ({size_mb:.2f} MB).")
    print("[OK] Listo para enviar a: yerson.porras@unillanos.edu.co")


if __name__ == "__main__":
    create_submission_zip()
