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
    def extract_symbols_from_strokes_2d(cls, strokes, step=12.0):
        """
        Dada una lista de trazos (cada uno con puntos [(x, y), ...]),
        remuestrea cada trazo individualmente y extrae la secuencia de observaciones discretas.
        """
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
    def extract_symbols_from_sphere_points(cls, points_3d, radius=1.0, step=0.08):
        """
        Discretiza un trazo 3D sobre la esfera en símbolos angulares K=16 evaluando
        variaciones tangenciales (Delta_theta, Delta_phi).
        """
        if len(points_3d) < 2:
            return [], []

        res_pts = cls.resample_polyline_3d_sphere(points_3d, radius=radius, step=step)
        if len(res_pts) < 2:
            return [], res_pts

        symbols = []
        for i in range(len(res_pts) - 1):
            p_prev = res_pts[i]
            p_curr = res_pts[i + 1]

            _, th_prev, phi_prev = cls.cartesian_to_spherical(p_prev[0], p_prev[1], p_prev[2], radius)
            _, th_curr, phi_curr = cls.cartesian_to_spherical(p_curr[0], p_curr[1], p_curr[2], radius)

            # Diferencia angular con corrección del salto periódico [-pi, pi]
            d_theta = th_curr - th_prev
            while d_theta > np.pi:
                d_theta -= 2.0 * np.pi
            while d_theta < -np.pi:
                d_theta += 2.0 * np.pi

            d_phi = phi_curr - phi_prev

            # Vector tangencial en la superficie local
            phi_mid = 0.5 * (phi_prev + phi_curr)
            v_theta = radius * np.sin(phi_mid) * d_theta
            v_phi = radius * d_phi

            # Ángulo local de rumbo tangencial
            psi = np.arctan2(v_phi, v_theta)
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
