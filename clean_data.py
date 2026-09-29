import os
import io
import re
import urllib.request
import pandas as pd

RAW_DATA_URL = "https://huggingface.co/datasets/puyang2025/seven-phishing-email-datasets/resolve/main/test.parquet"
OUTPUT_CSV = "data.csv"
OUTPUT_COMPAT_CSV = "spam_ham_dataset.csv"

def download_raw_data():
    raw_cache = "raw_emails.parquet"
    if os.path.exists(raw_cache):
        print(f"Loading cached raw file '{raw_cache}'...")
        return pd.read_parquet(raw_cache)
        
    print(f"Downloading dataset from Hugging Face: {RAW_DATA_URL} ...")
    req = urllib.request.Request(RAW_DATA_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as resp:
        content = resp.read()
        
    with open(raw_cache, "wb") as f:
        f.write(content)
        
    print(f"Saved raw cache to '{raw_cache}' ({len(content)/1024/1024:.2f} MB).")
    return pd.read_parquet(io.BytesIO(content))

def clean_text(text):
    text = str(text).lower()
    
    # 1. Normalize URLs and domains
    text = re.sub(r'https?://\S+|www\.\S+|\b[a-zA-Z0-9.-]+\.(com|org|net|edu|gov|co|uk|io)\b', ' [url] ', text)
    
    # 2. Normalize Currency (including slang 1k, 1m, 1 million dollars, $500, etc.)
    text = re.sub(r'[$£€]\s?\d+(\.\d+)?|\b\d+\s?(k|m|million|billion)?\s?(dollars|pounds|cents|usd|euro)\b', ' [money] ', text)
    text = re.sub(r'\b\d+\s?(k|m)\b', ' [money] ', text)
    
    # 3. Normalize Phone numbers
    text = re.sub(r'\b\d{7,}\b|\b\d{3,}[-\s.]\d{3,}[-\s.]\d{3,}\b|\b0800\d+\b', ' [phone] ', text)
    
    # 4. Normalize Numbers
    text = re.sub(r'\b\d+\b', ' [number] ', text)
    
    # 5. Clean whitespace and non-ascii artifacts
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def main():
    print("=" * 60)
    print("Email Spam & Phishing Dataset Cleaning Pipeline")
    print("=" * 60)
    
    df_raw = download_raw_data()
    print(f"Raw dataset shape: {df_raw.shape}")
    print(f"Sources included: {df_raw['dataset_name'].value_counts().to_dict()}")
    
    # Combine subject and body text for realistic email structure
    subject = df_raw['subject'].fillna('').astype(str)
    body = df_raw['text'].fillna('').astype(str)
    full_email = "Subject: " + subject + " " + body
    
    # Map label (0 = ham, 1 = spam)
    labels = df_raw['label'].map({0: 'ham', 1: 'spam'})
    labels_num = df_raw['label'].astype(int)
    
    print("\nCleaning text with regex tokenization ([url], [money], [phone], [number])...")
    cleaned_texts = full_email.apply(clean_text)
    
    df_clean = pd.DataFrame({
        'label': labels,
        'text': cleaned_texts,
        'label_num': labels_num
    })
    
    # Drop empty texts and duplicates
    initial_len = len(df_clean)
    df_clean = df_clean[df_clean['text'].str.strip() != '']
    df_clean = df_clean.drop_duplicates(subset=['text']).reset_index(drop=True)
    print(f"Removed {initial_len - len(df_clean)} duplicates / empty entries.")
    
    print("\nCleaned Class Distribution:")
    print(df_clean['label'].value_counts())
    print(f"Ham ratio:  {(df_clean['label']=='ham').mean():.2%}")
    print(f"Spam ratio: {(df_clean['label']=='spam').mean():.2%}")
    
    # Save clean dataset
    df_clean.to_csv(OUTPUT_CSV, index=False)
    df_clean.to_csv(OUTPUT_COMPAT_CSV, index=False)
    print(f"\nSaved cleaned dataset to '{OUTPUT_CSV}' and '{OUTPUT_COMPAT_CSV}' ({os.path.getsize(OUTPUT_CSV)/1024/1024:.2f} MB).")
    
    print("\nSample Cleaned Emails:")
    for i, row in df_clean.head(2).iterrows():
        print(f"[{row['label'].upper()}] {row['text'][:140]}...")

if __name__ == "__main__":
    main()
