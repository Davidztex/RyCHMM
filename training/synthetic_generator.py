"""
synthetic_generator.py
======================
Generador de trazos sintéticos canónicos y parametrizados para las 27 letras del español.
Permite aumentar datos con perturbaciones gaussianas, rotaciones y escalas, y provee
prototipos geométricos de referencia para el autocompletado y los iconos visuales.
"""

import numpy as np


class SyntheticGlyphGenerator:
    """
    Genera geometrías vectoriales limpias normalizadas en el rango [0, 100] x [0, 100]
    para las 27 letras minúsculas del alfabeto español.
    """

    @staticmethod
    def get_canonical_strokes(char):
        """
        Retorna una lista de trazos [(x, y), ...] para el carácter especificado.
        """
        ch = char.lower()
        strokes = []

        if ch == 'a':
            # Círculo antihorario iniciando arriba a la derecha + asta vertical descendente
            th = np.linspace(np.pi * 0.25, np.pi * 2.25, 30)
            circle = np.column_stack([48 + 22 * np.cos(th), 63 - 22 * np.sin(th)])
            line = np.column_stack([np.full(15, 70.0), np.linspace(42, 85, 15)])
            strokes = [circle.tolist(), line.tolist()]

        elif ch == 'b':
            # Asta vertical descendente + bucle inferior derecho
            stem = np.column_stack([np.full(25, 30.0), np.linspace(15, 85, 25)])
            th = np.linspace(np.pi * 0.5, -np.pi * 0.5, 25)
            loop = np.column_stack([30 + 35 * np.cos(th), 66.5 - 18.5 * np.sin(th)])
            strokes = [stem.tolist(), loop.tolist()]

        elif ch == 'c':
            # Arco curvado abierto a la derecha de arriba a abajo en sentido antihorario
            th = np.linspace(np.pi * 0.3, np.pi * 1.7, 30)
            arc = np.column_stack([48 + 25 * np.cos(th), 61 - 22 * np.sin(th)])
            strokes = [arc.tolist()]

        elif ch == 'd':
            # Bucle circular antihorario a la izquierda + asta vertical alta a la derecha
            th = np.linspace(0, 2 * np.pi, 25)
            circle = np.column_stack([45 + 20 * np.cos(th), 63 - 20 * np.sin(th)])
            stem = np.column_stack([np.full(25, 65.0), np.linspace(15, 85, 25)])
            strokes = [circle.tolist(), stem.tolist()]

        elif ch == 'e':
            # Barra horizontal central que se abre en bucle superior y curva inferior
            line = np.column_stack([np.linspace(25, 70, 15), np.full(15, 60.0)])
            th = np.linspace(0, 1.7 * np.pi, 30)
            loop = np.column_stack([48 + 23 * np.cos(th), 60 - 22 * np.sin(th)])
            strokes = [np.vstack([line, loop]).tolist()]

        elif ch == 'f':
            # Gancho superior curvado a la izquierda descendente + travesaño horizontal
            th = np.linspace(0, np.pi, 15)
            arch = np.column_stack([65 - 15 * np.cos(th), 25 - 10 * np.sin(th)])
            stem = np.column_stack([np.full(20, 50.0), np.linspace(25, 85, 20)])
            cross = np.column_stack([np.linspace(35, 65, 10), np.full(10, 48.0)])
            strokes = [np.vstack([arch, stem]).tolist(), cross.tolist()]

        elif ch == 'g':
            # Bucle superior antihorario + cola descendente con gancho inferior hacia la izquierda
            th = np.linspace(0, 2 * np.pi, 25)
            circle = np.column_stack([48 + 18 * np.cos(th), 52 - 18 * np.sin(th)])
            stem = np.column_stack([np.full(15, 66.0), np.linspace(42, 85, 15)])
            th_hook = np.linspace(0, np.pi * 0.8, 15)
            hook = np.column_stack([46 + 20 * np.cos(th_hook), 85 + 20 * np.sin(th_hook)])
            strokes = [circle.tolist(), np.vstack([stem, hook]).tolist()]

        elif ch == 'h':
            # Asta vertical + arco lateral derecho
            stem = np.column_stack([np.full(25, 30.0), np.linspace(15, 85, 25)])
            th = np.linspace(np.pi, 0, 20)
            arch = np.column_stack([50 + 20 * np.cos(th), 60 - 20 * np.sin(th)])
            down = np.column_stack([np.full(12, 70.0), np.linspace(60, 85, 12)])
            strokes = [stem.tolist(), np.vstack([arch, down]).tolist()]

        elif ch == 'i':
            # Asta corta vertical descendente + punto superior
            stem = np.column_stack([np.full(20, 50.0), np.linspace(45, 85, 20)])
            dot = [[50.0, 28.0], [50.0, 29.0]]
            strokes = [stem.tolist(), dot]

        elif ch == 'j':
            # Tallo descendente con gancho inferior + punto
            stem = np.column_stack([np.full(20, 55.0), np.linspace(45, 85, 20)])
            th = np.linspace(0, np.pi * 0.8, 15)
            hook = np.column_stack([35 + 20 * np.cos(th), 85 + 20 * np.sin(th)])
            dot = [[55.0, 28.0], [55.0, 29.0]]
            strokes = [np.vstack([stem, hook]).tolist(), dot]

        elif ch == 'k':
            # Asta vertical + 2 diagonales
            stem = np.column_stack([np.full(25, 30.0), np.linspace(15, 85, 25)])
            diag1 = np.column_stack([np.linspace(65, 30, 15), np.linspace(40, 62, 15)])
            diag2 = np.column_stack([np.linspace(30, 65, 15), np.linspace(62, 85, 15)])
            strokes = [stem.tolist(), diag1.tolist(), diag2.tolist()]

        elif ch == 'l':
            # Asta vertical larga con pequeño remate
            stem = np.column_stack([np.full(25, 45.0), np.linspace(15, 80, 25)])
            foot = np.column_stack([np.linspace(45, 55, 6), np.full(6, 82.0)])
            strokes = [np.vstack([stem, foot]).tolist()]

        elif ch == 'm':
            # Tallo + 2 arcos sucesivos
            stem = np.column_stack([np.full(15, 25.0), np.linspace(45, 85, 15)])
            th1 = np.linspace(np.pi, 0, 15)
            arch1 = np.column_stack([37.5 + 12.5 * np.cos(th1), 58 - 15 * np.sin(th1)])
            down1 = np.column_stack([np.full(10, 50.0), np.linspace(58, 85, 10)])
            th2 = np.linspace(np.pi, 0, 15)
            arch2 = np.column_stack([62.5 + 12.5 * np.cos(th2), 58 - 15 * np.sin(th2)])
            down2 = np.column_stack([np.full(10, 75.0), np.linspace(58, 85, 10)])
            strokes = [stem.tolist(), np.vstack([arch1, down1]).tolist(), np.vstack([arch2, down2]).tolist()]

        elif ch == 'n':
            # Tallo + 1 arco
            stem = np.column_stack([np.full(20, 30.0), np.linspace(45, 85, 20)])
            th = np.linspace(np.pi, 0, 20)
            arch = np.column_stack([50 + 20 * np.cos(th), 58 - 18 * np.sin(th)])
            down = np.column_stack([np.full(15, 70.0), np.linspace(58, 85, 15)])
            strokes = [stem.tolist(), np.vstack([arch, down]).tolist()]

        elif ch == 'ñ':
            # Tallo + arco de 'n' + virgulilla ondulada superior
            stem = np.column_stack([np.full(20, 30.0), np.linspace(45, 85, 20)])
            th = np.linspace(np.pi, 0, 20)
            arch = np.column_stack([50 + 20 * np.cos(th), 58 - 18 * np.sin(th)])
            down = np.column_stack([np.full(15, 70.0), np.linspace(58, 85, 15)])
            # Virgulilla ondulada
            x_tilde = np.linspace(30, 70, 20)
            y_tilde = 25 - 5 * np.sin(np.linspace(0, 2 * np.pi, 20))
            tilde = np.column_stack([x_tilde, y_tilde])
            strokes = [stem.tolist(), np.vstack([arch, down]).tolist(), tilde.tolist()]

        elif ch == 'o':
            # Círculo cerrado antihorario iniciando arriba
            th = np.linspace(np.pi * 0.5, np.pi * 2.5, 35)
            circle = np.column_stack([50 + 22 * np.cos(th), 60 - 22 * np.sin(th)])
            strokes = [circle.tolist()]

        elif ch == 'p':
            # Asta descendente larga + bucle derecho superior
            stem = np.column_stack([np.full(25, 30.0), np.linspace(45, 105, 25)])
            th = np.linspace(np.pi * 0.5, -np.pi * 0.5, 25)
            loop = np.column_stack([30 + 32 * np.cos(th), 60 - 15 * np.sin(th)])
            strokes = [stem.tolist(), loop.tolist()]

        elif ch == 'q':
            # Bucle izquierdo antihorario + asta descendente larga derecha
            th = np.linspace(0, 2 * np.pi, 25)
            circle = np.column_stack([45 + 18 * np.cos(th), 55 - 18 * np.sin(th)])
            stem = np.column_stack([np.full(25, 63.0), np.linspace(45, 105, 25)])
            strokes = [circle.tolist(), stem.tolist()]

        elif ch == 'r':
            # Tallo corto + pequeño arco superior derecho
            stem = np.column_stack([np.full(20, 35.0), np.linspace(45, 85, 20)])
            th = np.linspace(np.pi, np.pi * 0.15, 15)
            arch = np.column_stack([45 + 20 * np.cos(th), 60 - 16 * np.sin(th)])
            strokes = [stem.tolist(), arch.tolist()]

        elif ch == 's':
            # Curva en S de arriba a abajo
            t = np.linspace(0, 1, 35)
            x = 50 - 18 * np.sin(2 * np.pi * t)
            y = 40 + 44 * t
            strokes = [np.column_stack([x, y]).tolist()]

        elif ch == 't':
            # Asta vertical con gancho inferior + barra transversal
            stem = np.column_stack([np.full(20, 48.0), np.linspace(22, 80, 20)])
            hook = np.column_stack([np.linspace(48, 60, 6), np.linspace(80, 83, 6)])
            cross = np.column_stack([np.linspace(32, 65, 12), np.full(12, 42.0)])
            strokes = [np.vstack([stem, hook]).tolist(), cross.tolist()]

        elif ch == 'u':
            # Bajada, curva inferior y subida + pequeño trazo hacia abajo
            down = np.column_stack([np.full(15, 30.0), np.linspace(45, 70, 15)])
            th = np.linspace(np.pi, 0, 15)
            bottom = np.column_stack([50 + 20 * np.cos(th), 70 + 15 * np.sin(th)])
            up = np.column_stack([np.full(15, 70.0), np.linspace(70, 45, 15)])
            down_end = np.column_stack([np.full(10, 70.0), np.linspace(45, 85, 10)])
            strokes = [np.vstack([down, bottom, up]).tolist(), down_end.tolist()]

        elif ch == 'v':
            # Dos diagonales formando V
            d1 = np.column_stack([np.linspace(30, 50, 18), np.linspace(45, 85, 18)])
            d2 = np.column_stack([np.linspace(50, 70, 18), np.linspace(85, 45, 18)])
            strokes = [np.vstack([d1, d2]).tolist()]

        elif ch == 'w':
            # Dos V encadenadas
            d1 = np.column_stack([np.linspace(20, 35, 12), np.linspace(45, 85, 12)])
            d2 = np.column_stack([np.linspace(35, 50, 12), np.linspace(85, 50, 12)])
            d3 = np.column_stack([np.linspace(50, 65, 12), np.linspace(50, 85, 12)])
            d4 = np.column_stack([np.linspace(65, 80, 12), np.linspace(85, 45, 12)])
            strokes = [np.vstack([d1, d2, d3, d4]).tolist()]

        elif ch == 'x':
            # Dos diagonales cruzadas
            d1 = np.column_stack([np.linspace(30, 70, 20), np.linspace(45, 85, 20)])
            d2 = np.column_stack([np.linspace(70, 30, 20), np.linspace(45, 85, 20)])
            strokes = [d1.tolist(), diag_cross := d2.tolist()]

        elif ch == 'y':
            # Forma de U superior + trazo diagonal descendente largo
            u1 = np.column_stack([np.linspace(30, 50, 15), np.linspace(45, 70, 15)])
            u2 = np.column_stack([np.linspace(50, 70, 15), np.linspace(70, 45, 15)])
            tail = np.column_stack([np.linspace(70, 35, 25), np.linspace(45, 105, 25)])
            strokes = [np.vstack([u1, u2]).tolist(), tail.tolist()]

        elif ch == 'z':
            # Barra horizontal superior + diagonal + barra horizontal inferior
            top = np.column_stack([np.linspace(30, 70, 12), np.full(12, 45.0)])
            diag = np.column_stack([np.linspace(70, 30, 20), np.linspace(45, 85, 20)])
            bot = np.column_stack([np.linspace(30, 70, 12), np.full(12, 85.0)])
            strokes = [np.vstack([top, diag, bot]).tolist()]

        else:
            # Fallback genérico
            strokes = [[[30.0, 30.0], [70.0, 70.0]]]

        return strokes

    @classmethod
    def perturb_strokes(cls, strokes, noise_std=2.0, scale_range=(0.85, 1.15), angle_range=(-10, 10)):
        """Aplica aumentación de datos aleatoria: ruido gaussiano, escala y rotación."""
        scale = np.random.uniform(*scale_range)
        ang_deg = np.random.uniform(*angle_range)
        rad = np.radians(ang_deg)
        cos_a, sin_a = np.cos(rad), np.sin(rad)

        perturbed = []
        for stroke in strokes:
            pts = np.asarray(stroke, dtype=np.float64)
            # Centrar en (50, 50)
            centered = pts - 50.0
            # Escala
            scaled = centered * scale
            # Rotación
            rot_x = scaled[:, 0] * cos_a - scaled[:, 1] * sin_a
            rot_y = scaled[:, 0] * sin_a + scaled[:, 1] * cos_a
            # Ruido
            noise = np.random.normal(0.0, noise_std, size=pts.shape)
            final_pts = np.column_stack([rot_x, rot_y]) + 50.0 + noise
            perturbed.append(final_pts.tolist())

        return perturbed
