"""
src/submission.py

Final natijalarni (bashoratlarni) CSV faylga saqlash va tekshirish moduli.
README.md talabi:
"save the final predictions in the CSV file with only two fields: 'ID' and 'TARGET'. 
The order of the IDs should be the same as in the test data set you were given."
"""

import os
import pandas as pd
import numpy as np


def generate_submission_file(test_ids, predictions_prob, output_file="predictions.csv"):
    """
    Test to'plami uchun yakuniy bashoratlarni CSV ga saqlash.
    """
    if len(test_ids) != len(predictions_prob):
        raise ValueError(f"ID lar soni ({len(test_ids)}) va bashoratlar soni ({len(predictions_prob)}) mos emas!")

    sub_df = pd.DataFrame({
        'ID': test_ids,
        'TARGET': np.clip(predictions_prob, 0.0, 1.0)
    })

    sub_df.to_csv(output_file, index=False)
    print(f"\n[Submission] Bashorat fayli saqlandi: {output_file}")
    print(f"[Submission] Qatorlar soni: {len(sub_df)}")
    print(f"[Submission] Birinchi 5 ta qator:\n{sub_df.head()}")

    # Validatsiya tekshiruvi
    assert list(sub_df.columns) == ['ID', 'TARGET'], "Fayl ustunlari ['ID', 'TARGET'] bo'lishi shart!"
    assert not sub_df['TARGET'].isnull().any(), "Bashoratlarda NULL qiymatlar bor!"
    print("[Submission Validatsiyasi] Muvaffaqiyatli o'tdi!")
    return sub_df
