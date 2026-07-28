"""
src/models_dl.py

Deep Learning Framework Modellar moduli:
1. Keras (TensorFlow.Keras Sequential / Functional API model)
2. TensorFlow Custom Training Loop (GradientTape bilan)
"""

import numpy as np


def run_keras_model(X_train, y_train, X_val, y_val, epochs=20, batch_size=512):
    """
    Keras yordamida ko'p qatlamli neyron tarmog'i (MLP / FCNN).
    Dropout, BatchNormalization hamda EarlyStopping va ReduceLROnPlateau ishlatiladi.
    """
    try:
        import tensorflow as tf
        from tensorflow.keras import layers, models, callbacks, metrics
    except ImportError:
        print("[Warning] TensorFlow / Keras o'rnatilmagan.")
        return None, 0.0, 0.5, None

    print("\n--- 4. Keras (TensorFlow.Keras) MLP Model ---")
    input_dim = X_train.shape[1]

    model = models.Sequential([
        layers.Input(shape=(input_dim,)),
        
        layers.Dense(256),
        layers.BatchNormalization(),
        layers.Activation('swish'),
        layers.Dropout(0.3),
        
        layers.Dense(128),
        layers.BatchNormalization(),
        layers.Activation('swish'),
        layers.Dropout(0.3),
        
        layers.Dense(64),
        layers.BatchNormalization(),
        layers.Activation('swish'),
        layers.Dropout(0.2),

        layers.Dense(32),
        layers.BatchNormalization(),
        layers.Activation('swish'),
        
        layers.Dense(1, activation='sigmoid')
    ])

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        loss='binary_crossentropy',
        metrics=[
            metrics.BinaryAccuracy(name='accuracy'),
            metrics.AUC(name='auc')
        ]
    )

    cb_list = [
        callbacks.EarlyStopping(monitor='val_auc', mode='max', patience=5, restore_best_weights=True),
        callbacks.ReduceLROnPlateau(monitor='val_auc', mode='max', factor=0.5, patience=2, verbose=1)
    ]

    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=epochs,
        batch_size=batch_size,
        callbacks=cb_list,
        verbose=1
    )

    val_probs = model.predict(X_val, batch_size=1024).flatten()
    
    try:
        from sklearn.metrics import accuracy_score, roc_auc_score
        val_auc = roc_auc_score(y_val, val_probs)
        val_acc = accuracy_score(y_val, (val_probs >= 0.5).astype(int))
    except ImportError:
        val_auc = float(history.history['val_auc'][-1])
        val_acc = float(history.history['val_accuracy'][-1])

    print(f"Keras Model -> Val Acc: {val_acc:.4f}, Val AUC: {val_auc:.4f}")
    return model, val_acc, val_auc, history


def run_tensorflow_custom_loop(X_train, y_train, X_val, y_val, epochs=15, batch_size=512):
    """
    TensorFlow pastki darajadagi (Low-Level) Custom Training Loop gradient tape bilan.
    """
    try:
        import tensorflow as tf
    except ImportError:
        print("[Warning] TensorFlow o'rnatilmagan.")
        return None, 0.0, 0.5

    print("\n--- 5. Pure TensorFlow Custom Training Loop ---")
    input_dim = X_train.shape[1]

    class CustomTFMLP(tf.keras.Model):
        def __init__(self):
            super().__init__()
            self.d1 = tf.keras.layers.Dense(256, activation='relu')
            self.drop1 = tf.keras.layers.Dropout(0.3)
            self.d2 = tf.keras.layers.Dense(128, activation='relu')
            self.drop2 = tf.keras.layers.Dropout(0.2)
            self.out = tf.keras.layers.Dense(1, activation='sigmoid')

        def call(self, x, training=False):
            x = self.d1(x)
            x = self.drop1(x, training=training)
            x = self.d2(x)
            x = self.drop2(x, training=training)
            return self.out(x)

    model = CustomTFMLP()
    loss_object = tf.keras.losses.BinaryCrossentropy()
    optimizer = tf.keras.optimizers.Adam(learning_rate=0.001)

    train_auc_metric = tf.keras.metrics.AUC(name='train_auc')
    val_auc_metric = tf.keras.metrics.AUC(name='val_auc')

    train_dataset = tf.data.Dataset.from_tensor_slices((X_train, y_train)).shuffle(buffer_size=10000).batch(batch_size)

    @tf.function
    def train_step(images, labels):
        with tf.GradientTape() as tape:
            predictions = model(images, training=True)
            loss = loss_object(labels, predictions)
        gradients = tape.gradient(loss, model.trainable_variables)
        optimizer.apply_gradients(zip(gradients, model.trainable_variables))
        train_auc_metric.update_state(labels, predictions)
        return loss

    best_val_auc = 0.0

    for epoch in range(1, epochs + 1):
        train_auc_metric.reset_state()
        val_auc_metric.reset_state()

        epoch_loss_avg = tf.keras.metrics.Mean()
        for x_b, y_b in train_dataset:
            y_b = tf.expand_dims(y_b, axis=-1)
            loss = train_step(x_b, y_b)
            epoch_loss_avg.update_state(loss)

        val_preds = model(X_val, training=False)
        val_auc_metric.update_state(y_val, val_preds)
        
        val_auc = float(val_auc_metric.result())
        train_auc = float(train_auc_metric.result())

        if val_auc > best_val_auc:
            best_val_auc = val_auc

        print(f"TF Custom Epoch {epoch:02d}/{epochs:02d} - Loss: {epoch_loss_avg.result():.4f} - Train AUC: {train_auc:.4f} - Val AUC: {val_auc:.4f}")

    val_preds_final = model(X_val, training=False).numpy().flatten()
    val_acc = float(( (val_preds_final >= 0.5) == y_val ).mean())

    print(f"TF Custom Model -> Final Val Acc: {val_acc:.4f}, Best Val AUC: {best_val_auc:.4f}")
    return model, val_acc, best_val_auc
