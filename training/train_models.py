"""
train_models.py
===============
Script de entrenamiento offline independiente para el Reconocedor HMM 2D/3D.
Cumple con la sección 4.1 del documento de especificación:
"Los parámetros lambda_c = (A_c, B_c, pi_c) para los 27 caracteres deben ser entrenados
de forma previa mediante scripts independientes (Baum-Welch o máxima verosimilitud).
Los parámetros aprendidos se exportan a archivos estructurados (.json) que la GUI cargará al iniciar."
"""

import json
import os
import shutil
import sys
import time

# Permitir ejecución directa
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from engine.hmm_engine import DiscreteHMM, MultiCharacterClassifier, SPANISH_ALPHABET
from engine.feature_extractor import FeatureExtractor
from training.synthetic_generator import SyntheticGlyphGenerator
from training.generate_icons import generate_all_icons


def find_dataset_file():
    """Busca el archivo de dataset en rutas conocidas."""
    candidates = [
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "dataset", "glifo-dataset-2026-11-05.json")),
        r"c:\Users\David\Downloads\glifo-dataset-2026-11-05.json",
        os.path.abspath("glifo-dataset-2026-11-05.json")
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return None


def copy_dataset_if_needed(source_path, target_dir):
    """Copia el dataset a data/dataset para portabilidad total del proyecto."""
    os.makedirs(target_dir, exist_ok=True)
    target_path = os.path.join(target_dir, "glifo-dataset-2026-11-05.json")
    if not os.path.exists(target_path) and os.path.exists(source_path):
        print(f"Copiando dataset a carpeta local del proyecto: {target_path}")
        shutil.copy2(source_path, target_path)
    return target_path if os.path.exists(target_path) else source_path


def train_all_models(dataset_path=None, output_dir=None, n_states=6, max_iter=12):
    """
    Ejecuta el entrenamiento estocástico Baum-Welch para los 27 caracteres del alfabeto español.
    """
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if output_dir is None:
        output_dir = os.path.join(base_dir, "data", "models")
    os.makedirs(output_dir, exist_ok=True)

    if dataset_path is None:
        dataset_path = find_dataset_file()

    local_ds_dir = os.path.join(base_dir, "data", "dataset")
    if dataset_path and os.path.exists(dataset_path):
        dataset_path = copy_dataset_if_needed(dataset_path, local_ds_dir)

    raw_data = {}
    if dataset_path and os.path.exists(dataset_path):
        print(f"[Dataset] Cargando datos manuscritos desde: {dataset_path}")
        with open(dataset_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
        print(f"[Dataset] Claves encontradas: {len(raw_data)}")
    else:
        print("[Dataset] AVISO: Archivo JSON no encontrado. Se utilizará el generador sintético canónico.")

    classifier = MultiCharacterClassifier(SPANISH_ALPHABET)
    t_start = time.time()

    print(f"\n{'='*70}")
    print(f" INICIANDO ENTRENAMIENTO OFFLINE NATIVO HMM (N={n_states} estados, K=16 sectores)")
    print(f" Topología: Left-to-Right (Bakis) | Algoritmo: Baum-Welch (EM)")
    print(f"{'='*70}")

    for idx, char in enumerate(SPANISH_ALPHABET, start=1):
        t0 = time.time()

        # Obtener muestras del dataset humano
        char_samples = raw_data.get(char, [])
        if not char_samples and char == 'ñ':
            # Intentar buscar por código o representación
            for k in raw_data.keys():
                if ord(k[0]) == 241 or k == 'ñ' or k == '':
                    char_samples = raw_data[k]
                    break

        sequences = []
        best_representative_pts = []
        best_representative_syms = []

        # Extraer secuencias del dataset humano
        for sample in char_samples:
            syms, res_strokes = FeatureExtractor.extract_symbols_from_strokes_2d(sample, step=14.0)
            if len(syms) >= 3:
                sequences.append(syms)
                # Guardar el primer trazo representativo de longitud moderada
                if not best_representative_pts and 8 <= len(syms) <= 35:
                    all_pts = []
                    for st in res_strokes:
                        all_pts.extend(st.tolist())
                    best_representative_pts = all_pts
                    best_representative_syms = syms

        # Complementar con muestras canónicas sintéticas perturbadas
        canon_strokes = SyntheticGlyphGenerator.get_canonical_strokes(char)
        canon_syms, canon_res = FeatureExtractor.extract_symbols_from_strokes_2d(canon_strokes, step=14.0)
        if canon_syms:
            sequences.append(canon_syms)
            # Agregar 10 perturbaciones sintéticas suaves para robustez
            for _ in range(10):
                pert = SyntheticGlyphGenerator.perturb_strokes(canon_strokes, noise_std=1.5)
                p_syms, _ = FeatureExtractor.extract_symbols_from_strokes_2d(pert, step=14.0)
                if len(p_syms) >= 3:
                    sequences.append(p_syms)

        if not best_representative_syms:
            best_representative_syms = canon_syms
            best_representative_pts = [p for st in canon_res for p in st.tolist()]

        # Crear y entrenar modelo HMM
        hmm = DiscreteHMM(n_states=n_states, n_obs=16, char_label=char)
        hmm.canonical_points = best_representative_pts
        hmm.canonical_symbols = best_representative_syms

        hmm.train_baum_welch(sequences, max_iter=max_iter)
        classifier.add_model(hmm)

        dt = time.time() - t0
        print(f" [{idx:02d}/27] Letra '{char}': {len(sequences):3d} secuencias entrenadas en {dt:.2f}s")

    # Guardar todos los modelos exportados
    classifier.save_all_models(output_dir)
    total_time = time.time() - t_start
    print(f"\n{'='*70}")
    print(f" ENTRENAMIENTO COMPLETADO EXITOSAMENTE en {total_time:.2f} segundos")
    print(f" Modelos exportados a: {output_dir}")
    print(f"{'='*70}\n")

    # Generar iconos de referencia
    icons_dir = os.path.join(base_dir, "data", "icons")
    try:
        generate_all_icons(icons_dir)
    except Exception as e:
        print(f"Generación de iconos omitida o diferida: {e}")

    return classifier


if __name__ == "__main__":
    train_all_models()
