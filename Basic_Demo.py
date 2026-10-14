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
    # Banking / Phishing
    "kyc": 3.5,
    "yono": 3.5,
    "hdfc": 3.0,
    "paytm": 3.0,
    "netbanking": 3.0,
    "pan card": 3.5,
    "pancard": 3.5,
    "sbi": 2.5,
    "icici": 2.5,
    "account blocked": 4.0,
    "account suspended": 4.0,
    "account locked": 3.5,
    "card blocked": 3.5,
    "security alert": 3.0,
    "unauthorized": 2.5,
    "unusual activity": 2.5,
    "verify your": 2.5,
    "update your": 2.0,
    "won": 2.0, 
    "free": 1.0,
    "bank account": 2.0,

    # Links & URLs
    "[url]": 2.0,
    "http://": 2.5,
    "https://": 2.5,
    "bit.ly": 2.5,
    "tinyurl": 2.5,
    "click here": 3.0,
    "click link": 3.0,
    "click the link": 3.0,
    "click url": 3.0,
    "tap here": 2.5,
    "visit": 1.0,

    # Delivery & Carriers
    "usps": 2.5,
    "fedex": 2.5,
    "dhl": 2.5,
    "parcel": 2.0,
    "package": 1.5,
    "stuck at transit": 3.5,
    "stuck": 2.0,
    "redelivery": 3.0,
    "customs fee": 3.0,
    "warehouse": 2.0,

    # Lottery, Prizes & Money
    "million dollars": 4.0,
    "lottery": 3.5,
    "jackpot": 3.5,
    "gift card": 3.5,
    "cash prize": 3.5,
    "prize": 2.5,
    "winner": 2.5,
    "congratulations": 2.0,
    "congratulation": 2.0,
    "claim": 2.0,
    "[money]": 1.0,
    "free entry": 3.5,
    "wkly comp": 3.5,

    # Urgent Actions & SMS Promos
    "urgent": 2.0,
    "immediately": 2.0,
    "action required": 3.0,
    "final notice": 3.0,
    "reply stop": 3.0,
    "text stop": 3.0,
    "txt stop": 3.0,
    "stop to cancel": 3.0,
    "[phone]": 1.0,
    "toll free": 2.0,
    "toll-free": 2.0,
    "customer care": 2.0,
    "helpline": 2.0,
    "dear customer": 2.5,
    "call now": 2.0,

    # Impersonation
    "smashed my phone": 4.0,
    "dropped my phone": 4.0,
    "lost my phone": 4.0,
    "this is my new number": 4.0,

    # Ham Indicators (Negative Points)
    "haha": -3.0,
    "hehe": -3.0,
    "lols": -2.5,
    "dun": -2.5,
    "lor": -2.5,
    "leh": -2.5,
    "lah": -2.5,
    "liao": -2.5,
    "dunno": -2.5,
    "okie": -2.5,
    "homework": -3.0,
    "prerequisites": -3.5,
    "assignment": -2.5,
    "lecture": -2.5,
    "graduated": -3.5,
    "lunch": -2.5,
    "dinner": -2.5,
    "breakfast": -2.0,
    "meeting": -2.0,
    "tomorrow": -2.0,
    "tonight": -1.5,
    "yesterday": -1.5,
    "how it's going": -2.0,
    "how are you": -2.0,
    "see you": -2.0,
    "love you": -2.0,
    "daughter": -3.0,
    "thanks": -1.5,
    "thank you": -1.5,
    "sorry": -1.5
}

def detect_spamassassin(text, threshold=2.0):
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
        print(f"Rule-Based       : {res_naive}")
        if sa_hits:
            hit_str = ", ".join(sa_hits)
            print(f"SpamAssassin     : {res_sa} (score: {sa_score:+.1f} | hits: {hit_str})")
        else:
            print(f"SpamAssassin     : {res_sa} (score: {sa_score:+.1f} | no rules hit)")
        print(f"Machine Learning : {res_ml}")

if __name__ == "__main__":
    main()
