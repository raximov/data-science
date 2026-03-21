import pandas as pd
import joblib


# =========================
# 1. RATING PREDICTOR
# =========================
class RatingPredictor:
    def __init__(self, model_path, ingredient_cols):
        self.model = joblib.load(model_path)
        self.columns = ingredient_cols

    def preprocess(self, ingredients):
        data = {col: 0 for col in self.columns}

        for ing in ingredients:
            if ing in data:
                data[ing] = 1

        return pd.DataFrame([data])

    def predict(self, ingredients):
        X = self.preprocess(ingredients)
        pred = self.model.predict(X)[0]

        # 🔥 map regression → label
        if pred <= 2:
            return "bad"
        elif pred <= 3.5:
            return "so-so"
        else:
            return "great"


# =========================
# 2. NUTRITION ANALYZER
# =========================
class NutritionAnalyzer:
    def __init__(self, nutrition_csv):
        self.df = pd.read_csv(nutrition_csv)

    def get_nutrition(self, ingredients):
        result = {}

        for ing in ingredients:
            row = self.df[self.df['ingredient'] == ing]

            if not row.empty:
                result[ing] = row.iloc[0].to_dict()
            else:
                result[ing] = None   # 🔥 important (matches nutritionist.py)

        return result