"""
src/models_baseline.py

Baseline modellar moduli:
1. Naive Classifier (eng ko'p uchraydigan sinf)
2. Random Forest Classifier (GridSearch giperparametrlari bilan)
3. Scikit-Learn MLPClassifier (Multi-layer Perceptron)
"""

import numpy as np


class NaiveClassifier:
    """
    1. Baseline: Naive Classifier.
    Barcha namunalar uchun eng ko'p uchraydigan sinfni (0) yoki 
    sinf tarqalish prior ehtimolligini qaytaradi.
    """
    def __init__(self):
        self.most_frequent_class = 0
        self.prior_prob = 0.0

    def fit(self, X, y):
        counts = np.bincount(y.astype(int))
        self.most_frequent_class = np.argmax(counts)
        self.prior_prob = float(np.mean(y == 1))
        return self

    def predict(self, X):
        return np.full(X.shape[0], self.most_frequent_class, dtype=int)

    def predict_proba(self, X):
        # 1-sinf ehtimolligini qaytarish
        return np.full(X.shape[0], self.prior_prob, dtype=np.float32)


def run_random_forest_baseline(X_train, y_train, X_val, y_val):
    """
    2. Random Forest Baseline (GridSearch orqali optimallashtirish).
    """
    try:
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.metrics import accuracy_score, roc_auc_score
    except ImportError:
        print("[Warning] scikit-learn o'rnatilmagan.")
        return None, {}, 0.5

    print("\n--- 2. Random Forest Baseline & Grid Search ---")
    best_model = None
    best_auc = 0.5
    best_params = {}

    param_grid = [
        {'n_estimators': 50, 'max_depth': 10, 'min_samples_split': 5},
        {'n_estimators': 100, 'max_depth': 15, 'min_samples_split': 5},
        {'n_estimators': 150, 'max_depth': 20, 'min_samples_split': 2},
    ]

    for params in param_grid:
        rf = RandomForestClassifier(**params, random_state=42, n_jobs=-1)
        rf.fit(X_train, y_train)

        val_probs = rf.predict_proba(X_val)[:, 1]
        auc = roc_auc_score(y_val, val_probs)
        acc = accuracy_score(y_val, (val_probs >= 0.5).astype(int))

        print(f"RF Params: {params} -> Val Acc: {acc:.4f}, Val AUC: {auc:.4f}")

        if auc > best_auc:
            best_auc = auc
            best_model = rf
            best_params = params

    print(f"Best RF Params: {best_params} | Best Val AUC: {best_auc:.4f}")
    return best_model, best_params, best_auc


def run_sklearn_mlp(X_train, y_train, X_val, y_val):
    """
    3. Scikit-Learn MLPClassifier.
    """
    try:
        from sklearn.neural_network import MLPClassifier
        from sklearn.metrics import accuracy_score, roc_auc_score
    except ImportError:
        print("[Warning] scikit-learn o'rnatilmagan.")
        return None, {}, 0.5

    print("\n--- 3. Scikit-Learn MLPClassifier ---")
    best_model = None
    best_auc = 0.5
    best_params = {}

    param_grid = [
        {'hidden_layer_sizes': (128, 64), 'activation': 'relu', 'alpha': 0.0001, 'max_iter': 25},
        {'hidden_layer_sizes': (256, 128, 64), 'activation': 'relu', 'alpha': 0.001, 'max_iter': 25},
        {'hidden_layer_sizes': (128, 64, 32), 'activation': 'tanh', 'alpha': 0.0001, 'max_iter': 25},
    ]

    for params in param_grid:
        mlp = MLPClassifier(**params, random_state=42, early_stopping=True)
        mlp.fit(X_train, y_train)

        val_probs = mlp.predict_proba(X_val)[:, 1]
        auc = roc_auc_score(y_val, val_probs)
        acc = accuracy_score(y_val, (val_probs >= 0.5).astype(int))

        print(f"MLP Params: {params} -> Val Acc: {acc:.4f}, Val AUC: {auc:.4f}")

        if auc > best_auc:
            best_auc = auc
            best_model = mlp
            best_params = params

    print(f"Best Scikit-Learn MLP Params: {best_params} | Best Val AUC: {best_auc:.4f}")
    return best_model, best_params, best_auc
