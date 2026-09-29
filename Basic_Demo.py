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
# Engine 2: SpamAssassin (Simple Point Scoring)
# ============================================================
RULE_POINTS = {
    "million dollars": 4.0,
    "lottery": 3.5,
    "prize": 3.0,
    "winner": 2.5,
    "locked": 2.5,
    "suspended": 2.5,
    "alert": 1.5,
    "bit.ly": 2.5,
    "tinyurl": 2.5,
    "stuck": 2.5,
    "parcel": 2.0,
    "package": 2.0,
    "gift card": 3.5,
    "smashed my phone": 4.0,
    "dropped my phone": 4.0,
    "urgent": 2.0,
    "claim": 2.0,
    "free": 1.5,

    "graduated": -3.5,
    "daughter": -3.0,
    "prerequisites": -3.5,
    "homework": -3.0,
    "lunch": -2.5,
    "dinner": -2.5,
    "meeting": -2.0,
    "tomorrow": -2.0,
    "how it's going": -2.0,
    "how are you": -2.0
}

def detect_spamassassin(text, threshold=4.0):
    score = 0.0
    hits = []
    text_lower = text.lower()
    
    # 1. Add or subtract points for matching words / phrases
    for phrase, points in RULE_POINTS.items():
        if phrase in text_lower:
            score += points
            hits.append(f"{phrase} ({points:+})")
            
    # 2. Extra points for shouting (all-caps)
    if len(text) > 10 and sum(1 for c in text if c.isupper()) / len(text) > 0.4:
        score += 2.0
        hits.append("SHOUTING (+2.0)")
        
    verdict = "SPAM" if score >= threshold else "HAM"
    return verdict, score, hits

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
    print("=" * 60)
    print("Spam & Scam Detector Demo (Type 'e' to exit)")
    print("=" * 60)
    
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
        res_sa, sa_score, sa_hits = detect_spamassassin(user_input)
        res_ml = detect_machine_learning(user_input)
        
        # Display results
        print("\nResults:")
        print(f"Naive            : {res_naive}")
        if sa_hits:
            hit_str = ", ".join(sa_hits)
            print(f"SpamAssassin     : {res_sa} (score: {sa_score:+.1f} | hits: {hit_str})")
        else:
            print(f"SpamAssassin     : {res_sa} (score: {sa_score:+.1f} | no rules hit)")
        print(f"Machine Learning : {res_ml}")

if __name__ == "__main__":
    main()
