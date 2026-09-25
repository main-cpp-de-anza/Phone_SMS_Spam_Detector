import re
import pandas as pd

DATA_FILE = "spam_ham_dataset.csv"

SPAM_WORDS = [
    "congratulations",
    "congrats",
    "free",
    "winner",
    "won",
    "prize",
    "click here",
    "limited time",
    "buy now",
    "claim"
]

def hardcoded_detector(email):
    email = str(email).lower()
    matched_words = []

    for word in SPAM_WORDS:
        pattern = r"\b" + re.escape(word) + r"\b"
        if re.search(pattern, email):
            matched_words.append(word)

    return ("spam" if matched_words else "ham"), matched_words

df = pd.read_csv(DATA_FILE)
df["label"] = df["label"].astype(str).str.lower().str.strip()

results = df["text"].apply(hardcoded_detector)
df["prediction"] = results.apply(lambda x: x[0])
df["matched_words"] = results.apply(lambda x: x[1])
df["correct"] = df["prediction"] == df["label"]

accuracy = df["correct"].mean()

false_positives = df[
    (df["label"] == "ham") &
    (df["prediction"] == "spam")
]

false_negatives = df[
    (df["label"] == "spam") &
    (df["prediction"] == "ham")
]

print("=" * 50)
print("SECTION 1 - HARD-CODED RULES")
print("=" * 50)
print(f"Total emails: {len(df)}")
print(f"Accuracy: {accuracy:.2%}")
print(f"False positives: {len(false_positives)}")
print(f"False negatives: {len(false_negatives)}")

if not false_positives.empty:
    row = false_positives.iloc[0]
    print("\nFalse Positive Example")
    print("Actual: HAM")
    print("Prediction: SPAM")
    print("Matched words:", row["matched_words"])
    print("Preview:", str(row["text"]).replace("\n", " ")[:180] + "...")

if not false_negatives.empty:
    row = false_negatives.iloc[0]
    print("\nFalse Negative Example")
    print("Actual: SPAM")
    print("Prediction: HAM")
    print("Preview:", str(row["text"]).replace("\n", " ")[:180] + "...")

main_cpp_ad = """
Subject: CONGRATULATIONS! Join main.cpp for FREE!

Congratulations!
You have been selected to join main.cpp!
Join for FREE and work on exciting coding projects.
LIMITED TIME opportunity!
CLICK HERE to join today!
"""

main_cpp_normal = """
Subject: main.cpp Club Meeting

Hi everyone,

Are you free tomorrow?
We are having a main.cpp club meeting at 3 PM.

Thanks!
"""

ad_prediction, ad_words = hardcoded_detector(main_cpp_ad)
normal_prediction, normal_words = hardcoded_detector(main_cpp_normal)

print("\nmain.cpp Demo")
print("Promotional email ->", ad_prediction.upper(), "| Matched:", ad_words)
print("Normal email      ->", normal_prediction.upper(), "| Matched:", normal_words)
print("Expected normal email label: HAM")

print("\nLimitation:")
print(
    "Hard-coded rules are simple, but they do not understand context. "
    "A word such as 'free' can appear in both spam and normal emails."
)
