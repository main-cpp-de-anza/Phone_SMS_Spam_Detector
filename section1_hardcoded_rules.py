import re
import pandas as pd

# ============================================================
# SECTION 1: HARD-CODED RULES
#
# Goal:
# 1. Detect spam using fixed keywords/rules.
# 2. Test the rules on the spam/ham email dataset.
# 3. Show the limitation: hard-coded rules do not generalize well.
# 4. Use main.cpp emails as simple presentation examples.
# ============================================================

DATA_FILE = "spam_ham_dataset.csv"

# Fixed words/phrases that we decide are suspicious.
# These are NOT learned from data.
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
    """
    Detect spam using only predefined words/phrases.

    Returns:
        prediction: "spam" or "ham"
        matched_words: list of suspicious words found
    """
    email = str(email).lower()

    matched_words = []

    for word in SPAM_WORDS:
        # re.escape() makes sure special characters are treated normally.
        if re.search(re.escape(word), email):
            matched_words.append(word)

    if matched_words:
        return "spam", matched_words

    return "ham", matched_words


# ============================================================
# PART 1: TEST THE HARD-CODED RULES ON THE DATASET
# ============================================================

df = pd.read_csv(DATA_FILE)

# The dataset we chose uses:
#   text  -> email content
#   label -> spam / ham
#
# If these columns are missing, print the available columns.
if "text" not in df.columns or "label" not in df.columns:
    raise ValueError(
        "Expected columns 'text' and 'label'. "
        f"Available columns: {list(df.columns)}"
    )

# Normalize the real labels
df["label"] = df["label"].astype(str).str.lower().str.strip()

# Apply our hard-coded detector
results = df["text"].apply(hardcoded_detector)

df["prediction"] = results.apply(lambda x: x[0])
df["matched_words"] = results.apply(lambda x: x[1])

# Compare our prediction with the real label
df["correct"] = df["prediction"] == df["label"]

accuracy = df["correct"].mean()

# False Positive:
# Real email = HAM, but our rule predicts SPAM
false_positives = df[
    (df["label"] == "ham") &
    (df["prediction"] == "spam")
]

# False Negative:
# Real email = SPAM, but our rule predicts HAM
false_negatives = df[
    (df["label"] == "spam") &
    (df["prediction"] == "ham")
]


print("=" * 60)
print("SECTION 1 - HARD-CODED RULE RESULTS")
print("=" * 60)

print(f"Total emails: {len(df)}")
print(f"Accuracy: {accuracy:.2%}")
print(f"False positives: {len(false_positives)}")
print(f"False negatives: {len(false_negatives)}")


# Show a few examples where the rules fail
print("\n" + "=" * 60)
print("FALSE POSITIVE EXAMPLES")
print("Actual = HAM, Prediction = SPAM")
print("=" * 60)

for _, row in false_positives.head(3).iterrows():
    print("\nMatched words:", row["matched_words"])
    print("Email preview:")
    print(str(row["text"])[:500])
    print("-" * 60)


print("\n" + "=" * 60)
print("FALSE NEGATIVE EXAMPLES")
print("Actual = SPAM, Prediction = HAM")
print("=" * 60)

for _, row in false_negatives.head(3).iterrows():
    print("\nMatched words:", row["matched_words"])
    print("Email preview:")
    print(str(row["text"])[:500])
    print("-" * 60)


# ============================================================
# PART 2: main.cpp DEMO FOR THE PRESENTATION
# ============================================================

# Example 1: intentionally spam-like promotional email
main_cpp_ad = """
Subject: CONGRATULATIONS! Join main.cpp for FREE!

Congratulations!

You have been selected to join main.cpp!

Join for FREE and work on exciting coding projects.
LIMITED TIME opportunity!
CLICK HERE to join today!
"""

# Example 2: normal email that contains the word "free"
main_cpp_normal = """
Subject: main.cpp Club Meeting

Hi everyone,

Are you free tomorrow?
We are having a main.cpp club meeting at 3 PM.

Thanks!
"""


print("\n" + "=" * 60)
print("main.cpp PROMOTIONAL EMAIL")
print("=" * 60)

prediction, matched_words = hardcoded_detector(main_cpp_ad)

print(main_cpp_ad)
print("Prediction:", prediction.upper())
print("Matched words:", matched_words)


print("\n" + "=" * 60)
print("NORMAL main.cpp EMAIL")
print("=" * 60)

prediction, matched_words = hardcoded_detector(main_cpp_normal)

print(main_cpp_normal)
print("Prediction:", prediction.upper())
print("Matched words:", matched_words)

print("\nExpected label: HAM")
print("Result: The detector incorrectly predicts SPAM because of 'free'.")


# ============================================================
# CONCLUSION
# ============================================================

print("\n" + "=" * 60)
print("LIMITATION")
print("=" * 60)

print(
    "Hard-coded rules are simple, but they do not understand context. "
    "A word such as 'free' can appear in both spam and normal emails. "
    "Therefore, hard-coded rules do not generalize well."
)
