#!/usr/bin/env python3

import sys
import pandas as pd
import joblib
import numpy as np


# =========================
# RATING PREDICTOR
# =========================
class RatingPredictor:
    def __init__(self, model_path, ingredient_cols):
        self.model = joblib.load(model_path)
        self.ingredient_cols = ingredient_cols

    def _build_vector(self, ingredients):
        x = np.zeros(len(self.ingredient_cols))

        for ing in ingredients:
            if ing in self.ingredient_cols:
                idx = self.ingredient_cols.index(ing)
                x[idx] = 1

        return x.reshape(1, -1)

    def predict(self, ingredients):
        x = self._build_vector(ingredients)
        pred = self.model.predict(x)[0]

        # map to labels
        if pred <= 2:
            return "bad"
        elif pred <= 3.5:
            return "so-so"
        else:
            return "great"


# =========================
# NUTRITION ANALYZER
# =========================
class NutritionAnalyzer:
    def __init__(self, nutrition_path):
        self.df = pd.read_csv(nutrition_path)

    def get_nutrition(self, ingredients):
        result = {}

        for ing in ingredients:
            row = self.df[self.df['ingredient'] == ing]

            if not row.empty:
                result[ing] = row.iloc[0].to_dict()
            else:
                result[ing] = None

        return result


# =========================
# READ INPUT
# =========================
def parse_ingredients():
    if len(sys.argv) < 2:
        print("Usage: ./nutritionist.py milk, honey, jam")
        sys.exit(1)

    joined = " ".join(sys.argv[1:])
    ingredients = [x.strip().lower() for x in joined.split(",")]

    return ingredients


# =========================
# MAIN
# =========================
def main():
    ingredients = parse_ingredients()

    # load ingredient columns (same as training!)
    df = pd.read_csv("data/epi_r.csv")
    non_ing = ['title', 'rating', 'calories', 'protein', 'fat', 'sodium']
    ingredient_cols = [c for c in df.columns if c not in non_ing]

    predictor = RatingPredictor("models/best_rf_model.pkl", ingredient_cols)
    nutrition = NutritionAnalyzer("data/ingredients_nutrition.csv")

    # =========================
    # I. FORECAST
    # =========================
    print("I. OUR FORECAST")

    result = predictor.predict(ingredients)

    if result == "bad":
        print("You might find it tasty, but in our opinion, it is a bad idea to have a")
        print("dish with that list of ingredients.")
    elif result == "so-so":
        print("It might be okay, but it’s not the best combination.")
    else:
        print("Great choice! This combination should be tasty and enjoyable.")

    # =========================
    # II. NUTRITION FACTS
    # =========================
    print("\nII. NUTRITION FACTS")

    facts = nutrition.get_nutrition(ingredients)

    for ing in ingredients:
        print(f"\n{ing.capitalize()}")

        if facts[ing]:
            for k, v in facts[ing].items():
                if k != "ingredient":
                    print(f"{k} - {v}% of Daily Value")
        else:
            print("No data available")


# =========================
# ENTRY
# =========================
if __name__ == "__main__":
    main()