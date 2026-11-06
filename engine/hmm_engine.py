"""
HMMEngine.py
============
Módulo matemático con la implementación pura y nativa de Cadenas Ocultas de Markov (HMM).
Cumple con la restricción estricta del proyecto:

Contenido:
- DiscreteHMM: Modelo HMM discreto con topología Left-to-Right (Bakis), algoritmos Forward escalado,
  Backward escalado, Decodificación de Viterbi, entrenamiento Baum-Welch (EM) y proyección estocástica.
- MultiCharacterClassifier: Administrador de los 27 modelos HMM del alfabeto español (incluyendo la 'ñ'),
  cálculo de probabilidades posteriores P(c | O_1:t) mediante Softmax logarítmico y autocompletado espacial.
"""

import json
import os
import numpy as np

# 27 letras del alfabeto español en minúscula
SPANISH_ALPHABET = [
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
    'n', 'ñ', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z'
]


class DiscreteHMM:
    """
    Modelo Oculto de Markov Discreto lambda = (A, B, pi) implementado desde cero.
    
    Parámetros:
    -----------
    n_states : int
        Número de estados ocultos latentes N (fases secuenciales del trazo). Por defecto 6.
    n_obs : int
        Cardinalidad del alfabeto de observaciones K (sectores angulares). Por defecto 16.
    char_label : str
        Carácter asignado a este modelo (ej. 'a', 'ñ').
    """

    def __init__(self, n_states=6, n_obs=16, char_label="?"):
        self.N = n_states
        self.K = n_obs
        self.char_label = char_label

        # Vector de probabilidades iniciales pi: Trazo siempre inicia en estado S_0
        self.pi = np.zeros(self.N, dtype=np.float64)
        self.pi[0] = 1.0

        # Matriz de transición A: Topología Left-to-Right (Bakis)
        # Permite auto-transición (i -> i), avance inmediato (i -> i+1) y salto suave (i -> i+2)
        self.A = np.zeros((self.N, self.N), dtype=np.float64)
        for i in range(self.N):
            if i == self.N - 1:
                self.A[i, i] = 1.0
            elif i == self.N - 2:
                self.A[i, i] = 0.50
                self.A[i, i + 1] = 0.50
            else:
                self.A[i, i] = 0.45
                self.A[i, i + 1] = 0.40
                self.A[i, i + 2] = 0.15

        # Matriz de emisión B: P(O_t = v_k | q_t = S_j)
        # Inicialización uniforme con pequeña regularización
        self.B = np.ones((self.N, self.K), dtype=np.float64) / self.K

        # Prototipo canónico para autocompletado y renderizado geométrico
        self.canonical_points = []   # Lista de puntos normalizados [[x, y], ...]
        self.canonical_symbols = []  # Lista de símbolos discretos [s0, s1, ...]

    def forward(self, O):
        """
        Algoritmo Forward escalado para evaluación de verosimilitud en tiempo real.
        
        Ecuaciones:
        -----------
        1. Inicialización (t = 1):
           alpha_1(i) = pi_i * b_i(O_1)
           c_1 = 1 / sum_i(alpha_1(i))
           hat{alpha}_1(i) = c_1 * alpha_1(i)
           
        2. Inducción (1 < t <= T):
           alpha_t(j) = [sum_i hat{alpha}_{t-1}(i) * a_{ij}] * b_j(O_t)
           c_t = 1 / sum_j(alpha_t(j))
           hat{alpha}_t(j) = c_t * alpha_t(j)
           
        3. Log-Verosimilitud:
           ln P(O_{1:T} | lambda) = -sum_{t=1}^T ln(c_t)
           
        Retorna:
        --------
        log_lik : float (log-verosimilitud)
        alpha_hat : np.ndarray de dimensión (T, N)
        c : np.ndarray de dimensión (T,) (factores de escala)
        """
        T = len(O)
        if T == 0:
            return -1e12, np.zeros((0, self.N), dtype=np.float64), np.zeros(0, dtype=np.float64)

        alpha_hat = np.zeros((T, self.N), dtype=np.float64)
        c = np.zeros(T, dtype=np.float64)

        # Paso 1: Inicialización
        o0 = int(O[0])
        alpha_raw_0 = self.pi * self.B[:, o0]
        sum_alpha_0 = np.sum(alpha_raw_0)
        c[0] = 1.0 / max(sum_alpha_0, 1e-12)
        alpha_hat[0] = alpha_raw_0 * c[0]

        # Paso 2: Inducción temporal
        for t in range(1, T):
            ot = int(O[t])
            # sum_i hat{alpha}_{t-1}(i) * a_{ij}
            pred = np.dot(alpha_hat[t - 1], self.A)
            alpha_raw_t = pred * self.B[:, ot]
            sum_alpha_t = np.sum(alpha_raw_t)
            c[t] = 1.0 / max(sum_alpha_t, 1e-12)
            alpha_hat[t] = alpha_raw_t * c[t]

        # Paso 3: Log-verosimilitud
        # ln P(O|lambda) = - sum ln(c_t)
        log_lik = -np.sum(np.log(c))
        return float(log_lik), alpha_hat, c

    def backward(self, O, c):
        """
        Algoritmo Backward escalado para el paso E de Baum-Welch.
        
        Ecuaciones:
        -----------
        1. Inicialización (t = T):
           hat{beta}_T(i) = c_T * 1
           
        2. Inducción (T-1 >= t >= 1):
           beta_t(i) = sum_j a_{ij} * b_j(O_{t+1}) * hat{beta}_{t+1}(j)
           hat{beta}_t(i) = c_t * beta_t(i)
        """
        T = len(O)
        beta_hat = np.zeros((T, self.N), dtype=np.float64)
        if T == 0:
            return beta_hat

        # Inicialización
        beta_hat[T - 1] = c[T - 1]

        # Inducción regresiva
        for t in range(T - 2, -1, -1):
            ot_plus_1 = int(O[t + 1])
            term = self.B[:, ot_plus_1] * beta_hat[t + 1]
            beta_raw_t = np.dot(self.A, term)
            beta_hat[t] = beta_raw_t * c[t]

        return beta_hat

    def viterbi(self, O):
        """
        Algoritmo de Viterbi en el dominio logarítmico para evitar underflow numérico.
        Determina la secuencia óptima de estados latentes q_1^*, ..., q_T^*.
        
        Ecuaciones:
        -----------
        delta_1(i) = ln pi_i + ln b_i(O_1)
        delta_t(j) = max_i [delta_{t-1}(i) + ln a_{ij}] + ln b_j(O_t)
        psi_t(j)   = argmax_i [delta_{t-1}(i) + ln a_{ij}]
        """
        T = len(O)
        if T == 0:
            return -1e12, []

        log_pi = np.log(np.maximum(self.pi, 1e-12))
        log_A = np.log(np.maximum(self.A, 1e-12))
        log_B = np.log(np.maximum(self.B, 1e-12))

        delta = np.zeros((T, self.N), dtype=np.float64)
        psi = np.zeros((T, self.N), dtype=np.int32)

        # Paso 1: Inicialización
        o0 = int(O[0])
        delta[0] = log_pi + log_B[:, o0]

        # Paso 2: Recursión
        for t in range(1, T):
            ot = int(O[t])
            for j in range(self.N):
                trans_scores = delta[t - 1] + log_A[:, j]
                best_prev = int(np.argmax(trans_scores))
                delta[t, j] = trans_scores[best_prev] + log_B[j, ot]
                psi[t, j] = best_prev

        # Paso 3: Terminación y Backtracking
        best_last_state = int(np.argmax(delta[T - 1]))
        best_log_prob = float(delta[T - 1, best_last_state])

        best_path = [0] * T
        best_path[T - 1] = best_last_state
        for t in range(T - 2, -1, -1):
            best_path[t] = int(psi[t + 1, best_path[t + 1]])

        return best_log_prob, best_path

    def train_baum_welch(self, sequences, max_iter=20, tol=1e-3):
        """
        Entrenamiento nativo offline mediante algoritmo de Baum-Welch (EM) multi-secuencia.
        
        Parámetros:
        -----------
        sequences : list of lists
            Lista de secuencias discretas de entrenamiento {O^(d)}.
        max_iter : int
            Máximo número de iteraciones EM.
        tol : float
            Tolerancia de cambio en log-verosimilitud para convergencia.
        """
        valid_seqs = [s for s in sequences if len(s) >= 2]
        if not valid_seqs:
            return

        # 1. Inicialización guiada de emisiones basada en progreso secuencial
        B_counts = np.ones((self.N, self.K), dtype=np.float64) * 0.1
        for seq in valid_seqs:
            L = len(seq)
            for idx, symbol in enumerate(seq):
                state_idx = min(self.N - 1, int(idx / L * self.N))
                B_counts[state_idx, int(symbol)] += 1.0
        self.B = B_counts / np.sum(B_counts, axis=1, keepdims=True)

        prev_total_lik = -np.inf
        bakis_mask = (self.A > 0)

        for iteration in range(max_iter):
            # Acumuladores del paso M
            A_num = np.zeros_like(self.A)
            A_den = np.zeros(self.N, dtype=np.float64)
            B_num = np.ones_like(self.B) * 0.05  # Suavizado de Laplace
            B_den = np.ones(self.N, dtype=np.float64) * (0.05 * self.K)

            total_lik = 0.0

            # Paso E: Expectation sobre cada secuencia
            for O in valid_seqs:
                T = len(O)
                log_lik, alpha_hat, c = self.forward(O)
                total_lik += log_lik
                beta_hat = self.backward(O, c)

                # gamma_t(i) = hat{alpha}_t(i) * hat{beta}_t(i) / c_t
                # Debido a la escala hat{alpha} * hat{beta} suma c_t, se normaliza por fila:
                gamma = alpha_hat * beta_hat
                row_sums = np.sum(gamma, axis=1, keepdims=True)
                row_sums[row_sums == 0] = 1.0
                gamma = gamma / row_sums

                # xi_t(i, j) = hat{alpha}_t(i) * a_{ij} * b_j(O_{t+1}) * hat{beta}_{t+1}(j)
                for t in range(T - 1):
                    ot_plus_1 = int(O[t + 1])
                    xi_t = self.A * np.outer(alpha_hat[t], self.B[:, ot_plus_1] * beta_hat[t + 1])
                    sum_xi = np.sum(xi_t)
                    if sum_xi > 0:
                        xi_t /= sum_xi
                    A_num += xi_t
                    A_den += gamma[t]

                for t in range(T):
                    ot = int(O[t])
                    B_num[:, ot] += gamma[t]
                    B_den += gamma[t]

            # Paso M: Maximización y actualización de A y B
            # Actualizar A respetando máscara Bakis
            for i in range(self.N):
                denom = A_den[i]
                if denom > 1e-6:
                    for j in range(self.N):
                        if bakis_mask[i, j]:
                            self.A[i, j] = A_num[i, j] / denom
                row_total = np.sum(self.A[i] * bakis_mask[i])
                if row_total > 0:
                    self.A[i] = (self.A[i] * bakis_mask[i]) / row_total
                else:
                    self.A[i, i] = 1.0

            # Actualizar B con suavizado
            for i in range(self.N):
                self.B[i] = B_num[i] / B_den[i]

            # Criterio de convergencia
            diff = total_lik - prev_total_lik
            if iteration > 0 and 0 <= diff < tol:
                break
            prev_total_lik = total_lik

    def predict_future_symbols(self, current_obs, horizon=15):
        """
        Extrapola los símbolos estocásticos futuros esperados {O_{t+1}, ..., O_{t+H}}
        a partir del estado latente actual decodificado mediante Viterbi.
        """
        T = len(current_obs)
        if T == 0:
            current_state = 0
        else:
            _, path = self.viterbi(current_obs)
            current_state = path[-1] if path else 0

        predicted_symbols = []
        state = current_state

        for _ in range(horizon):
            # En el estado actual, el símbolo más probable es argmax_k B_state(k)
            best_symbol = int(np.argmax(self.B[state]))
            predicted_symbols.append(best_symbol)

            # Transición más probable al siguiente estado
            # Preferir avance secuencial si aún no se ha llegado al estado final
            if state < self.N - 1:
                # Transición ponderada o hacia adelante
                next_state_candidates = self.A[state].copy()
                next_state = int(np.argmax(next_state_candidates))
                state = next_state
            else:
                state = self.N - 1

        return predicted_symbols

    def to_dict(self):
        """Serializa el modelo a un diccionario nativo para exportación JSON."""
        return {
            "char_label": self.char_label,
            "N": int(self.N),
            "K": int(self.K),
            "pi": self.pi.tolist(),
            "A": self.A.tolist(),
            "B": self.B.tolist(),
            "canonical_points": self.canonical_points,
            "canonical_symbols": self.canonical_symbols
        }

    @classmethod
    def from_dict(cls, data):
        """Deserializa un modelo DiscreteHMM a partir de un diccionario."""
        hmm = cls(n_states=data["N"], n_obs=data["K"], char_label=data["char_label"])
        hmm.pi = np.array(data["pi"], dtype=np.float64)
        hmm.A = np.array(data["A"], dtype=np.float64)
        hmm.B = np.array(data["B"], dtype=np.float64)
        hmm.canonical_points = data.get("canonical_points", [])
        hmm.canonical_symbols = data.get("canonical_symbols", [])
        return hmm

    def save_json(self, filepath):
        """Guarda el modelo en un archivo JSON estructurado."""
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    @classmethod
    def load_json(cls, filepath):
        """Carga un modelo DiscreteHMM desde un archivo JSON."""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)


