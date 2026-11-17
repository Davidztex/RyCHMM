"""
apply_light_theme.py
Reemplaza todos los colores oscuros hardcodeados en los archivos GUI
por colores del tema claro:
  Fondo: #FFFFFE  Texto: #111111  Acento: #1565C0  Blanco: #FFFFFE
"""
import os, re

# Mapeo de colores oscuros -> claros
# Formato: (patron_regex, reemplazo)
COLOR_MAP = [
    # Fondos oscuros principales → fondo blanco / casi blanco
    (r'#0d1117', '#FFFFFE'),
    (r'#0b0e14', '#F5F7FA'),
    (r'#0e1219', '#F5F7FA'),
    (r'#161b22', '#EEF2FF'),
    (r'#1c2330', '#E8EFFF'),
    (r'#0d1e2e', '#D6E4FF'),
    (r'#21262d', '#E0E8FF'),
    (r'#30363d', '#C8D8F0'),
    (r'#2a1215', '#FDECEA'),
    (r'#3e1b1e', '#FDECEA'),
    (r'#482326', '#FADDD9'),

    # Colores de texto claros → negro / gris oscuro
    (r'#e6edf3', '#111111'),
    (r'#f0f6fc', '#111111'),
    (r'#c9d1d9', '#222222'),
    (r'#8b949e', '#555555'),
    (r'#484f58', '#777777'),

    # Acentos cian → azul #1565C0
    (r'#00d2ff', '#1565C0'),
    (r'#00b4d8', '#1976D2'),
    (r'#90e0ef', '#42A5F5'),

    # Acentos azul claro → azul oscuro
    (r'#58a6ff', '#1565C0'),
    (r'#388bfd', '#1565C0'),
    (r'#3b82f6', '#1976D2'),

    # Gradientes azul oscuro → gradiente azul marino
    (r'#0077b6', '#0D47A1'),
    (r'#0096c7', '#1565C0'),

    # Bordes
    (r'#30363d', '#BBCDE5'),
    (r'#363b42', '#BBCDE5'),

    # Rojo peligro
    (r'#da3633', '#C62828'),
    (r'#f85149', '#C62828'),

    # Semitransparentes oscuros → blancos translúcidos
    (r'rgba\(22,\s*27,\s*34,\s*0\.88\)', 'rgba(255, 255, 254, 0.88)'),
    (r'rgba\(22,\s*27,\s*34,\s*[\d.]+\)', 'rgba(240, 244, 255, 0.90)'),

    # 1f6feb (azul medio)
    (r'#1f6feb', '#1565C0'),
]

GUI_DIR = os.path.join(os.path.dirname(__file__), 'gui')
SKIP = {'styles.py'}  # ya actualizado manualmente

changed_files = []
for root, dirs, files in os.walk(GUI_DIR):
    for fname in files:
        if not fname.endswith('.py') or fname in SKIP:
            continue
        path = os.path.join(root, fname)
        with open(path, 'r', encoding='utf-8') as f:
            original = f.read()
        content = original
        for pat, rep in COLOR_MAP:
            content = re.sub(pat, rep, content, flags=re.IGNORECASE)
        if content != original:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            changed_files.append(fname)
            print(f"  OK {fname}")

print(f"\nTotal archivos actualizados: {len(changed_files)}")
