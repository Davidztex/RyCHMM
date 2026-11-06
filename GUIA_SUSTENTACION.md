# Guía Matemática para la Sustentación Oral en Tablero
## Universidad de los Llanos — Procesos Estocásticos (603504)
### Proyecto Final: Reconocedor y Clasificador HMM 2D/3D (90% Tercer Corte)

Esta guía contiene la derivación formal paso a paso de las ecuaciones implementadas nativamente en el proyecto (sin librerías estocásticas externas), requeridas para la **Defensa Matemática en Tablero (15 Puntos / 13.5% del corte)**.

---

## 1. Definición Formal de la Cadena Oculta de Markov $\lambda_c = (A_c, B_c, \pi_c)$

Para cada letra $c \in \{a, b, c, \dots, z, \tilde{n}\}$ (27 caracteres) se define un HMM independiente:

1. **Espacio de Estados Ocultos ($S$)**:
   $$S = \{S_1, S_2, \dots, S_N\}, \quad N = 6 \text{ fases latentes del trazo}$$
   Representa las fases secuenciales no observables en la construcción del carácter.

2. **Alfabeto de Observaciones ($V$)**:
   $$V = \{v_0, v_1, \dots, v_{K-1}\}, \quad K = 16 \text{ sectores angulares } (22.5^\circ \text{ por sector})$$
   Cada sector corresponde a la discretización del ángulo de desplazamiento $\theta$:
   $$O_t = \left\lfloor \frac{\theta + \frac{\pi}{16}}{\frac{2\pi}{16}} \right\rfloor \pmod{16}$$

3. **Distribución Inicial de Estados ($\pi$)**:
   $$\pi_i = P(q_1 = S_i) = \begin{cases} 1.0 & \text{si } i = 1 \\ 0.0 & \text{si } i > 1 \end{cases}$$
   Todo trazo comienza obligatoriamente en la fase inicial $S_1$.

4. **Matriz de Transición de Estados ($A \in \mathbb{R}^{N \times N}$)**:
   $$a_{ij} = P(q_{t+1} = S_j \mid q_t = S_i), \quad \sum_{j=1}^N a_{ij} = 1$$
   **Topología Left-to-Right (Bakis)**: Prohíbe retrocesos temporales:
   $$a_{ij} = 0 \quad \forall j < i \quad \text{y} \quad \forall j > i + 2$$
   Permite permanecer en la fase actual ($a_{ii}$), avanzar a la siguiente ($a_{i, i+1}$) o realizar un salto suave ($a_{i, i+2}$).

5. **Matriz de Emisión de Observaciones ($B \in \mathbb{R}^{N \times K}$)**:
   $$b_j(k) = P(O_t = v_k \mid q_t = S_j), \quad \sum_{k=0}^{K-1} b_j(k) = 1$$
   Probabilidad de emitir la dirección $k$ cuando el trazo se encuentra en la fase latente $S_j$.

---

## 2. Problema de Evaluación: Algoritmo Forward Escalado ($\alpha_t(i)$)

Para evaluar en tiempo real la verosimilitud de la secuencia parcial observada $O_{1:t} = (O_1, O_2, \dots, O_t)$ sin sufrir *underflow* numérico:

### Paso 1: Inicialización ($t = 1$)
$$\alpha_1(i) = \pi_i \cdot b_i(O_1), \quad 1 \le i \le N$$
Factor de normalización:
$$c_1 = \frac{1}{\sum_{i=1}^N \alpha_1(i)}$$
Variable escalada:
$$\hat{\alpha}_1(i) = c_1 \cdot \alpha_1(i), \quad \text{donde } \sum_{i=1}^N \hat{\alpha}_1(i) = 1$$

### Paso 2: Inducción ($1 < \tau \le t$)
Para cada estado $j \in \{1, \dots, N\}$:
$$\alpha_\tau(j) = \left[ \sum_{i=1}^N \hat{\alpha}_{\tau-1}(i) \cdot a_{ij} \right] b_j(O_\tau)$$
Factor de normalización en el instante $\tau$:
$$c_\tau = \frac{1}{\sum_{j=1}^N \alpha_\tau(j)}$$
Variable escalada:
$$\hat{\alpha}_\tau(j) = c_\tau \cdot \alpha_\tau(j)$$

### Paso 3: Log-Verosimilitud Total
Por la propiedad matemática del producto de factores de escala:
$$P(O_{1:t} \mid \lambda) = \prod_{\tau=1}^t \frac{1}{c_\tau} \implies \ln P(O_{1:t} \mid \lambda) = -\sum_{\tau=1}^t \ln(c_\tau)$$

---

## 3. Clasificación Probabilística Softmax

Dadas las 27 log-verosimilitudes $\{\ln P(O_{1:t} \mid \lambda_c)\}_{c \in \mathcal{C}}$, se calcula la distribución de probabilidad a posteriori mediante Softmax centrado:

$$P(c \mid O_{1:t}) = \frac{\exp\Big(\ln P(O_{1:t} \mid \lambda_c) - \max_k \ln P(O_{1:t} \mid \lambda_k)\Big)}{\sum_{c' \in \mathcal{C}} \exp\Big(\ln P(O_{1:t} \mid \lambda_{c'}) - \max_k \ln P(O_{1:t} \mid \lambda_k)\Big)}$$

