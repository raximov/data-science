"""
src/numpy_neural_net.py

NumPy ramkasi yordamida to'liq noldan yozilgan Sun'iy Neyron Tarmog'i (FCNN).
OOP prinsiplari: Layer, Dense, Activation, Dropout, Loss, Optimizer, NeuralNetwork.
"""

import numpy as np


class Layer:
    """
    Qatlamlar uchun abstrakt baza kursi.
    """
    def forward(self, inputs, training=True):
        raise NotImplementedError

    def backward(self, dout):
        raise NotImplementedError

    def get_params(self):
        return []

    def get_grads(self):
        return []


class Dense(Layer):
    """
    To'liq bog'langan (Fully Connected / Linear) Qatlam.
    Vaznlarni initsializatsiya qilish: He Normal Initialization.
    """
    def __init__(self, in_features, out_features):
        # He / Kaiming initialization
        self.W = np.random.randn(in_features, out_features).astype(np.float32) * np.sqrt(2.0 / in_features)
        self.b = np.zeros((1, out_features), dtype=np.float32)
        
        self.dW = np.zeros_like(self.W)
        self.db = np.zeros_like(self.b)
        self.inputs = None

    def forward(self, inputs, training=True):
        self.inputs = inputs
        return np.dot(inputs, self.W) + self.b

    def backward(self, dout):
        # dout shape: (batch_size, out_features)
        batch_size = self.inputs.shape[0]
        self.dW = np.dot(self.inputs.T, dout) / batch_size
        self.db = np.sum(dout, axis=0, keepdims=True) / batch_size
        dx = np.dot(dout, self.W.T)
        return dx

    def get_params(self):
        return [self.W, self.b]

    def get_grads(self):
        return [self.dW, self.db]


class ReLU(Layer):
    """
    ReLU Aktivatsiya Qatlami: f(x) = max(0, x)
    """
    def __init__(self):
        self.inputs = None

    def forward(self, inputs, training=True):
        self.inputs = inputs
        return np.maximum(0, inputs)

    def backward(self, dout):
        dx = dout.copy()
        dx[self.inputs <= 0] = 0
        return dx


class Sigmoid(Layer):
    """
    Sigmoid Aktivatsiya Qatlami: f(x) = 1 / (1 + exp(-x))
    """
    def __init__(self):
        self.out = None

    def forward(self, inputs, training=True):
        # Numeric overflow guard
        clipped_inputs = np.clip(inputs, -50.0, 50.0)
        self.out = 1.0 / (1.0 + np.exp(-clipped_inputs))
        return self.out

    def backward(self, dout):
        return dout * self.out * (1.0 - self.out)


class Dropout(Layer):
    """
    Inverted Dropout Qatlami (Regularizatsiya uchun).
    """
    def __init__(self, drop_rate=0.2):
        self.drop_rate = drop_rate
        self.mask = None

    def forward(self, inputs, training=True):
        if training and self.drop_rate > 0.0:
            keep_prob = 1.0 - self.drop_rate
            self.mask = (np.random.rand(*inputs.shape) < keep_prob) / keep_prob
            return inputs * self.mask
        return inputs

    def backward(self, dout):
        if self.mask is not None:
            return dout * self.mask
        return dout


class BinaryCrossEntropyLoss:
    """
    Binary Cross-Entropy Yo'qotish funksiyasi.
    Loss = - [y * log(p) + (1-y) * log(1-p)]
    """
    def __call__(self, y_true, y_pred, eps=1e-12):
        y_pred = np.clip(y_pred, eps, 1.0 - eps)
        loss = - np.mean(y_true * np.log(y_pred) + (1.0 - y_true) * np.log(1.0 - y_pred))
        return loss

    def gradient(self, y_true, y_pred, eps=1e-12):
        y_pred = np.clip(y_pred, eps, 1.0 - eps)
        # Loss ning y_pred bo'yicha hosilasi
        grad = (y_pred - y_true) / (y_pred * (1.0 - y_pred))
        return grad


