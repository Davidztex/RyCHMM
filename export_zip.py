import os
import zipfile

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ZIP_OUTPUT_NAME = "HMM_ProyectoFinal_Unillanos.zip"
ZIP_OUTPUT_PATH = os.path.join(BASE_DIR, ZIP_OUTPUT_NAME)
DOWNLOADS_ZIP_PATH = os.path.join(r"C:\Users\David\Downloads", ZIP_OUTPUT_NAME)

EXCLUDED_DIRS = {"__pycache__", ".git", ".idea", ".vscode"}
EXCLUDED_EXTS = {".pyc", ".pyo", ".zip"}

def create_project_zip(target_path):
    print(f"Empaquetando proyecto en: {target_path}")
    count = 0
    with zipfile.ZipFile(target_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(BASE_DIR):
            # Filtrar carpetas excluidas en su lugar
            dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
            
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in EXCLUDED_EXTS:
                    continue
                file_path = os.path.join(root, file)
                # Relativo al directorio base con prefijo de carpeta
                rel_path = os.path.relpath(file_path, BASE_DIR)
                archive_name = os.path.join("HMM_ProyectoFinal_Unillanos", rel_path)
                zipf.write(file_path, archive_name)
                count += 1
    
    size_mb = os.path.getsize(target_path) / (1024 * 1024)
    print(f"[OK] Archivo generado con exito ({count} archivos, {size_mb:.2f} MB): {target_path}")

if __name__ == "__main__":
    create_project_zip(ZIP_OUTPUT_PATH)
    try:
        create_project_zip(DOWNLOADS_ZIP_PATH)
    except Exception as e:
        print(f"Nota: No se pudo copiar a Downloads: {e}")
