"""
FeatureExtractor.py
===================
Módulo de procesamiento geométrico, remuestreo espacial equidistante,
cuantización angular en código de cadena K=16 y transformaciones esféricas 3D.
"""

import numpy as np


class FeatureExtractor:
    """
    Extractor de características geométricas 2D y 3D para el modelo HMM.
    Discretiza trayectorias continuas en secuencias de símbolos angulares K=16.
    """

    K_SECTORS = 16
    SECTOR_SIZE_RAD = 2.0 * np.pi / 16.0  # 22.5 grados por sector

    @staticmethod
    def resample_polyline_2d(points, step=12.0):
        """
        Remuestrea una secuencia de puntos 2D a intervalos de longitud de arco equidistantes.
        Elimina la dependencia de la velocidad con que el usuario mueve el ratón.
        
        Parámetros:
        -----------
        points : list of (x, y) or np.ndarray
        step : float (espaciamiento euclidiano deseado en píxeles)
        
        Retorna:
        --------
        np.ndarray de dimensión (M, 2)
        """
        pts = np.asarray(points, dtype=np.float64)
        if len(pts) < 2:
            return pts

        diffs = np.diff(pts, axis=0)
        dists = np.hypot(diffs[:, 0], diffs[:, 1])
        total_len = np.sum(dists)

        if total_len < 1e-3:
            return pts[:1]

        cum_dist = np.insert(np.cumsum(dists), 0, 0.0)
        num_target = max(2, int(np.round(total_len / step)) + 1)
        target_dists = np.linspace(0.0, total_len, num_target)

        resampled = np.zeros((num_target, 2), dtype=np.float64)
        resampled[:, 0] = np.interp(target_dists, cum_dist, pts[:, 0])
        resampled[:, 1] = np.interp(target_dists, cum_dist, pts[:, 1])
        return resampled

    @classmethod
    def quantize_angle_2d(cls, dx, dy):
        """
        Cuantiza el vector de desplazamiento continuo (dx, dy) en uno de los K=16 sectores angulares.
        
        Sectores:
        0: [ -11.25°, +11.25° ] -> Hacia la derecha (+X)
        4: [ 78.75°, 101.25° ]  -> Hacia abajo (+Y en coordenadas de pantalla)
        8: [ 168.75°, 191.25° ] -> Hacia la izquierda (-X)
        12: [ 258.75°, 281.25° ] -> Hacia arriba (-Y en coordenadas de pantalla)
        """
        angle = np.arctan2(dy, dx)
        if angle < 0.0:
            angle += 2.0 * np.pi

        # Desfase de medio sector para que el sector 0 quede centrado en 0 radianes
        half_sector = cls.SECTOR_SIZE_RAD / 2.0
        sector = int(np.floor((angle + half_sector) / cls.SECTOR_SIZE_RAD)) % cls.K_SECTORS
        return sector

    @classmethod
    def sector_to_vector_2d(cls, sector):
        """
        Convierte un símbolo discreto del sector angular k en un vector unitario 2D (cos, sin).
        """
        angle = (int(sector) % cls.K_SECTORS) * cls.SECTOR_SIZE_RAD
        return float(np.cos(angle)), float(np.sin(angle))

    @classmethod
    def extract_symbols_from_strokes_2d(cls, strokes, step=None):
        """
        Dada una lista de trazos (cada uno con puntos [(x, y), ...]),
        remuestrea cada trazo individualmente y extrae la secuencia de observaciones discretas.
        
        Invarianza de escala: Si step=None, el paso de remuestreo se adapta dinámicamente
        a la dimensión característica de los trazos (step = max(6.0, dim / 25.0)), asegurando
        que tanto letras pequeñas (40px) como grandes (600px+) generen secuencias consistentes
        y compatibles con los modelos HMM.
        """
        if step is None:
            all_pts = [p for st in strokes for p in st if len(p) >= 2]
            if len(all_pts) >= 2:
                pts_arr = np.asarray(all_pts, dtype=np.float64)
                w = float(pts_arr[:, 0].max() - pts_arr[:, 0].min())
                h = float(pts_arr[:, 1].max() - pts_arr[:, 1].min())
                dim = max(w, h)
                step = float(np.clip(dim / 25.0, 6.0, 32.0))
            else:
                step = 10.0

        symbols = []
        resampled_strokes = []

        for stroke in strokes:
            if len(stroke) < 2:
                continue
            res_pts = cls.resample_polyline_2d(stroke, step=step)
            if len(res_pts) < 2:
                continue
            resampled_strokes.append(res_pts)
            diffs = np.diff(res_pts, axis=0)
            for dx, dy in diffs:
                s = cls.quantize_angle_2d(dx, dy)
                symbols.append(s)

        return symbols, resampled_strokes

    @classmethod
    def reconstruct_trajectory_2d(cls, start_pos, symbols, step=12.0):
        """
        Reconstruye las coordenadas proyectadas (x_t, y_t) a partir de una posición inicial
        del cursor y una secuencia de símbolos discretos proyectados por el modelo HMM.
        """
        if not symbols:
            return []

        traj = [list(start_pos)]
        curr_x, curr_y = float(start_pos[0]), float(start_pos[1])

        for s in symbols:
            dx, dy = cls.sector_to_vector_2d(s)
            curr_x += dx * step
            curr_y += dy * step
            traj.append([curr_x, curr_y])

        return traj

    # -------------------------------------------------------------
    # Métodos para Geometría y Cuantización Esférica 3D
    # -------------------------------------------------------------

    @staticmethod
    def cartesian_to_spherical(x, y, z, radius=1.0):
        """
        Convierte un punto cartesiano 3D (x, y, z) a coordenadas esféricas (r, theta, phi).
        
        theta: Azimut / longitud en [-pi, pi]
        phi: Colatitud / ángulo polar desde el eje +Z en [0, pi]
        """
        r = np.sqrt(x * x + y * y + z * z)
        if r < 1e-9:
            return 0.0, 0.0, 0.0
        theta = np.arctan2(y, x)
        phi = np.arccos(np.clip(z / r, -1.0, 1.0))
        return float(r), float(theta), float(phi)

    @staticmethod
    def spherical_to_cartesian(radius, theta, phi):
        """Convierte coordenadas esféricas (r, theta, phi) a cartesianas 3D (x, y, z)."""
        x = radius * np.sin(phi) * np.cos(theta)
        y = radius * np.sin(phi) * np.sin(theta)
        z = radius * np.cos(phi)
        return float(x), float(y), float(z)

    @classmethod
    def resample_polyline_3d_sphere(cls, points_3d, radius=1.0, step=0.08):
        """
        Remuestrea puntos 3D sobre la superficie de una esfera mediante geodésicas (arcos circulares).
        """
        pts = np.asarray(points_3d, dtype=np.float64)
        if len(pts) < 2:
            return pts

        # Proyectar rigurosamente cada punto al cascarón esférico
        norms = np.linalg.norm(pts, axis=1, keepdims=True)
        norms[norms < 1e-9] = 1.0
        unit_pts = pts / norms * radius

        # Calcular distancias angulares sucesivas
        arc_lengths = []
        for i in range(len(unit_pts) - 1):
            p1 = unit_pts[i] / radius
            p2 = unit_pts[i + 1] / radius
            dot = np.clip(np.dot(p1, p2), -1.0, 1.0)
            ang = np.arccos(dot)
            arc_lengths.append(radius * ang)

        total_arc = sum(arc_lengths)
        if total_arc < 1e-3:
            return unit_pts[:1]

        cum_arcs = np.insert(np.cumsum(arc_lengths), 0, 0.0)
        num_target = max(2, int(np.round(total_arc / step)) + 1)
        target_arcs = np.linspace(0.0, total_arc, num_target)

        # Interpolación Slerp simplificada a lo largo de los arcos acumulados
        resampled = []
        for targ in target_arcs:
            idx = np.searchsorted(cum_arcs, targ)
            if idx == 0:
                resampled.append(unit_pts[0])
            elif idx >= len(unit_pts):
                resampled.append(unit_pts[-1])
            else:
                a0, a1 = cum_arcs[idx - 1], cum_arcs[idx]
                span = a1 - a0
                frac = 0.0 if span < 1e-6 else (targ - a0) / span
                p0 = unit_pts[idx - 1]
                p1 = unit_pts[idx]
                # Interpolación esférica (Slerp)
                dot = np.clip(np.dot(p0, p1) / (radius * radius), -1.0, 1.0)
                omega = np.arccos(dot)
                if omega < 1e-5:
                    interp = p0
                else:
                    interp = (np.sin((1 - frac) * omega) * p0 + np.sin(frac * omega) * p1) / np.sin(omega)
                # Re-normalizar a radio exacto
                interp = interp / np.linalg.norm(interp) * radius
                resampled.append(interp)

        return np.asarray(resampled, dtype=np.float64)

    @classmethod
    def extract_symbols_from_sphere_points(cls, points_3d, radius=1.0, step=None,
                                           cam_right=None, cam_down=None):
        """
        Discretiza un trazo 3D sobre la esfera en símbolos angulares K=16.

        Método correcto e invariante a la posición en la esfera:
        - Calcula el vector tangente cartesiano en cada par de puntos consecutivos.
        - Lo proyecta sobre el plano tangente LOCAL de la esfera en ese punto.
        - Expresa el vector tangente en una base {u_x, u_y} consistente con la vista del usuario:
              u_x = dirección "derecha" de cámara (cam_right), proyectada en el plano tangente
              u_y = dirección "abajo" de cámara (cam_down), proyectada en el plano tangente
        - Si cam_right/cam_down no se dan, se usa la base global {X, -Y} como aproximación.

        Esto hace que los símbolos sean CONSISTENTES con los modelos HMM entrenados en 2D,
        independientemente de en qué región de la esfera se dibuje.

        Parámetros:
        -----------
        cam_right : np.ndarray(3,) — vector "derecha" del frame de cámara en espacio mundo
        cam_down  : np.ndarray(3,) — vector "abajo" del frame de cámara en espacio mundo
        """
        if len(points_3d) < 2:
            return [], []

        pts_arr = np.asarray(points_3d, dtype=np.float64)

        # Paso adaptativo según longitud geodésica total
        if step is None:
            norms_arr = np.linalg.norm(pts_arr, axis=1, keepdims=True).clip(1e-9)
            unit_arr = pts_arr / norms_arr
            total_arc = 0.0
            for i in range(len(unit_arr) - 1):
                dot = float(np.clip(np.dot(unit_arr[i], unit_arr[i+1]), -1.0, 1.0))
                total_arc += radius * np.arccos(dot)
            step = float(np.clip(total_arc / 25.0, 0.025, 0.14))

        res_pts = cls.resample_polyline_3d_sphere(points_3d, radius=radius, step=step)
        if len(res_pts) < 2:
            return [], res_pts

        # Base global del frame de cámara (vectores en espacio mundo)
        # Estos representan "derecha" y "abajo" en la pantalla del usuario.
        if cam_right is not None and cam_down is not None:
            g_right = np.asarray(cam_right, dtype=np.float64)
            g_down  = np.asarray(cam_down,  dtype=np.float64)
        else:
            # Base global predeterminada: X=derecha, Y=arriba => down = -Y global
            # Consistente con la vista frontal por defecto (yaw=0, pitch=0)
            g_right = np.array([1.0, 0.0, 0.0], dtype=np.float64)
            g_down  = np.array([0.0, -1.0, 0.0], dtype=np.float64)

        symbols = []
        for i in range(len(res_pts) - 1):
            p_prev = np.asarray(res_pts[i],   dtype=np.float64)
            p_curr = np.asarray(res_pts[i+1], dtype=np.float64)

            # Vector tangente cartesiano
            tangent = p_curr - p_prev

            # Normal de la esfera en p_prev
            n = p_prev / (np.linalg.norm(p_prev) + 1e-9)

            # Proyectar tangente sobre el plano tangente local
            tang_proj = tangent - np.dot(tangent, n) * n
            tang_norm = np.linalg.norm(tang_proj)
            if tang_norm < 1e-9:
                continue

            # Proyectar los vectores globales del frame de cámara sobre el plano tangente
            # para obtener una base 2D local consistente con la vista del usuario
            u_x = g_right - np.dot(g_right, n) * n
            norm_ux = np.linalg.norm(u_x)
            if norm_ux < 1e-7:
                # Si g_right es paralelo a n (improbable pero posible), usar g_down
                u_x = np.cross(n, g_down)
                norm_ux = np.linalg.norm(u_x)
            u_x = u_x / max(norm_ux, 1e-9)

            u_y = g_down - np.dot(g_down, n) * n
            norm_uy = np.linalg.norm(u_y)
            if norm_uy < 1e-7:
                u_y = np.cross(u_x, n)
                norm_uy = np.linalg.norm(u_y)
            u_y = u_y / max(norm_uy, 1e-9)

            # Componentes del vector tangente en la base local {u_x, u_y}
            # = {derecha, abajo} en pantalla = mismo convenio que 2D
            comp_x = float(np.dot(tang_proj, u_x))   # "dx" en pantalla
            comp_y = float(np.dot(tang_proj, u_y))   # "dy" en pantalla (positivo = abajo)

            # Cuantizar con el mismo convenio que quantize_angle_2d
            psi = np.arctan2(comp_y, comp_x)
            if psi < 0.0:
                psi += 2.0 * np.pi

            half_sec = cls.SECTOR_SIZE_RAD / 2.0
            sector = int(np.floor((psi + half_sec) / cls.SECTOR_SIZE_RAD)) % cls.K_SECTORS
            symbols.append(sector)

        return symbols, res_pts

    @classmethod
    def reconstruct_trajectory_3d_sphere(cls, start_pt_3d, symbols, radius=1.0, step=0.08):
        """
        Reconstruye la trayectoria proyectada en el cascarón esférico 3D a partir de un punto
        de inicio 3D y la secuencia de símbolos discretos proyectados por el modelo HMM.
        """
        if not symbols:
            return []

        # Asegurar que el punto inicial esté rigurosamente en la esfera
        p0 = np.asarray(start_pt_3d, dtype=np.float64)
        norm = np.linalg.norm(p0)
        if norm < 1e-6:
            p0 = np.array([0.0, 0.0, radius], dtype=np.float64)
        else:
            p0 = p0 / norm * radius

        _, curr_th, curr_phi = cls.cartesian_to_spherical(p0[0], p0[1], p0[2], radius)
        traj_3d = [p0.tolist()]

        delta_sigma = step / max(radius, 1e-6)  # Paso angular sobre el gran círculo

        for s in symbols:
            # Ángulo de rumbo tangencial psi
            psi = (int(s) % cls.K_SECTORS) * cls.SECTOR_SIZE_RAD
            d_phi = delta_sigma * np.sin(psi)
            sin_phi = max(np.sin(curr_phi), 0.05)
            d_theta = (delta_sigma * np.cos(psi)) / sin_phi

            curr_phi = np.clip(curr_phi + d_phi, 0.01, np.pi - 0.01)
            curr_th += d_theta
            while curr_th > np.pi:
                curr_th -= 2.0 * np.pi
            while curr_th < -np.pi:
                curr_th += 2.0 * np.pi

            x, y, z = cls.spherical_to_cartesian(radius, curr_th, curr_phi)
            traj_3d.append([x, y, z])

        return traj_3d

    @classmethod
    def predict_complete_projection_2d(cls, strokes, top_char, classifier=None, step_dots=None):
        r"""
        Implementa estrictamente el Modelo de Proyección de Trayectoria Futura (Sección 3.5):
        1. Dada la secuencia parcial O_{1:t}, se evalúa la verosimilitud P(O_{1:t} | \lambda_c)
           usando el algoritmo Forward (\alpha_t(i)).
        2. Se identifica el carácter de máxima probabilidad: \hat{c} = \arg\max_c P(O_{1:t} | \lambda_c).
        3. Se mapean DIRECTAMENTE las coordenadas canónicas restantes al espacio de pantalla:
               T(P) = u_curr + scale * (P - p_anchor)
           Esto evita el error acumulado de reconstruir desde símbolos cuantizados.

        Retorna:
            Lista de trazos proyectados [stroke1_dots, stroke2_dots, ...],
            donde cada trazo es una lista de puntos [[x, y], ...].
        """
        from training.synthetic_generator import SyntheticGlyphGenerator

        if not strokes or not strokes[-1] or len(strokes[-1]) < 1:
            return []

        u_curr = np.asarray(strokes[-1][-1], dtype=np.float64)

        # 1. Extraer secuencia de símbolos discretos O_{1:t} del usuario
        symbols, _ = cls.extract_symbols_from_strokes_2d(strokes)
        if not symbols and len(strokes[-1]) >= 2:
            p0, p1 = strokes[-1][0], strokes[-1][-1]
            dx, dy = p1[0] - p0[0], p1[1] - p0[1]
            if dx * dx + dy * dy >= 9.0:
                symbols = [cls.quantize_angle_2d(dx, dy)]

        # 2. Forward alpha_t(i) => tau (fracción de progreso en la secuencia canónica)
        model = None
        if classifier is not None and hasattr(classifier, 'models'):
            model = classifier.models.get(top_char)

        if model is not None and symbols:
            _, alpha_hat, _ = model.forward(symbols)
            alpha_last = alpha_hat[-1]
            exp_state = float(np.sum(np.arange(model.N) * alpha_last))
            tau = float(np.clip((exp_state + 0.5) / float(model.N), 0.05, 0.95))
        else:
            tau = 0.20

        # 3. Trayectoria canónica como COORDENADAS (no símbolos)
        #    Paso fino para suavidad: CANON_STEP = 3px en espacio [0,100]
        canon_strokes_raw = SyntheticGlyphGenerator.get_canonical_strokes(top_char)
        if not canon_strokes_raw:
            return []

        CANON_STEP = 3.0
        canon_res = []          # list of np.ndarray shape (M, 2)
        canon_cum = []          # arc-length cumulatives per stroke
        for st in canon_strokes_raw:
            pts = np.asarray(st, dtype=np.float64)
            if len(pts) >= 2:
                r = cls.resample_polyline_2d(pts, step=CANON_STEP)
                if len(r) >= 2:
                    dists = np.linalg.norm(np.diff(r, axis=0), axis=1)
                    cum = np.insert(np.cumsum(dists), 0, 0.0)
                    canon_res.append(r)
                    canon_cum.append(cum)

        if not canon_res:
            return []

        # Índice del trazo activo (el que se está dibujando)
        s_idx = min(len(strokes) - 1, len(canon_res) - 1)
        r_active = canon_res[s_idx]       # (M, 2)  coordenadas canónicas del trazo activo
        cum_active = canon_cum[s_idx]     # (M,)    longitud de arco acumulada
        L_active_total = cum_active[-1]

        # Punto de anclaje: tau * L_total en el trazo activo (arco canónico)
        target_arc = tau * L_active_total
        k_anchor = int(np.searchsorted(cum_active, target_arc, side='right')) - 1
        k_anchor = int(np.clip(k_anchor, 1, len(r_active) - 2))
        p_anchor = r_active[k_anchor]     # punto canónico que corresponde al cursor

        # 4. Escala: se combinan dos estimadores y se toma el más conservador
        L_user = sum(
            float(np.sum(np.linalg.norm(np.diff(np.asarray(st, dtype=np.float64), axis=0), axis=1)))
            for st in strokes if len(st) >= 2
        )
        L_canon_anchor = float(cum_active[k_anchor])
        L_canon_total  = float(cum_active[-1])

        # Estimador 1: ratio de arco usuario / canónico hasta k_anchor
        # Solo confiable cuando L_canon_anchor es una fracción razonable del total
        arc_reliable = (L_user >= 8.0 and L_canon_anchor >= 0.10 * max(L_canon_total, 1.0))
        scale_arc = float(np.clip(L_user / max(L_canon_anchor, 1e-3), 0.15, 60.0)) if arc_reliable else None

        # Estimador 2: ratio bounding-box (siempre calculado como referencia)
        all_drawn = np.vstack([np.asarray(st, dtype=np.float64) for st in strokes if len(st) > 0])
        dim_drawn = max(
            float(all_drawn[:, 0].max() - all_drawn[:, 0].min()),
            float(all_drawn[:, 1].max() - all_drawn[:, 1].min()), 1.0
        )
        all_canon = np.vstack(canon_res)
        dim_canon = max(
            float(all_canon[:, 0].max() - all_canon[:, 0].min()),
            float(all_canon[:, 1].max() - all_canon[:, 1].min()), 1.0
        )
        scale_bb = float(np.clip(dim_drawn / dim_canon, 0.15, 60.0))

        # Elegir: si arc_reliable y la diferencia con BB es < 4×, usar arco; si no, usar BB
        if scale_arc is not None and scale_arc <= 4.0 * scale_bb:
            scale = scale_arc
        else:
            scale = scale_bb

        # Espaciado entre puntos proyectados (proporcional a la escala)
        dot_step = step_dots if step_dots else float(np.clip(5.0 * max(scale, 0.5) ** 0.5, 5.0, 25.0))

        projected_strokes = []

        # 5a. Parte restante del trazo activo: transformación directa de coordenadas
        #     T(P) = u_curr + scale * (P - p_anchor)   <- cero error acumulado
        rem_canon = r_active[k_anchor:]     # (K, 2)
        if len(rem_canon) >= 2:
            rem_proj = u_curr + scale * (rem_canon - p_anchor)   # (K, 2)
            dots = cls.resample_polyline_2d(rem_proj, step=dot_step)
            projected_strokes.append(dots.tolist() if len(dots) >= 2 else rem_proj.tolist())

        # 5b. Trazos canónicos subsiguientes (ej. punto de 'i', tilde de 'ñ', travesaño de 't')
        for j in range(s_idx + 1, len(canon_res)):
            st_j = canon_res[j]                                   # (K, 2)
            st_j_proj = u_curr + scale * (st_j - p_anchor)       # misma transformación T
            dots_j = cls.resample_polyline_2d(st_j_proj, step=dot_step)
            projected_strokes.append(dots_j.tolist() if len(dots_j) >= 2 else st_j_proj.tolist())

        return projected_strokes

    @classmethod
    def predict_complete_projection_3d(cls, all_strokes_3d, top_char, radius=1.0,
                                       classifier=None, step_dots=None,
                                       cam_right=None, cam_down=None):
        r"""
        Proyección de Trayectoria Futura 3D (Sección 3.5) — enfoque en espacio de coordenadas:

        1. O_{1:t} = símbolos extraídos de todos los trazos dibujados sobre la esfera
           utilizando el frame de cámara (invariante a rotación de esfera y posición de dibujo).
        2. Forward alpha_t(i) => tau (progreso fraccionario en la secuencia canónica).
        3. Base tangente local {ux, uy} en p_curr_3d derivada de la vista del usuario:
               ux = cam_right proyectado sobre el plano tangente local (dirección horizontal)
               uy = cam_down proyectado sobre el plano tangente local (dirección vertical hacia abajo)
        4. Coordenadas canónicas restantes mapeadas directamente sobre la superficie esférica:
               V_3d(P) = p_curr + scale*(P.x - p_a.x)*ux + scale*(P.y - p_a.y)*uy
               P_sphere = V_3d / ||V_3d|| * radius
        5. Esto reproduce fielmente la FORMA y TAMAÑO de la letra sobre la esfera,
           completando todo el trazo faltante con puntos (GL_POINTS).
        """
        from training.synthetic_generator import SyntheticGlyphGenerator

        if not all_strokes_3d:
            return []

        # Reunir todos los puntos en orden
        all_pts_flat = []
        for st in all_strokes_3d:
            all_pts_flat.extend(st)

        if not all_pts_flat:
            return []

        p_curr_3d = np.asarray(all_pts_flat[-1], dtype=np.float64)
        norm_curr = np.linalg.norm(p_curr_3d)
        if norm_curr < 1e-9:
            return []
        p_curr_3d = p_curr_3d / norm_curr * radius

        # 1. Extraer símbolos O_{1:t} de todos los trazos usando frame de cámara
        symbols, _ = cls.extract_symbols_from_sphere_points(
            all_pts_flat, radius=radius, cam_right=cam_right, cam_down=cam_down
        )
        if not symbols and len(all_pts_flat) >= 2:
            p0 = np.asarray(all_pts_flat[0], dtype=np.float64)
            p1 = p_curr_3d
            d = p1 - p0 / (np.linalg.norm(p0) + 1e-9) * radius
            if np.linalg.norm(d) > 1e-5:
                # Fallback con base tangente
                if cam_right is not None and cam_down is not None:
                    dx = float(np.dot(d, cam_right))
                    dy = float(np.dot(d, cam_down))
                    symbols = [cls.quantize_angle_2d(dx, dy)]

        # 2. Forward alpha_t(i) => tau
        model = None
        if classifier is not None and hasattr(classifier, 'models'):
            model = classifier.models.get(top_char)

        if model is not None and symbols:
            _, alpha_hat, _ = model.forward(symbols)
            alpha_last = alpha_hat[-1]
            exp_state = float(np.sum(np.arange(model.N) * alpha_last))
            tau = float(np.clip((exp_state + 0.5) / float(model.N), 0.05, 0.95))
        else:
            tau = 0.20

        # 3. Coordenadas canónicas densas del glifo en [0,100]x[0,100]
        canon_strokes_raw = SyntheticGlyphGenerator.get_canonical_strokes(top_char)
        if not canon_strokes_raw:
            return []

        CANON_STEP = 3.0
        canon_res = []
        canon_cum = []
        for st in canon_strokes_raw:
            pts = np.asarray(st, dtype=np.float64)
            if len(pts) >= 2:
                r = cls.resample_polyline_2d(pts, step=CANON_STEP)
                if len(r) >= 2:
                    dists = np.linalg.norm(np.diff(r, axis=0), axis=1)
                    cum = np.insert(np.cumsum(dists), 0, 0.0)
                    canon_res.append(r)
                    canon_cum.append(cum)

        if not canon_res:
            return []

        # Trazo canónico activo (coincide con el trazo que se está dibujando)
        s_idx = min(len(all_strokes_3d) - 1, len(canon_res) - 1)
        r_active = canon_res[s_idx]
        cum_active = canon_cum[s_idx]
        L_active_total = cum_active[-1]

        # Punto de anclaje en arco canónico según tau
        target_arc = tau * L_active_total
        k_anchor = int(np.searchsorted(cum_active, target_arc, side='right')) - 1
        k_anchor = int(np.clip(k_anchor, 1, len(r_active) - 2))
        p_anchor_2d = r_active[k_anchor]   # punto canónico 2D que coincide con el cursor

        # 4. Base tangente ortonormal local en p_curr_3d alineada con la vista de cámara
        n_hat = p_curr_3d / radius
        if cam_right is not None and cam_down is not None:
            g_right = np.asarray(cam_right, dtype=np.float64)
            g_down  = np.asarray(cam_down,  dtype=np.float64)
        else:
            g_right = np.array([1.0, 0.0, 0.0], dtype=np.float64)
            g_down  = np.array([0.0, -1.0, 0.0], dtype=np.float64)

        ux = g_right - np.dot(g_right, n_hat) * n_hat
        n_ux = np.linalg.norm(ux)
        if n_ux < 1e-7:
            ux = np.cross(n_hat, g_down)
            n_ux = np.linalg.norm(ux)
        ux = ux / max(n_ux, 1e-9)

        uy = g_down - np.dot(g_down, n_hat) * n_hat
        n_uy = np.linalg.norm(uy)
        if n_uy < 1e-7:
            uy = np.cross(ux, n_hat)
            n_uy = np.linalg.norm(uy)
        uy = uy / max(n_uy, 1e-9)

        # 5. Escala: estimador por arco geodésico y bounding-box esférico
        total_arc_3d = 0.0
        for st in all_strokes_3d:
            st_arr = np.asarray(st, dtype=np.float64)
            if len(st_arr) >= 2:
                p_n = st_arr / np.linalg.norm(st_arr, axis=1, keepdims=True).clip(1e-9)
                for i in range(len(p_n) - 1):
                    dot = float(np.clip(np.dot(p_n[i], p_n[i+1]), -1.0, 1.0))
                    total_arc_3d += radius * np.arccos(dot)

        L_canon_anchor = float(cum_active[k_anchor])
        L_canon_total  = float(cum_active[-1])

        arc_reliable = (total_arc_3d >= 0.01 and L_canon_anchor >= 0.10 * max(L_canon_total, 1.0))
        scale_arc = float(np.clip(total_arc_3d / max(L_canon_anchor, 1e-4), 0.0005, 0.08)) if arc_reliable else None

        all_pts_arr = np.asarray(all_pts_flat, dtype=np.float64)
        if len(all_pts_arr) >= 2:
            span_3d = float(np.max(np.linalg.norm(all_pts_arr - all_pts_arr[0], axis=1)))
        else:
            span_3d = 0.05
        all_canon = np.vstack(canon_res)
        dim_canon = max(
            float(all_canon[:, 0].max() - all_canon[:, 0].min()),
            float(all_canon[:, 1].max() - all_canon[:, 1].min()), 1.0
        )
        scale_bb = float(np.clip(span_3d / dim_canon, 0.0005, 0.08))

        if scale_arc is not None and scale_arc <= 4.0 * scale_bb:
            scale_3d = scale_arc
        else:
            scale_3d = scale_bb

        # Espaciado entre puntos para autocompletado con puntos (GL_POINTS)
        dot_spacing = step_dots if step_dots else float(np.clip(scale_3d * 6.0, 0.015, 0.06))

        def _map_canon_to_sphere(pts_2d, p_anchor2d, p_curr, ux_v, uy_v, sc, R):
            """Mapea puntos canónicos 2D al cascarón esférico via base tangente local."""
            result = []
            for p2d in pts_2d:
                dx2d = (p2d[0] - p_anchor2d[0]) * sc
                dy2d = (p2d[1] - p_anchor2d[1]) * sc
                v = p_curr + dx2d * ux_v + dy2d * uy_v
                nv = np.linalg.norm(v)
                if nv > 1e-9:
                    result.append((v / nv * R).tolist())
            return result

        projected_strokes_3d = []

        # 5a. Parte restante del trazo activo
        rem_canon = r_active[k_anchor:]
        if len(rem_canon) >= 2:
            proj_pts = _map_canon_to_sphere(rem_canon, p_anchor_2d, p_curr_3d, ux, uy, scale_3d, radius)
            if len(proj_pts) >= 2:
                dots = cls.resample_polyline_3d_sphere(proj_pts, radius=radius, step=dot_spacing)
                projected_strokes_3d.append(dots.tolist() if len(dots) >= 2 else proj_pts)

        # 5b. Trazos canónicos subsiguientes (punto de 'i', tilde de 'ñ', travesaño de 't', etc.)
        for j in range(s_idx + 1, len(canon_res)):
            st_j = canon_res[j]
            proj_pts_j = _map_canon_to_sphere(st_j, p_anchor_2d, p_curr_3d, ux, uy, scale_3d, radius)
            if len(proj_pts_j) >= 2:
                dots_j = cls.resample_polyline_3d_sphere(proj_pts_j, radius=radius, step=dot_spacing)
                projected_strokes_3d.append(dots_j.tolist() if len(dots_j) >= 2 else proj_pts_j)

        return projected_strokes_3d
