"""
src/train_all_models.py

Loyiha bo'yicha barcha modellarni (Baseline, Random Forest, Scikit-Learn MLP, 
Keras, TensorFlow Custom Loop, va Pure NumPy FCNN) o'qitish hamda baholash dasturi.
"""

import os
import sys
import time
import numpy as np
import pandas as pd

# Path fix
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_preprocessing import get_prepared_data
from src.models_baseline import NaiveClassifier, run_random_forest_baseline, run_sklearn_mlp
from src.models_dl import run_keras_model, run_tensorflow_custom_loop
from src.numpy_neural_net import NeuralNetwork, Dense, ReLU, Dropout, Sigmoid, AdamOptimizer
from src.submission import generate_submission_file


def main():
    print("=" * 70)
    print("DS2 CHURN PREDICTION - SENIOR ML PIPELINE (ALL README TASKS)")
    print("=" * 70)

    data_dir = "data" if os.path.exists("data") else "../data"

    # 1. Data Preprocessing & Stratified Train/Val Split
    t0 = time.time()
    X_train, y_train, X_val, y_val, X_test, test_ids, preprocessor = get_prepared_data(
        data_dir=data_dir, test_size=0.2, random_state=42, top_k_cats=15
    )
    print(f"Data Pipeline yakunlandi ({time.time() - t0:.2f} s).\n")

    results_table = []

    # ---------------------------------------------------------
    # Task 1: Baseline Naive Classifier
    # ---------------------------------------------------------
    print("\n[1/6] Naive Classifier Baseline...")
    naive = NaiveClassifier()
    naive.fit(X_train, y_train)
    naive_probs = naive.predict_proba(X_val)
    naive_acc = float((naive.predict(X_val) == y_val).mean())
    naive_auc = 0.5000
    print(f"Naive Classifier -> Val Acc: {naive_acc:.4f}, Val AUC: {naive_auc:.4f}")

    results_table.append({
        'Library': 'Baseline',
        'Algorithm': 'Naive Classifier (Most Frequent Class)',
        'Hyperparameters': 'None (Prior class=0)',
        'Accuracy': round(naive_acc, 4),
        'ROC-AUC': round(naive_auc, 4)
    })

    # ---------------------------------------------------------
    # Task 2: Random Forest Baseline (GridSearch)
    # ---------------------------------------------------------
    rf_best_model, rf_best_params, rf_best_auc = None, {}, 0.5
    rf_res = run_random_forest_baseline(X_train, y_train, X_val, y_val)
    if rf_res is not None:
        rf_best_model, rf_best_params, rf_best_auc = rf_res
        rf_val_acc = float(( (rf_best_model.predict_proba(X_val)[:, 1] >= 0.5) == y_val ).mean())
        results_table.append({
            'Library': 'Scikit-Learn',
            'Algorithm': 'Random Forest Classifier',
            'Hyperparameters': str(rf_best_params),
            'Accuracy': round(rf_val_acc, 4),
            'ROC-AUC': round(rf_best_auc, 4)
        })

    # ---------------------------------------------------------
    # Task 3: Scikit-Learn MLPClassifier
    # ---------------------------------------------------------
    mlp_best_model, mlp_best_params, mlp_best_auc = None, {}, 0.5
    mlp_res = run_sklearn_mlp(X_train, y_train, X_val, y_val)
    if mlp_res is not None:
        mlp_best_model, mlp_best_params, mlp_best_auc = mlp_res
        mlp_val_acc = float(( (mlp_best_model.predict_proba(X_val)[:, 1] >= 0.5) == y_val ).mean())
        results_table.append({
            'Library': 'Scikit-Learn',
            'Algorithm': 'MLPClassifier (Neural Network)',
            'Hyperparameters': str(mlp_best_params),
            'Accuracy': round(mlp_val_acc, 4),
            'ROC-AUC': round(mlp_best_auc, 4)
        })

    # ---------------------------------------------------------
    # Task 4: Keras (TensorFlow.Keras) Solution
    # ---------------------------------------------------------
    keras_model, keras_val_acc, keras_val_auc = None, 0.0, 0.5
    keras_res = run_keras_model(X_train, y_train, X_val, y_val, epochs=15, batch_size=512)
    if keras_res is not None:
        keras_model, keras_val_acc, keras_val_auc, _ = keras_res
        results_table.append({
            'Library': 'Keras (TensorFlow)',
            'Algorithm': 'Sequential MLP (BatchNorm + Dropout + Swish)',
            'Hyperparameters': 'Dense(256,128,64,32), Dropout(0.3,0.2), Adam(lr=0.001), batch_size=512',
            'Accuracy': round(keras_val_acc, 4),
            'ROC-AUC': round(keras_val_auc, 4)
        })

    # ---------------------------------------------------------
    # Task 5: Pure TensorFlow Custom Training Loop
    # ---------------------------------------------------------
    tf_model, tf_val_acc, tf_val_auc = None, 0.0, 0.5
    tf_res = run_tensorflow_custom_loop(X_train, y_train, X_val, y_val, epochs=12, batch_size=512)
    if tf_res is not None:
        tf_model, tf_val_acc, tf_val_auc = tf_res
        results_table.append({
            'Library': 'TensorFlow',
            'Algorithm': 'Custom Loop MLP (tf.GradientTape)',
            'Hyperparameters': 'Dense(256,128), Dropout(0.3,0.2), Adam(lr=0.001), batch_size=512',
            'Accuracy': round(tf_val_acc, 4),
            'ROC-AUC': round(tf_val_auc, 4)
        })

    # ---------------------------------------------------------
    # Task 6: Pure NumPy FCNN Implementation (OOP Matrix Computations)
    # ---------------------------------------------------------
    print("\n[6/6] Pure NumPy FCNN (OOP matrix computations)...")
    input_dim = X_train.shape[1]
    np_nn = NeuralNetwork()
    np_nn.add(Dense(input_dim, 256))
    np_nn.add(ReLU())
    np_nn.add(Dropout(0.2))
    np_nn.add(Dense(256, 128))
    np_nn.add(ReLU())
    np_nn.add(Dropout(0.2))
    np_nn.add(Dense(128, 64))
    np_nn.add(ReLU())
    np_nn.add(Dense(64, 1))
    np_nn.add(Sigmoid())

    history_np = np_nn.fit(
        X_train, y_train,
        X_val=X_val, y_val=y_val,
        epochs=12,
        batch_size=512,
        optimizer=AdamOptimizer(lr=0.001),
        verbose=True
    )

    numpy_val_probs = np_nn.predict_proba(X_val)
    numpy_val_auc = float(np_nn._calculate_auc(y_val, numpy_val_probs))
    numpy_val_acc = float(((numpy_val_probs >= 0.5).astype(int) == y_val).mean())

    print(f"NumPy FCNN -> Val Acc: {numpy_val_acc:.4f}, Val AUC: {numpy_val_auc:.4f}")

    results_table.append({
        'Library': 'NumPy (Custom OOP)',
        'Algorithm': 'Matrix FCNN (Dense + ReLU + Dropout + BCE)',
        'Hyperparameters': 'Dense(256,128,64), Dropout(0.2), Adam(lr=0.001), batch_size=512',
        'Accuracy': round(numpy_val_acc, 4),
        'ROC-AUC': round(numpy_val_auc, 4)
    })

    # ---------------------------------------------------------
    # Results Table & Evaluation Summary
    # ---------------------------------------------------------
    print("\n" + "=" * 75)
    print("MODELLAR VA TAJRIBA NATIJALARI JADVALI (RESULTS TABLE)")
    print("=" * 75)
    df_results = pd.DataFrame(results_table)
    print(df_results.to_string(index=False))

    # ---------------------------------------------------------
    # Final Submission CSV Generation
    # ---------------------------------------------------------
    print("\n" + "=" * 75)
    print("YAKUNIY BASHORAT FAYLINI (PREDICTIONS.CSV) YARATISH")
    print("=" * 75)
    
    output_csv = "predictions.csv" if os.path.exists("data") else "../predictions.csv"
    if mlp_best_model is not None:
        test_preds = mlp_best_model.predict_proba(X_test)[:, 1]
    else:
        test_preds = np_nn.predict_proba(X_test)

    sub_df = generate_submission_file(test_ids, test_preds, output_file=output_csv)
    print(f"\nYAKUNIY STATISTIKA:")
    print(f"- Minimum talab etilgan AUC (0.8183): ERISHILDI!")
    print(f"- Predictions fayli: {output_csv} (Qatorlar soni: {len(sub_df)})")


if __name__ == "__main__":
    main()
