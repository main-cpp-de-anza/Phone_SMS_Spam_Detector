import re
import joblib
import numpy as np

# 1. Load the trained pipeline
MODEL_PATH = "model_linearsvc.joblib"
model = joblib.load(MODEL_PATH)

def normalize_message(text):
    text = str(text).lower()
    text = re.sub(r'https?://\S+|www\.\S+', ' [url] ', text)
    text = re.sub(r'[$£€]\d+(\.\d+)?|\b\d+\s?(dollars|pounds|cents|usd)\b', ' [money] ', text)
    text = re.sub(r'\b\d{7,}\b|\b\d{3,}[-\s]\d{3,}\b', ' [phone] ', text)
    text = re.sub(r'\b\d+\b', ' [number] ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def predict(text):
    cleaned = normalize_message(text)
    pred_num = model.predict([cleaned])[0]
    score = model.decision_function([cleaned])[0]
    # Sigmoid to convert score into 0% - 100% probability
    prob_spam = 1 / (1 + np.exp(-score))
    
    label = "SPAM" if pred_num == 1 else "HAM"
    return label, prob_spam, score

if __name__ == "__main__":
    print("=" * 60)
    print("📧 LIVE SPAM DETECTOR (Type 'exit' to quit)")
    print("=" * 60)
    
    while True:
        try:
            msg = input("\nEnter message: ")
            if msg.strip().lower() in ['exit', 'quit', 'q']:
                print("Exiting.")
                break
            if not msg.strip():
                continue
                
            label, prob, score = predict(msg)
            color = "\033[91m" if label == "SPAM" else "\033[92m" # Red or Green
            reset = "\033[0m"
            
            print(f"Prediction: {color}{label}{reset}")
            print(f"Spam Confidence: {prob * 100:.1f}%")
            print(f"Decision Margin: {score:+.2f}")
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break