- **Propiedades**:
  1. $0.0 \le P(c \mid O_{1:t}) \le 1.0$
  2. $\sum_{c \in \mathcal{C}} P(c \mid O_{1:t}) = 1.0$
  3. La resta de $\max_k \ln P$ previene cualquier desbordamiento exponencial (*overflow*).

---

## 4. Problema de Decodificación: Algoritmo de Viterbi

Determina la secuencia óptima de estados ocultos $q_{1:t}^* = \arg\max_{q} P(q, O_{1:t} \mid \lambda)$.
Se computa en el dominio logarítmico:

### Paso 1: Inicialización ($t = 1$)
$$\delta_1(i) = \ln \pi_i + \ln b_i(O_1), \quad \psi_1(i) = 0$$

### Paso 2: Recursión ($1 < \tau \le t$)
$$\delta_\tau(j) = \max_{1 \le i \le N} \Big[ \delta_{\tau-1}(i) + \ln a_{ij} \Big] + \ln b_j(O_\tau)$$
$$\psi_\tau(j) = \arg\max_{1 \le i \le N} \Big[ \delta_{\tau-1}(i) + \ln a_{ij} \Big]$$

### Paso 3: Terminación y Reconstrucción (Backtracking)
$$q_t^* = \arg\max_{1 \le i \le N} \delta_t(i)$$
Para $\tau = t-1, t-2, \dots, 1$:
$$q_\tau^* = \psi_{\tau+1}(q_{\tau+1}^*)$$

---

## 5. Proyección Dinámica de Trayectoria (Autocompletado Espacial)

1. Se selecciona el carácter ganador:
   $$\hat{c} = \arg\max_{c \in \mathcal{C}} P(c \mid O_{1:t})$$

2. Se identifica el estado actual $q_t^*$ mediante Viterbi.

3. Para las fases restantes $\tau = t+1, \dots, T$, se proyecta la observación más probable emitida en cada fase:
   $$O_\tau^* = \arg\max_{0 \le k < 16} b_{q_\tau}(k)$$

4. **Reconstrucción Cartesiana 2D**:
   Partiendo de la posición actual del cursor $(x_t, y_t)$ y paso espacial $\Delta s$:
   $$x_\tau = x_{\tau-1} + \Delta s \cos\left( \frac{2\pi \cdot O_\tau^*}{16} \right)$$
   $$y_\tau = y_{\tau-1} + \Delta s \sin\left( \frac{2\pi \cdot O_\tau^*}{16} \right)$$

5. **Reconstrucción Geodésica 3D (Superficie Esférica)**:
   Partiendo de las coordenadas angulares actuales $(\theta_t, \phi_t)$ sobre la esfera de radio $R$:
   $$\Delta\sigma = \frac{\Delta s}{R}, \quad \psi_\tau = \frac{2\pi \cdot O_\tau^*}{16}$$
   $$\phi_\tau = \phi_{\tau-1} + \Delta\sigma \sin(\psi_\tau)$$
   $$\theta_\tau = \theta_{\tau-1} + \frac{\Delta\sigma \cos(\psi_\tau)}{\sin\phi_{\tau-1}}$$
   Coordenadas en $\mathbb{R}^3$:
   $$x_\tau = R \sin\phi_\tau \cos\theta_\tau, \quad y_\tau = R \sin\phi_\tau \sin\theta_\tau, \quad z_\tau = R \cos\phi_\tau$$

---

## 6. Algoritmo de Baum-Welch (Paso E y Paso M para Entrenamiento Offline)

Para un conjunto de secuencias de entrenamiento $\{O^{(d)}\}_{d=1}^D$:

### Probabilidad Posterior de Estado ($\gamma_\tau(i)$):
$$\gamma_\tau(i) = P(q_\tau = S_i \mid O, \lambda) = \frac{\hat{\alpha}_\tau(i) \hat{\beta}_\tau(i)}{\sum_{j=1}^N \hat{\alpha}_\tau(j) \hat{\beta}_\tau(j)}$$

### Probabilidad Posterior de Transición ($\xi_\tau(i, j)$):
$$\xi_\tau(i, j) = P(q_\tau = S_i, q_{\tau+1} = S_j \mid O, \lambda) = \frac{\hat{\alpha}_\tau(i) a_{ij} b_j(O_{\tau+1}) \hat{\beta}_{\tau+1}(j)}{\sum_{k=1}^N \sum_{m=1}^N \hat{\alpha}_\tau(k) a_{km} b_m(O_{\tau+1}) \hat{\beta}_{\tau+1}(m)}$$

### Fórmulas de Re-estimación (Paso M):
$$\bar{a}_{ij} = \frac{\sum_{d=1}^D \sum_{\tau=1}^{T_d-1} \xi_\tau^{(d)}(i, j)}{\sum_{d=1}^D \sum_{\tau=1}^{T_d-1} \gamma_\tau^{(d)}(i)}$$

$$\bar{b}_j(k) = \frac{\sum_{d=1}^D \sum_{\tau: O_\tau^{(d)} = v_k} \gamma_\tau^{(d)}(j) + \epsilon}{\sum_{d=1}^D \sum_{\tau=1}^{T_d} \gamma_\tau^{(d)}(j) + K \cdot \epsilon} \quad (\text{Suavizado de Laplace } \epsilon > 0)$$