class AdamOptimizer:
    """
    Adam Optimizatori (Adaptive Moment Estimation).
    """
    def __init__(self, lr=0.001, beta1=0.9, beta2=0.999, eps=1e-8):
        self.lr = lr
        self.beta1 = beta1
        self.beta2 = beta2
        self.eps = eps
        self.m = {}
        self.v = {}
        self.t = 0

    def update(self, layers):
        self.t += 1
        for i, layer in enumerate(layers):
            params = layer.get_params()
            grads = layer.get_grads()
            if not params:
                continue

            if i not in self.m:
                self.m[i] = [np.zeros_like(p) for p in params]
                self.v[i] = [np.zeros_like(p) for p in params]

            for j in range(len(params)):
                self.m[i][j] = self.beta1 * self.m[i][j] + (1 - self.beta1) * grads[j]
                self.v[i][j] = self.beta2 * self.v[i][j] + (1 - self.beta2) * (grads[j] ** 2)

                m_hat = self.m[i][j] / (1 - self.beta1 ** self.t)
                v_hat = self.v[i][j] / (1 - self.beta2 ** self.t)

                params[j] -= self.lr * m_hat / (np.sqrt(v_hat) + self.eps)


class NeuralNetwork:
    """
    NumPy FCNN Kontayneri.
    """
    def __init__(self):
        self.layers = []
        self.loss_fn = BinaryCrossEntropyLoss()

    def add(self, layer):
        self.layers.append(layer)

    def forward(self, X, training=True):
        out = X
        for layer in self.layers:
            out = layer.forward(out, training=training)
        return out

    def backward(self, loss_grad):
        dout = loss_grad
        for layer in reversed(self.layers):
            dout = layer.backward(dout)

    def fit(self, X_train, y_train, X_val=None, y_val=None, epochs=15, batch_size=512, optimizer=None, verbose=True):
        if optimizer is None:
            optimizer = AdamOptimizer(lr=0.001)

        y_train = y_train.reshape(-1, 1).astype(np.float32)
        if y_val is not None:
            y_val = y_val.reshape(-1, 1).astype(np.float32)

        num_samples = X_train.shape[0]
        history = {'train_loss': [], 'val_loss': [], 'val_auc': []}

        for epoch in range(1, epochs + 1):
            # Epoch boshida ma'lumotlarni aralashtirish
            indices = np.arange(num_samples)
            np.random.shuffle(indices)
            X_shuffled = X_train[indices]
            y_shuffled = y_train[indices]

            epoch_losses = []
            for start_idx in range(0, num_samples, batch_size):
                end_idx = min(start_idx + batch_size, num_samples)
                X_batch = X_shuffled[start_idx:end_idx]
                y_batch = y_shuffled[start_idx:end_idx]

                # 1. Forward
                y_pred = self.forward(X_batch, training=True)
                loss = self.loss_fn(y_batch, y_pred)
                epoch_losses.append(loss)

                # 2. Backward
                loss_grad = self.loss_fn.gradient(y_batch, y_pred)
                self.backward(loss_grad)

                # 3. Update weights
                optimizer.update(self.layers)

            train_loss = np.mean(epoch_losses)
            history['train_loss'].append(train_loss)

            val_str = ""
            if X_val is not None and y_val is not None:
                val_preds = self.forward(X_val, training=False)
                val_loss = self.loss_fn(y_val, val_preds)
                val_auc = self._calculate_auc(y_val.flatten(), val_preds.flatten())
                history['val_loss'].append(val_loss)
                history['val_auc'].append(val_auc)
                val_str = f" | Val Loss: {val_loss:.4f} - Val AUC: {val_auc:.4f}"

            if verbose and (epoch % 1 == 0 or epoch == epochs):
                print(f"Epoch {epoch:02d}/{epochs:02d} - Train Loss: {train_loss:.4f}{val_str}")

        return history

    def predict_proba(self, X):
        return self.forward(X, training=False).flatten()

    def predict(self, X, threshold=0.5):
        probs = self.predict_proba(X)
        return (probs >= threshold).astype(int)

    def _calculate_auc(self, y_true, y_pred):
        """
        Pure NumPy Trapezoidal ROC-AUC hisoblash funksiyasi.
        """
        # Elementlarni ehtimollik bo'yicha kamayish tartibida saralash
        sort_idx = np.argsort(y_pred)[::-1]
        y_true_sorted = y_true[sort_idx]
        
        tps = np.cumsum(y_true_sorted)
        fps = np.cumsum(1 - y_true_sorted)

        if tps[-1] == 0 or fps[-1] == 0:
            return 0.5

        tpr = tps / tps[-1]
        fpr = fps / fps[-1]

        # Trapezoidal integral (AUC)
        auc = np.trapz(tpr, fpr)
        return float(auc)
