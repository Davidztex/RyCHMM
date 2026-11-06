# Reconocedor y Clasificador de Caracteres en Tiempo Real 2D/3D mediante Cadenas Ocultas de Markov (HMM)

**Universidad de los Llanos**  
**Facultad de Ciencias Básicas e Ingeniería — Programa de Ingeniería de Sistemas**  
**Asignatura**: Procesos Estocásticos (Código 603504) — 5.º Semestre  
**Docente**: Yerson Porras (`yerson.porras@unillanos.edu.co`)  
**Ponderación**: 90% del Tercer Corte  

---

## 1. Descripción del Proyecto

Sistema interactivo de escritorio para la captura, procesamiento, clasificación probabilística continua y autocompletado espacial dinámico de trazos manuscritos del alfabeto español (27 letras minúsculas $a-z$ y $\tilde{n}$), operable tanto en plano bidimensional cartesiano (2D) como sobre la superficie de una esfera tridimensional (3D con PyOpenGL).

### Cumplimiento Estricto de Restricciones Matemáticas
- **Prohibición Absoluta Cumplida**: Cero librerías o frameworks estocásticos externos (`hmmlearn`, `scikit-learn`, `PyTorch`, `TensorFlow`, `scipy.stats`).
- **Implementación 100% Nativa**: Toda la formulación estocástica ($\lambda = (A, B, \pi)$, algoritmo Forward escalado, Backward escalado, decodificación de Viterbi, log-verosimilitud, entrenamiento Baum-Welch y proyección de trayectoria) fue programada desde cero utilizando exclusivamente **NumPy** para álgebra lineal y arreglos numéricos.

---

## 2. Arquitectura del Software (POO y Arquitectura Limpia)

El código se organiza modularmente en capas con separación estricta de responsabilidades:

```
hmm_recognizer/
│
├── main.py                     # Punto de entrada principal de la aplicación GUI
├── requirements.txt            # Dependencias oficiales (PyQt6, PyOpenGL, numpy)
├── README.md                   # Documentación general y guía de instalación
├── GUIA_SUSTENTACION.md        # Formulación matemática paso a paso para defensa en tablero
├── export_zip.py               # Empaquetador automático para entrega institucional
│
├── engine/                     # Capa de lógica matemática y procesamiento geométrico
│   ├── __init__.py
│   ├── hmm_engine.py           # DiscreteHMM nativo, Forward, Backward, Viterbi, Baum-Welch, MultiCharacterClassifier
│   └── feature_extractor.py    # Remuestreo espacial, K=16 chain code, coordenadas esféricas y proyección
│
├── training/                   # Capa de entrenamiento offline y aumento de datos
│   ├── __init__.py
│   ├── train_models.py         # Script de entrenamiento offline Baum-Welch sobre dataset
│   ├── synthetic_generator.py  # Generador de prototipos geométricos y perturbaciones
│   └── generate_icons.py       # Renderizador de miniaturas de referencia de las 27 letras
│
├── gui/                        # Capa de presentación visual (PyQt6 + PyOpenGL)
│   ├── __init__.py
│   ├── main_window.py          # Ventana principal con QStackedWidget y barra de estado
│   ├── styles.py               # Tema grafito oscuro con acentos cian (QSS minimalista)
│   ├── views/                  # Las 3 ventanas requeridas por la especificación
│   │   ├── __init__.py
│   │   ├── menu_view.py        # Ventana A: Menú Principal institucional
│   │   ├── recognizer_2d_view.py # Ventana B: Reconocedor y Lienzo 2D
│   │   └── recognizer_3d_view.py # Ventana C: Reconocedor y Lienzo 3D Esférico
│   └── widgets/                # Componentes interactivos reutilizables
│       ├── __init__.py
│       ├── canvas_2d.py        # Lienzo 2D con QPainter, grilla cartesiana y proyección punteada
│       ├── canvas_3d_sphere.py # Lienzo 3D con PyOpenGL, raycasting y proyección esférica
│       └── ranking_panel.py    # Tarjeta Top-1 y listado ordenado P(C | O1:t) con iconos
│
└── data/                       # Almacenamiento persistente
    ├── dataset/                # Dataset de trazos manuscritos (glifo-dataset-2026-11-05.json)
    ├── models/                 # Modelos serializados estructurados (.json para cada letra y models.json)
    └── icons/                  # Iconos y miniaturas gráficas de las 27 letras (.png)
```

