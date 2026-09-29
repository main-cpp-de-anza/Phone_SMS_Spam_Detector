import re
import joblib

# ============================================================
# Engine 1: Hard-Coded Rules (Naive)
# ============================================================
SPAM_KEYWORDS = [
    "congratulations", "congratulation", "congrats", "free", "winner", 
    "won", "prize", "click here", "urgent", "claim", "buy now"
]

def detect_naive(text):
    text_lower = text.lower()
    for word in SPAM_KEYWORDS:
        if word in text_lower:
            return "SPAM"
    return "HAM"

# ============================================================
# Engine 2: SpamAssassin (Weighted Point Scoring)
# ============================================================
WORD_WEIGHTS = {
    # Spam signals (positive points)
    "free": 2.0, "winner": 3.0, "won": 2.5, "prize": 3.0, 
    "claim": 3.0, "urgent": 2.5, "cash": 2.5, "congratulations": 2.0,
    # Safe signals (negative points)
    "daughter": -4.0, "graduated": -3.5, "mom": -3.0, "dad": -3.0,
    "meeting": -3.0, "lunch": -2.5, "tomorrow": -2.0, "thanks": -2.0,
    "project": -2.5, "homework": -3.0, "team": -2.0
}

def detect_spamassassin(text, threshold=4.0):
    score = 0.0
    text_lower = text.lower()
    
    # Add/subtract points based on words
    for word, weight in WORD_WEIGHTS.items():
        if word in text_lower:
            score += weight
            
    # Check for excessive uppercase (shouting)
    if len(text) > 10 and sum(1 for c in text if c.isupper()) / len(text) > 0.4:
        score += 2.0
        
    return "SPAM" if score >= threshold else "HAM"

# ============================================================
# Engine 3: Machine Learning (LinearSVC Pipeline)
# ============================================================
MODEL_FILE = "model_linearsvc.joblib"
ml_model = joblib.load(MODEL_FILE)

def normalize_text(text):
    text = str(text).lower()
    text = re.sub(r'https?://\S+|www\.\S+|\b[a-zA-Z0-9.-]+\.(com|org|net|edu|gov|co|uk|io)\b', ' [url] ', text)
    text = re.sub(r'[$£€]\s?\d+(\.\d+)?|\b\d+\s?(k|m|million|billion)?\s?(dollars|pounds|cents|usd|euro)\b', ' [money] ', text)
    text = re.sub(r'\b\d+\s?(k|m)\b', ' [money] ', text)
    text = re.sub(r'\b\d{7,}\b|\b\d{3,}[-\s.]\d{3,}[-\s.]\d{3,}\b|\b0800\d+\b', ' [phone] ', text)
    text = re.sub(r'\b\d+\b', ' [number] ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def detect_machine_learning(text):
    cleaned = normalize_text(text)
    prediction = ml_model.predict([cleaned])[0]
    return prediction.upper()

# ============================================================
# Interactive Loop
# ============================================================
def main():
    print("=" * 50)
    print("Spam Detector Demo (Type 'e' to exit)")
    print("=" * 50)
    
    while True:
        user_input = input("\nEnter message: ")
        
        # Stop if user types 'e'
        if user_input.strip().lower() == 'e':
            print("Exiting program.")
            break
            
        if not user_input.strip():
            continue
            
        # Run all 3 detection engines
        res_naive = detect_naive(user_input)
        res_sa = detect_spamassassin(user_input)
        res_ml = detect_machine_learning(user_input)
        
        # Display results
        print("\nResults:")
        print(f"Naive            : {res_naive}")
        print(f"SpamAssassin     : {res_sa}")
        print(f"Machine Learning : {res_ml}")

if __name__ == "__main__":
    main()
