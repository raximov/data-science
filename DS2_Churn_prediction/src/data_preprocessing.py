"""
src/data_preprocessing.py

Bank mijozlarining ketib qolishi (churn) ma'lumotlarini tozalash, 
missing valuelarni to'ldirish, kategorial belgilarni kodlash hamda 
standartlashtirish moduli.
"""

import os
import pandas as pd
import numpy as np


def load_raw_data(data_dir="data"):
    """
    Xom ma'lumotlarni yuklash.
    """
    train_path = os.path.join(data_dir, "bank_data_train.csv")
    test_path = os.path.join(data_dir, "bank_data_test.csv")

    if not os.path.exists(train_path) or not os.path.exists(test_path):
        raise FileNotFoundError(f"Ma'lumotlar fayllari {data_dir} papkasida topilmadi.")

    train_df = pd.read_csv(train_path)
    test_df = pd.read_csv(test_path)

    return train_df, test_df


class DataPreprocessor:
    """
    Senior-level Data Preprocessor:
    - High-cardinality handling (Top N categories per column, rest -> 'OTHER')
    - Categorical One-Hot Encoding
    - Numerical median imputation + StandardScaler
    - RAM optimization (float32 conversion)
    """

    def __init__(self, top_k_cats=15):
        self.top_k_cats = top_k_cats
        self.cat_cols = []
        self.num_cols = []
        self.medians = {}
        self.top_categories_map = {}
        self.mean = None
        self.std = None
        self.final_feature_names = []

    def fit_transform(self, train_df):
        df = train_df.copy()
        
        # ID va TARGET ni ajratish
        if 'ID' in df.columns:
            df = df.drop(columns=['ID'])
        
        if 'TARGET' in df.columns:
            y = df['TARGET'].values.astype(np.int32)
            df = df.drop(columns=['TARGET'])
        else:
            y = None

        # Ustun turlarini aniqlash
        self.cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        self.num_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()

        # 1. Kategorial belgilarni ishlov berish (Top K strategiyasi)
        cat_processed_dfs = []
        for col in self.cat_cols:
            series = df[col].astype(str).fillna('MISSING')
            top_cats = series.value_counts().head(self.top_k_cats).index.tolist()
            if 'MISSING' not in top_cats:
                top_cats.append('MISSING')
            self.top_categories_map[col] = top_cats

            # Faqat top_cats qiymatlarini saqlash, qolganlarini 'OTHER' deb belgilash
            series_binned = series.apply(lambda x: x if x in top_cats else 'OTHER')
            dummies = pd.get_dummies(series_binned, prefix=col, dtype=np.float32)
            cat_processed_dfs.append(dummies)

        # 2. Sonli belgilarni to'ldirish
        num_dict = {}
        for col in self.num_cols:
            med = df[col].median()
            if pd.isna(med):
                med = 0.0
            self.medians[col] = float(med)
            num_dict[col] = df[col].fillna(med).astype(np.float32).values
        df_num = pd.DataFrame(num_dict, index=df.index)

        # Barcha belgilarni birlashtirish
        if cat_processed_dfs:
            df_cat_all = pd.concat(cat_processed_dfs, axis=1)
            X_all = pd.concat([df_num, df_cat_all], axis=1)
        else:
            X_all = df_num

        self.final_feature_names = X_all.columns.tolist()
        X_mat = X_all.values.astype(np.float32)

        # Standard Scaling (Mean = 0, Std = 1)
        self.mean = np.nanmean(X_mat, axis=0)
        self.std = np.nanstd(X_mat, axis=0)
        self.std[self.std < 1e-6] = 1.0  # Nolga bo'lish va doimiy ustunlar uchun

        X_scaled = (X_mat - self.mean) / self.std

        return X_scaled, y

    def transform(self, test_df):
        df = test_df.copy()
        if 'ID' in df.columns:
            df = df.drop(columns=['ID'])
        if 'TARGET' in df.columns:
            df = df.drop(columns=['TARGET'])

        # 1. Kategorial
        cat_processed_dfs = []
        for col in self.cat_cols:
            if col in df.columns:
                series = df[col].astype(str).fillna('MISSING')
            else:
                series = pd.Series(['MISSING'] * len(df))
            top_cats = self.top_categories_map.get(col, ['MISSING'])
            series_binned = series.apply(lambda x: x if x in top_cats else 'OTHER')
            dummies = pd.get_dummies(series_binned, prefix=col, dtype=np.float32)
            cat_processed_dfs.append(dummies)

        # 2. Sonli
        num_dict = {}
        for col in self.num_cols:
            if col in df.columns:
                val = df[col].fillna(self.medians.get(col, 0.0)).astype(np.float32).values
            else:
                val = np.full(len(df), self.medians.get(col, 0.0), dtype=np.float32)
            num_dict[col] = val
        df_num = pd.DataFrame(num_dict, index=df.index)

        if cat_processed_dfs:
            df_cat_all = pd.concat(cat_processed_dfs, axis=1)
            X_all = pd.concat([df_num, df_cat_all], axis=1)
        else:
            X_all = df_num

        # Fit paytidagi ustunlar strukturasiga reindex qilish
        X_all = X_all.reindex(columns=self.final_feature_names, fill_value=0.0)
        X_mat = X_all.values.astype(np.float32)

        X_scaled = (X_mat - self.mean) / self.std
        return X_scaled


def get_prepared_data(data_dir="data", test_size=0.2, random_state=42, top_k_cats=15):
    """
    Train/Validation split (Stratified) va Test ma'lumotlarini tayyorlab beruvchi asosiy funksiya.
    """
    train_df, test_df = load_raw_data(data_dir)
    test_ids = test_df['ID'].values

    preprocessor = DataPreprocessor(top_k_cats=top_k_cats)
    X_full, y_full = preprocessor.fit_transform(train_df)
    X_test = preprocessor.transform(test_df)

    # Stratified Split
    np.random.seed(random_state)
    idx_0 = np.where(y_full == 0)[0]
    idx_1 = np.where(y_full == 1)[0]

    np.random.shuffle(idx_0)
    np.random.shuffle(idx_1)

    n_val_0 = int(len(idx_0) * test_size)
    n_val_1 = int(len(idx_1) * test_size)

    val_idx = np.concatenate([idx_0[:n_val_0], idx_1[:n_val_1]])
    train_idx = np.concatenate([idx_0[n_val_0:], idx_1[n_val_1:]])

    np.random.shuffle(val_idx)
    np.random.shuffle(train_idx)

    X_train, y_train = X_full[train_idx], y_full[train_idx]
    X_val, y_val = X_full[val_idx], y_full[val_idx]

    print(f"[Data Pipeline] Train hajmi: {X_train.shape}, Val hajmi: {X_val.shape}, Test hajmi: {X_test.shape}")
    print(f"[Data Pipeline] Train Target tarqalishi: 0 -> {(y_train==0).mean():.4f}, 1 -> {(y_train==1).mean():.4f}")

    return X_train, y_train, X_val, y_val, X_test, test_ids, preprocessor