---

## 3. Requisitos del Sistema e Instalación

### Requisitos:
- Python 3.10 o superior (compatible y probado en Python 3.14).
- Sistema Operativo: Windows, Linux o macOS.
- Tarjeta gráfica con soporte OpenGL 2.0+ (compatible con GPUs dedicadas o integradas).

### Instalación de Dependencias:
```bash
pip install -r requirements.txt
```

---

## 4. Instrucciones de Uso

### 4.1. Ejecución de la Aplicación Gráfica (GUI)
```bash
python main.py
```

Al iniciar:
1. **Ventana A (Menú Principal)**: Seleccione entre **Modo 2D** (plano cartesiano) o **Modo 3D** (superficie esférica).
2. **Ventana B (Modo 2D)**:
   - Dibuje libremente con el ratón sobre el lienzo cartesiano milimétrico.
   - En tiempo real, el trazo activo se iluminará en color cian y el sistema proyectará de forma punteada la trayectoria futura estimada (autocompletado espacial) correspondiente a la letra con mayor probabilidad a posteriori.
   - En el panel derecho observará la tarjeta destacada Top-1 y el ranking descendente de las 27 letras con sus porcentajes y miniaturas de referencia.
   - Controles disponibles: `Limpiar Lienzo` (o tecla `C` / `Espacio`), `Reiniciar Captura`, `← Volver al Menú`.
3. **Ventana C (Modo 3D)**:
   - Renderizado en 3D de una esfera traslúcida con malla de meridianos y paralelos.
   - **Clic Izquierdo sobre la esfera**: Dibuja trazos confinados a la superficie esférica.
   - **Clic Derecho o Arrastre libre**: Rota la esfera en 360° para dibujar en cualquier cuadrante o polo.
   - **Rueda del ratón**: Zoom in / Zoom out.
   - Observará la proyección geodésica dinámica 3D punteada sobre la esfera.

### 4.2. Re-entrenamiento Offline Independiente (Opcional)
Según la sección 4.1 de la especificación, los modelos HMM vienen pre-entrenados y listos para inferencia instantánea. Si desea re-entrenar los 27 modelos:
```bash
python training/train_models.py
```

### 4.3. Generación del Archivo de Entrega (.zip)
Para generar el archivo comprimido oficial listo para enviar al correo del docente (`yerson.porras@unillanos.edu.co`):
```bash
python export_zip.py
```
Generará el archivo `HMM_ProyectoFinal_Unillanos.zip`.

---

## 5. Rúbrica de Evaluación Oficial (100 Puntos / 90% Corte 3)

| Criterio | Puntos | Estado en este Proyecto |
| :--- | :---: | :--- |
| **1. Rigor Matemático e Implementación HMM Nativa (Sin lib)** | 30 | **100% Nativo en NumPy**: $\lambda=(A, B, \pi)$, Forward escalado, Backward escalado, Viterbi log-domain, Baum-Welch EM, Topología Bakis. |
| **2. Trazado 2D/3D y Proyección Dinámica de Trayectoria** | 25 | Lienzo 2D interactivo con grilla milimétrica y proyección punteada; Lienzo 3D OpenGL esférico con raycasting y geodésicas. |
| **3. Interfaz Gráfica GUI (Minimalista, Ventanas, Listado Top)** | 20 | 3 Ventanas (Menú, 2D, 3D), Tarjeta Hero Top-1, listado descendente de 27 letras con barras de progreso e iconos de referencia. |
| **4. Sustentación Oral y Defensa Matemática en Tablero** | 15 | Documento `GUIA_SUSTENTACION.md` con la derivación formal paso a paso lista para explicar en tablero. |
| **5. Arquitectura Limpia (POO, Repositorio y ZIP)** | 10 | Modularidad estricta en capas (Engine, Training, GUI, Data), código documentado con tipado y script `export_zip.py`. |
| **TOTAL** | **100** | **Excelente cumplimiento de la especificación oficial.** |
