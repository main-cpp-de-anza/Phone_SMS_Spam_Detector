import pandas as pd
import numpy as np

from sklearn.pipeline import make_pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import confusion_matrix, f1_score, accuracy_score


# ==========================================
# 1. Load dataset
# ==========================================

df = pd.read_csv("spam_ham_dataset.csv")

X = df["text"]
y = df["label"]


# ==========================================
# 2. Model
# TF-IDF + Multinomial Naive Bayes
# ==========================================

model = make_pipeline(
    TfidfVectorizer(),
    MultinomialNB()
)


# ==========================================
# 3. 5-Fold Stratified Cross Validation
# ==========================================

cv = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)

all_true = []
all_pred = []

f1_scores = []
accuracy_scores = []


for fold, (train_index, test_index) in enumerate(
    cv.split(X, y),
    start=1
):

    X_train = X.iloc[train_index]
    X_test = X.iloc[test_index]

    y_train = y.iloc[train_index]
    y_test = y.iloc[test_index]


    # Train model
    model.fit(X_train, y_train)


    # Predict
    y_pred = model.predict(X_test)


    # Save predictions
    all_true.extend(y_test)
    all_pred.extend(y_pred)


    # F1 score and accuracy
    f1 = f1_score(
        y_test,
        y_pred,
        pos_label="spam"
    )

    accuracy = accuracy_score(
        y_test,
        y_pred
    )

    f1_scores.append(f1)
    accuracy_scores.append(accuracy)


    # Confusion matrix
    tn, fp, fn, tp = confusion_matrix(
        y_test,
        y_pred,
        labels=["ham", "spam"]
    ).ravel()


    print(f"Fold {fold}")
    print("False Positives:", fp)
    print("False Negatives:", fn)
    print("F1 Score:", round(f1, 4))
    print("Accuracy:", round(accuracy, 4))
    print()


# ==========================================
# 4. Final Results
# ==========================================

tn, fp, fn, tp = confusion_matrix(
    all_true,
    all_pred,
    labels=["ham", "spam"]
).ravel()


print("========== Multinomial Naive Bayes ==========")

print("False Positives:", fp)
print("False Negatives:", fn)

print(
    "Average F1 Score:",
    round(np.mean(f1_scores), 4)
)

print(
    "Average Accuracy:",
    round(np.mean(accuracy_scores), 4)
)