class MultiCharacterClassifier:
    """
    Clasificador multiclase que administra los 27 modelos HMM independientes lambda_c.
    Calcula verosimilitud en tiempo real, normalización Softmax para probabilidades posteriores,
    ranking ordenado y autocompletado de trayectoria.
    """

    def __init__(self, alphabet=None):
        self.alphabet = alphabet or SPANISH_ALPHABET
        self.models = {}  # char -> DiscreteHMM

    def add_model(self, model):
        """Registra un modelo HMM para su carácter correspondiente."""
        self.models[model.char_label] = model

    def load_models_from_dir(self, models_dir):
        """Carga todos los modelos individuales .json o el consolidado models.json."""
        consolidated_path = os.path.join(models_dir, "models.json")
        loaded_count = 0

        if os.path.exists(consolidated_path):
            with open(consolidated_path, "r", encoding="utf-8") as f:
                all_data = json.load(f)
            for ch, data in all_data.items():
                self.models[ch] = DiscreteHMM.from_dict(data)
                loaded_count += 1
            return loaded_count

        for ch in self.alphabet:
            # Soportar nombres seguros de archivo para la 'ñ'
            filenames = [f"{ch}.json", f"char_{ord(ch)}.json"]
            if ch == 'ñ':
                filenames.insert(0, "nn.json")

            for fn in filenames:
                p = os.path.join(models_dir, fn)
                if os.path.exists(p):
                    self.models[ch] = DiscreteHMM.load_json(p)
                    loaded_count += 1
                    break

        return loaded_count

    def save_all_models(self, models_dir):
        """Exporta todos los modelos a archivos individuales y al archivo consolidado."""
        os.makedirs(models_dir, exist_ok=True)
        consolidated = {}
        for ch, model in self.models.items():
            consolidated[ch] = model.to_dict()
            safe_name = f"char_{ord(ch)}.json" if ord(ch) > 127 else f"{ch}.json"
            model.save_json(os.path.join(models_dir, safe_name))
            if ch == 'ñ':
                model.save_json(os.path.join(models_dir, "nn.json"))

        with open(os.path.join(models_dir, "models.json"), "w", encoding="utf-8") as f:
            json.dump(consolidated, f, indent=2, ensure_ascii=False)

    def classify(self, obs_sequence):
        """
        Evalúa la secuencia de observaciones parcial O_{1:t} en todos los modelos HMM.
        
        Aplica Softmax sobre las log-verosimilitudes para obtener probabilidades posteriores:
        P(c | O_{1:t}) = exp(ln P(O | lambda_c) - max_k ln P(O | lambda_k)) / sum_{c'} exp(...)
        
        Retorna:
        --------
        results : list of dicts ordenados descendentemente por probabilidad:
            [
                {
                    "char": 'a',
                    "probability": 0.842,
                    "percentage": "84.2%",
                    "log_likelihood": -14.25,
                    "rank": 1
                }, ...
            ]
        """
        if not self.models:
            # Si no hay modelos cargados, retorna distribución uniforme
            unif = 1.0 / len(self.alphabet)
            return [
                {"char": ch, "probability": unif, "percentage": f"{unif*100:.1f}%", "log_likelihood": 0.0, "rank": idx + 1}
                for idx, ch in enumerate(self.alphabet)
            ]

        if len(obs_sequence) == 0:
            # Trazo vacío: distribución uniforme
            unif = 1.0 / len(self.models)
            items = []
            for idx, ch in enumerate(sorted(self.models.keys())):
                items.append({
                    "char": ch,
                    "probability": unif,
                    "percentage": f"{unif * 100:.1f}%",
                    "log_likelihood": 0.0,
                    "rank": idx + 1
                })
            return items

        log_liks = {}
        for ch, model in self.models.items():
            ll, _, _ = model.forward(obs_sequence)
            log_liks[ch] = ll

        # Softmax numéricamente estable
        max_ll = max(log_liks.values())
        # Truncar exponente inferior para evitar underflow extremo
        exp_diffs = {ch: np.exp(max(ll - max_ll, -700.0)) for ch, ll in log_liks.items()}
        sum_exp = sum(exp_diffs.values())
        if sum_exp <= 0.0:
            sum_exp = 1.0

        probs = {ch: exp_diffs[ch] / sum_exp for ch in exp_diffs}

        # Ordenar descendentemente
        sorted_chars = sorted(probs.keys(), key=lambda c: probs[c], reverse=True)
        results = []
        for rank, ch in enumerate(sorted_chars, start=1):
            p = float(probs[ch])
            results.append({
                "char": ch,
                "probability": p,
                "percentage": f"{p * 100:.1f}%",
                "log_likelihood": float(log_liks[ch]),
                "rank": rank
            })

        return results

    def get_best_character(self, obs_sequence):
        """Retorna el carácter de mayor probabilidad a posteriori."""
        results = self.classify(obs_sequence)
        return results[0]["char"] if results else "a"

    def predict_trajectory_symbols(self, obs_sequence, top_char=None, horizon=20):
        """
        Retorna la secuencia de símbolos discretos proyectados para el autocompletado.
        Si no se especifica top_char, se toma el de mayor verosimilitud actual.
        """
        if not top_char:
            top_char = self.get_best_character(obs_sequence)

        model = self.models.get(top_char)
        if not model:
            return []

        # Si el modelo tiene trayectoria canónica aprendida y podemos sincronizarla:
        if model.canonical_symbols:
            T_drawn = len(obs_sequence)
            canon_len = len(model.canonical_symbols)
            if T_drawn < canon_len:
                # Extrae los símbolos restantes de la forma canónica
                return model.canonical_symbols[T_drawn:T_drawn + horizon]

        # En su defecto, proyecta mediante la secuencia de estados latentes de HMM
        return model.predict_future_symbols(obs_sequence, horizon=horizon)
