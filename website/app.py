import os
import re
import joblib
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ============================================================
# 1. Detection Engines (Exact mirror of Basic_Demo.py)
# ============================================================

# Engine 1: Hard-Coded Naive Keywords
SPAM_KEYWORDS = [
    "congratulations", "congratulation", "congrats", "free", "winner", 
    "won", "prize", "click here", "urgent", "claim", "buy now"
]

def detect_naive(text: str):
    text_lower = text.lower()
    matched = []
    for word in SPAM_KEYWORDS:
        if word in text_lower:
            matched.append(word)
    verdict = "SPAM" if len(matched) > 0 else "HAM"
    return {
        "verdict": verdict,
        "matched_keywords": matched
    }

# Engine 2: SpamAssassin (Point Scoring Dictionary)
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

def detect_spamassassin(text: str, threshold: float = 2.0):
    score = 0.0
    hits = []
    text_lower = text.lower()
    
    for phrase, points in RULE_POINTS.items():
        if phrase in text_lower:
            score += points
            hits.append({"phrase": phrase, "points": points})
            
    # Extra points for shouting (all-caps)
    is_shouting = False
    if len(text) > 10 and sum(1 for c in text if c.isupper()) / len(text) > 0.4:
        score += 2.0
        is_shouting = True
        hits.append({"phrase": "SHOUTING (ALL-CAPS)", "points": 2.0})
        
    verdict = "SPAM" if score >= threshold else "HAM"
    return {
        "verdict": verdict,
        "score": round(score, 2),
        "threshold": threshold,
        "hits": hits,
        "is_shouting": is_shouting
    }

# Engine 3: Machine Learning (LinearSVC Pipeline)
MODEL_PATH = os.path.join(os.path.dirname(__file__), "model_linearsvc.joblib")
if not os.path.exists(MODEL_PATH):
    # Local development fallback when the model remains in the repository root.
    MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "model_linearsvc.joblib")

ml_pipeline = joblib.load(MODEL_PATH)

def normalize_text(text: str) -> str:
    text = str(text).lower()
    text = re.sub(r'https?://\S+|www\.\S+|\b[a-zA-Z0-9.-]+\.(com|org|net|edu|gov|co|uk|io)\b', ' [url] ', text)
    text = re.sub(r'[$£€]\s?\d+(\.\d+)?|\b\d+\s?(k|m|million|billion)?\s?(dollars|pounds|cents|usd|euro)\b', ' [money] ', text)
    text = re.sub(r'\b\d+\s?(k|m)\b', ' [money] ', text)
    text = re.sub(r'\b\d{7,}\b|\b\d{3,}[-\s.]\d{3,}[-\s.]\d{3,}\b|\b0800\d+\b', ' [phone] ', text)
    text = re.sub(r'\b\d+\b', ' [number] ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def detect_machine_learning(text: str):
    cleaned = normalize_text(text)
    prediction = ml_pipeline.predict([cleaned])[0].upper()
    # LinearSVC decision function gives distance from hyperplane
    # Positive distance = spam, negative = ham
    decision_score = float(ml_pipeline.decision_function([cleaned])[0])
    
    # Calculate pseudo-probability via sigmoid for intuitive UI meter
    # P(spam) = 1 / (1 + exp(-decision_score))
    import math
    prob_spam = 1.0 / (1.0 + math.exp(-decision_score))
    
    return {
        "verdict": prediction,
        "decision_score": round(decision_score, 4),
        "spam_confidence_pct": round(prob_spam * 100, 1),
        "ham_confidence_pct": round((1.0 - prob_spam) * 100, 1),
        "cleaned_text": cleaned
    }

# ============================================================
# 2. FastAPI Application
# ============================================================
app = FastAPI(title="Phone SMS Spam Detector - Claude Style")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PredictRequest(BaseModel):
    text: str

@app.post("/predict")
@app.post("/api/predict")
def predict_endpoint(req: PredictRequest):
    if not req.text or not req.text.strip():
        raise HTTPException(status_code=400, detail="Empty text provided")
    
    raw = req.text.strip()
    res_naive = detect_naive(raw)
    res_sa = detect_spamassassin(raw)
    res_ml = detect_machine_learning(raw)
    
    return {
        "text": raw,
        "naive": res_naive,
        "spamassassin": res_sa,
        "machine_learning": res_ml
    }

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
def serve_index():
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "Website static files building..."}

if __name__ == "__main__":
    import uvicorn
    import sys
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    print("Starting Spam Detector website on http://127.0.0.1:8000 ...")
    uvicorn.run(app, host="127.0.0.1", port=8000)
