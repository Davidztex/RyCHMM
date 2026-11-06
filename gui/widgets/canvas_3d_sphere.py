"""
canvas_3d_sphere.py
===================
Lienzo tridimensional esférico interactivo implementado con QOpenGLWidget y PyOpenGL.
Soporta:
1. Renderizado 3D de una esfera traslúcida con malla de meridianos y paralelos.
2. Trazado continuo directo sobre la superficie esférica mediante raycasting euclidiano.
3. Rotación orbital en 360°, zoom suave y reorientación de la cámara.
4. Proyección dinámica 3D punteada/traslúcida de la trayectoria futura estimada sobre el cascarón esférico.
"""

import math
import numpy as np
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from OpenGL import GL, GLU


class Canvas3DSphere(QOpenGLWidget):
    """
    Widget OpenGL para interacción, dibujo y autocompletado sobre una esfera 3D.
    """

    # Señal emitida cuando el trazo 3D cambia: emite lista de puntos 3D [[x, y, z], ...]
    stroke_3d_updated = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        # Parámetros geométricos de la esfera
        self.radius = 1.0

        # Parámetros de la cámara orbital
        self.yaw = 0.0          # Rotación horizontal en grados
        self.pitch = 15.0       # Rotación vertical en grados (-85° a 85°)
        self.cam_distance = 2.8 # Distancia de la cámara al centro (zoom)

        # Estado del ratón
        self.last_mouse_pos = None
        self.is_drawing = False
        self.is_orbiting = False

        # Puntos 3D del trazo actual sobre la esfera: [[x, y, z], ...]
        self.stroke_points_3d = []
        self.all_completed_strokes_3d = []

        # Puntos 3D proyectados (autocompletado): [[x, y, z], ...]
        self.projected_trajectory_3d = []
        self.projected_char = ""
        self.projected_perc = ""

        # Punto 3D actual bajo el cursor (para indicador visual)
        self.hover_point_3d = None

    def clear_canvas(self):
        """Limpia los trazos y proyecciones de la esfera."""
        self.stroke_points_3d.clear()
        self.all_completed_strokes_3d.clear()
        self.projected_trajectory_3d.clear()
        self.projected_char = ""
        self.projected_perc = ""
        self.hover_point_3d = None
        self.update()
        self.stroke_3d_updated.emit([])

    def reset_view(self):
        """Restablece la orientación de la cámara al punto de vista canónico frontal."""
        self.yaw = 0.0
        self.pitch = 15.0
        self.cam_distance = 2.8
        self.update()

    def set_projection_3d(self, trajectory_3d, projected_char="", prob_perc=""):
        """Actualiza la trayectoria proyectada en 3D sobre la esfera."""
        self.projected_trajectory_3d = trajectory_3d or []
        self.projected_char = projected_char
        self.projected_perc = prob_perc
        self.update()

    # -------------------------------------------------------------
    # Ciclo de Vida OpenGL
    # -------------------------------------------------------------

    def initializeGL(self):
        GL.glClearColor(0.043, 0.067, 0.082, 1.0)  # Fondo grafito oscuro
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glDepthFunc(GL.GL_LEQUAL)

        # Habilitar canal alpha para transparencias de la esfera y líneas punteadas
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)

        # Suavizado de líneas
        GL.glEnable(GL.GL_LINE_SMOOTH)
        GL.glHint(GL.GL_LINE_SMOOTH_HINT, GL.GL_NICEST)

    def resizeGL(self, w, h):
        if h == 0:
            h = 1
        GL.glViewport(0, 0, w, h)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        aspect = w / float(h)
        GLU.gluPerspective(45.0, aspect, 0.1, 50.0)
        GL.glMatrixMode(GL.GL_MODELVIEW)

    def paintGL(self):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()

        # Posicionamiento de cámara orbital
        GL.glTranslatef(0.0, 0.0, -self.cam_distance)
        GL.glRotatef(self.pitch, 1.0, 0.0, 0.0)
        GL.glRotatef(self.yaw, 0.0, 1.0, 0.0)

        # 1. Dibujar esfera base y malla de meridianos/paralelos
        self._render_sphere_mesh()

        # 2. Dibujar trazos completados anteriores
        self._render_strokes_3d(self.all_completed_strokes_3d, color=(0.8, 0.85, 0.9, 0.9), line_width=3.0)

        # 3. Dibujar trazo activo actual
        if self.stroke_points_3d:
            self._render_single_stroke_3d(self.stroke_points_3d, color=(0.0, 0.85, 1.0, 1.0), line_width=4.0)

        # 4. Dibujar trayectoria dinámica proyectada (autocompletado 3D punteado)
        self._render_projected_trajectory_3d()

        # 5. Indicador del cursor sobre la superficie esférica
        if self.hover_point_3d is not None:
            self._render_hover_point()

    # -------------------------------------------------------------
    # Renderizado de Primitivas 3D
    # -------------------------------------------------------------

    def _render_sphere_mesh(self):
        """Renderiza los meridianos y paralelos de la esfera alámbrica traslúcida."""
        R = self.radius

        # Cascarón esférico sutilmente oscurecido para dar solidez
        GL.glColor4f(0.08, 0.11, 0.16, 0.5)
        quadric = GLU.gluNewQuadric()
        GLU.gluQuadricDrawStyle(quadric, GLU.GLU_FILL)
        GLU.gluSphere(quadric, R * 0.995, 32, 24)
        GLU.gluDeleteQuadric(quadric)

        # Paralelos (círculos de latitud cada 15 grados)
        GL.glLineWidth(1.0)
        for lat_deg in range(-75, 76, 15):
            lat_rad = math.radians(lat_deg)
            r_slice = R * math.cos(lat_rad)
            z_slice = R * math.sin(lat_rad)

            if lat_deg == 0:
                GL.glColor4f(0.25, 0.45, 0.65, 0.6)  # Ecuador resaltado
                GL.glLineWidth(1.5)
            else:
                GL.glColor4f(0.15, 0.22, 0.32, 0.35)
                GL.glLineWidth(1.0)

            GL.glBegin(GL.GL_LINE_LOOP)
            for seg in range(48):
                ang = 2.0 * math.pi * seg / 48.0
                GL.glVertex3f(r_slice * math.cos(ang), z_slice, r_slice * math.sin(ang))
            GL.glEnd()

        # Meridianos (círculos de longitud cada 30 grados)
        for lon_deg in range(0, 180, 30):
            lon_rad = math.radians(lon_deg)
            if lon_deg == 0:
                GL.glColor4f(0.25, 0.45, 0.65, 0.6)
                GL.glLineWidth(1.5)
            else:
                GL.glColor4f(0.15, 0.22, 0.32, 0.35)
                GL.glLineWidth(1.0)

            GL.glBegin(GL.GL_LINE_LOOP)
            for seg in range(48):
                ang = 2.0 * math.pi * seg / 48.0
                x = R * math.cos(ang) * math.cos(lon_rad)
                z = R * math.sin(ang)
                y = R * math.cos(ang) * math.sin(lon_rad)
                GL.glVertex3f(x, z, y)
            GL.glEnd()

    def _render_single_stroke_3d(self, pts, color, line_width):
        """Renderiza una polilínea 3D directamente sobre la superficie de la esfera."""
        if len(pts) < 2:
            return

        GL.glLineWidth(line_width)
        GL.glColor4f(*color)

        # Elevar ligeramente para evitar z-fighting con la malla esférica
        scale = 1.004

        GL.glBegin(GL.GL_LINE_STRIP)
        for p in pts:
            GL.glVertex3f(p[0] * scale, p[1] * scale, p[2] * scale)
        GL.glEnd()

        # Dibujar punto inicial y final
        GL.glPointSize(6.0)
        GL.glBegin(GL.GL_POINTS)
        p_last = pts[-1]
        GL.glVertex3f(p_last[0] * scale, p_last[1] * scale, p_last[2] * scale)
        GL.glEnd()

    def _render_strokes_3d(self, stroke_list, color, line_width):
        for st in stroke_list:
            self._render_single_stroke_3d(st, color, line_width)

    def _render_projected_trajectory_3d(self):
        """Renderiza la proyección futura 3D con línea punteada ámbar sobre la esfera."""
        if len(self.projected_trajectory_3d) < 2:
            return

        scale = 1.006  # Ligeramente por encima del trazo
        GL.glLineWidth(3.0)
        GL.glColor4f(1.0, 0.72, 0.05, 0.95)  # Ámbar brillante

        # Habilitar estriado para punteado en OpenGL clásico
        GL.glEnable(GL.GL_LINE_STIPPLE)
        GL.glLineStipple(2, 0x0F0F)

        GL.glBegin(GL.GL_LINE_STRIP)
        for p in self.projected_trajectory_3d:
            GL.glVertex3f(p[0] * scale, p[1] * scale, p[2] * scale)
        GL.glEnd()

        GL.glDisable(GL.GL_LINE_STIPPLE)

        # Marcadores de hitos en la trayectoria proyectada
        GL.glPointSize(4.5)
        GL.glColor4f(1.0, 0.75, 0.1, 0.8)
        GL.glBegin(GL.GL_POINTS)
        for p in self.projected_trajectory_3d[::2]:
            GL.glVertex3f(p[0] * scale, p[1] * scale, p[2] * scale)
        GL.glEnd()

    def _render_hover_point(self):
        """Renderiza un anillo brillante en el punto de contacto del cursor sobre la esfera."""
        p = self.hover_point_3d
        GL.glPointSize(8.0)
        GL.glColor4f(0.0, 0.85, 1.0, 0.7)
        GL.glBegin(GL.GL_POINTS)
        GL.glVertex3f(p[0] * 1.008, p[1] * 1.008, p[2] * 1.008)
        GL.glEnd()

    # -------------------------------------------------------------
    # Raycasting: Intersección Pantalla 2D -> Cascarón Esférico 3D
    # -------------------------------------------------------------

    def _screen_to_sphere_raycast(self, mouse_x, mouse_y):
        """
        Calcula la intersección del rayo que sale de la cámara con la esfera x^2 + y^2 + z^2 = R^2.
        Retorna [x, y, z] sobre la superficie o None si el rayo no toca la esfera.
        """
        w = max(self.width(), 1)
        h = max(self.height(), 1)

        # Coordenadas de dispositivo normalizadas (NDC) [-1, 1]
        ndc_x = (2.0 * mouse_x) / w - 1.0
        ndc_y = 1.0 - (2.0 * mouse_y) / h

        aspect = w / float(h)
        fov_rad = math.radians(45.0)
        tan_half_fov = math.tan(fov_rad / 2.0)

        # Vector de dirección en el espacio de la cámara
        dir_cam = np.array([
            ndc_x * aspect * tan_half_fov,
            ndc_y * tan_half_fov,
            -1.0
        ], dtype=np.float64)
        dir_cam /= np.linalg.norm(dir_cam)

        # Transformar origen y dirección a coordenadas del mundo mediante rotación inversa de la cámara
        rad_pitch = math.radians(self.pitch)
        rad_yaw = math.radians(self.yaw)

        # Matriz de rotación Rx(pitch) * Ry(yaw)
        cos_p, sin_p = math.cos(rad_pitch), math.sin(rad_pitch)
        cos_y, sin_y = math.cos(rad_yaw), math.sin(rad_yaw)

        # Origen de la cámara en el espacio del objeto
        # La cámara mira a (0,0,0) desde distancia cam_distance a lo largo del eje Z transformado
        cam_pos_world = np.array([
            self.cam_distance * sin_y * cos_p,
            -self.cam_distance * sin_p,
            self.cam_distance * cos_y * cos_p
        ], dtype=np.float64)

        # Rotar vector de dirección al espacio del mundo
        # Primero por pitch (eje X) luego yaw (eje Y)
        # Inversa: Ry(-yaw) * Rx(-pitch) en sentido opuesto
        dx_p = dir_cam[0]
        dy_p = dir_cam[1] * cos_p - dir_cam[2] * sin_p
        dz_p = dir_cam[1] * sin_p + dir_cam[2] * cos_p

        dx_w = dx_p * cos_y - dz_p * sin_y
        dy_w = dy_p
        dz_w = dx_p * sin_y + dz_p * cos_y

        ray_dir_world = np.array([dx_w, dy_w, dz_w], dtype=np.float64)
        ray_dir_world /= np.linalg.norm(ray_dir_world)

        # Intersección Rayo - Esfera: ||cam_pos + t * ray_dir||^2 = R^2
        # a*t^2 + b*t + c = 0 donde a = 1
        b = 2.0 * np.dot(cam_pos_world, ray_dir_world)
        c = np.dot(cam_pos_world, cam_pos_world) - self.radius * self.radius

        discriminant = b * b - 4.0 * c
        if discriminant < 0.0:
            return None  # El rayo no intersecta la esfera

        t = (-b - math.sqrt(discriminant)) / 2.0
        if t < 0.0:
            return None

        hit_point = cam_pos_world + t * ray_dir_world
        # Re-normalizar al radio exacto
        hit_point = hit_point / np.linalg.norm(hit_point) * self.radius
        return hit_point.tolist()

    # -------------------------------------------------------------
    # Eventos de Interacción de Usuario
    # -------------------------------------------------------------

    def mousePressEvent(self, event):
        self.last_mouse_pos = event.position()

        if event.button() == Qt.MouseButton.LeftButton:
            # Comprobar si se hace clic sobre la esfera para dibujar
            hit = self._screen_to_sphere_raycast(event.position().x(), event.position().y())
            if hit is not None:
                self.is_drawing = True
                self.stroke_points_3d = [hit]
                self.hover_point_3d = hit
                self.update()
                self.stroke_3d_updated.emit(self.stroke_points_3d)
            else:
                # Si hace clic fuera de la esfera, permite orbitar
                self.is_orbiting = True

        elif event.button() in (Qt.MouseButton.RightButton, Qt.MouseButton.MiddleButton):
            self.is_orbiting = True

    def mouseMoveEvent(self, event):
        pos = event.position()

        # Actualizar hover point si no está dibujando
        if not self.is_drawing:
            self.hover_point_3d = self._screen_to_sphere_raycast(pos.x(), pos.y())
            self.update()

        if self.is_drawing:
            hit = self._screen_to_sphere_raycast(pos.x(), pos.y())
            if hit is not None:
                # Comprobar distancia mínima con el punto anterior para no saturar
                if self.stroke_points_3d:
                    p_last = np.array(self.stroke_points_3d[-1])
                    dist = np.linalg.norm(np.array(hit) - p_last)
                    if dist >= 0.015:  # Paso espacial mínimo
                        self.stroke_points_3d.append(hit)
                        self.hover_point_3d = hit
                        self.update()
                        self.stroke_3d_updated.emit(self.stroke_points_3d)
                else:
                    self.stroke_points_3d.append(hit)
                    self.update()

        elif self.is_orbiting and self.last_mouse_pos:
            dx = pos.x() - self.last_mouse_pos.x()
            dy = pos.y() - self.last_mouse_pos.y()
            self.yaw += dx * 0.5
            self.pitch = max(-85.0, min(85.0, self.pitch + dy * 0.5))
            self.update()

        self.last_mouse_pos = pos

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.is_drawing:
            self.is_drawing = False
            if len(self.stroke_points_3d) >= 2:
                self.all_completed_strokes_3d.append(list(self.stroke_points_3d))
            self.stroke_points_3d = []
            self.update()

        if event.button() in (Qt.MouseButton.LeftButton, Qt.MouseButton.RightButton, Qt.MouseButton.MiddleButton):
            self.is_orbiting = False

    def wheelEvent(self, event):
        # Control suave de zoom
        delta = event.angleDelta().y()
        if delta > 0:
            self.cam_distance = max(1.4, self.cam_distance - 0.15)
        elif delta < 0:
            self.cam_distance = min(5.0, self.cam_distance + 0.15)
        self.update()
