import io
import re
import urllib.request
import zipfile
import xml.etree.ElementTree as ET
import pandas as pd

UCI_URL = "https://raw.githubusercontent.com/thehananbhat/spam-vs-ham/main/spam.csv"
MENDELEY_URL = "https://raw.githubusercontent.com/MarazMia/SMISH_DT/main/Dataset/Mendeley_Dataset_5971.csv"
SMISHTANK_URL = "https://raw.githubusercontent.com/MarazMia/SMISH_DT/main/Dataset/smishtank.csv"
IMC25_URL = "https://raw.githubusercontent.com/reportsmishing/Smishing-Dataset-IMC25/main/dataset/final_dataset_output.csv"
NUS_URL = "https://raw.githubusercontent.com/kite1988/nus-sms-corpus/master/smsCorpus_en_xml_2015.03.09_all.zip"

OUTPUT_CSV = "data.csv"
OUTPUT_COMPAT_CSV = "spam_ham_dataset.csv"

def clean_phone_text(text):
    text = str(text).lower()
    # 0. Clean research placeholders from IMC25
    text = re.sub(r'<url>', ' [url] ', text)
    text = re.sub(r'<phone_number>', ' [phone] ', text)
    text = re.sub(r'<(credit_card|us_bank_number|crypto|mrp|epic)>', ' [money] ', text)
    text = re.sub(r'<[a-z_]+>', ' ', text)
    # 1. Normalize URLs and domains
    text = re.sub(r'https?://\S+|www\.\S+|\b[a-zA-Z0-9.-]+\.(com|org|net|edu|gov|co|uk|io)\b', ' [url] ', text)
    # 2. Normalize Currency (including 1k, 1m, 1 million dollars, $500, etc.)
    text = re.sub(r'[$£€]\s?\d+(\.\d+)?|\b\d+\s?(k|m|million|billion)?\s?(dollars|pounds|cents|usd|euro)\b', ' [money] ', text)
    text = re.sub(r'\b\d+\s?(k|m)\b', ' [money] ', text)
    # 3. Normalize Phone numbers and shortcodes
    text = re.sub(r'\b\d{7,}\b|\b\d{3,}[-\s.]\d{3,}[-\s.]\d{3,}\b|\b0800\d+\b', ' [phone] ', text)
    # 4. Normalize standalone numbers
    text = re.sub(r'\b\d+\b', ' [number] ', text)
    # 5. Clean whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def fetch_data():
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    # 1. UCI SMS Spam
    print("1/5 Fetching UCI SMS Spam dataset...")
    req1 = urllib.request.Request(UCI_URL, headers=headers)
    with urllib.request.urlopen(req1) as resp:
        df_uci = pd.read_csv(resp, encoding='latin-1', usecols=[0, 1])
    df_uci.columns = ['label', 'text']
    df_uci['label'] = df_uci['label'].str.lower().str.strip()
    
    # 2. Mendeley SMS Phishing
    print("2/5 Fetching Mendeley SMS Phishing dataset...")
    req2 = urllib.request.Request(MENDELEY_URL, headers=headers)
    with urllib.request.urlopen(req2) as resp:
        df_men = pd.read_csv(resp)
    df_men = df_men[['LABEL', 'TEXT']].rename(columns={'LABEL': 'label', 'TEXT': 'text'})
    df_men['label'] = df_men['label'].str.lower().str.strip().replace({'smishing': 'spam'})
    
    # 3. Smishtank Verified Phishing
    print("3/5 Fetching Smishtank verified smishing dataset...")
    req3 = urllib.request.Request(SMISHTANK_URL, headers=headers)
    with urllib.request.urlopen(req3) as resp:
        df_smish = pd.read_csv(resp, encoding='latin-1')
    df_smish = pd.DataFrame({'label': 'spam', 'text': df_smish['Fulltext'].dropna()})
    
    # 4. IMC 2025 ACM Smishing Dataset
    print("4/5 Fetching IMC 2025 verified SMS scam dataset...")
    req4 = urllib.request.Request(IMC25_URL, headers=headers)
    with urllib.request.urlopen(req4) as resp:
        df_imc = pd.read_csv(resp)
    df_imc_en = df_imc[df_imc['language'] == 'English'].dropna(subset=['text'])
    df_imc_clean = pd.DataFrame({'label': 'spam', 'text': df_imc_en['text']})
    
    # 5. NUS SMS Corpus (legitimate SMS donated by real users)
    print("5/5 Fetching NUS SMS human-donated legitimate dataset...")
    req5 = urllib.request.Request(NUS_URL, headers=headers)
    with urllib.request.urlopen(req5) as resp:
        z = zipfile.ZipFile(io.BytesIO(resp.read()))
        with z.open(z.namelist()[0]) as f:
            tree = ET.parse(f)
            root = tree.getroot()
            nus_texts = [msg.find('text').text for msg in root.findall('.//message') if msg.find('text') is not None and msg.find('text').text]
    df_nus = pd.DataFrame({'label': 'ham', 'text': nus_texts})
    
    combined = pd.concat([df_uci, df_men, df_smish, df_imc_clean, df_nus], ignore_index=True)
    return combined

def main():
    print("=" * 60)
    print("Building Multi-Source Verified Phone Spam & Scam Dataset")
    print("=" * 60)
    
    df_raw = fetch_data()
    print(f"\nTotal raw fetched: {len(df_raw)} messages.")
    
    # Clean text
    print("Applying phone text cleaning regex...")
    df_raw['clean_text'] = df_raw['text'].apply(clean_phone_text)
    
    # Deduplicate and remove empty
    df_clean = df_raw.dropna(subset=['clean_text']).drop_duplicates(subset=['clean_text']).reset_index(drop=True)
    df_clean = df_clean[df_clean['clean_text'].str.strip() != '']
    
    df_final = pd.DataFrame({
        'label': df_clean['label'],
        'text': df_clean['clean_text'],
        'label_num': df_clean['label'].map({'ham': 0, 'spam': 1})
    })
    
    print(f"\nFinal Cleaned & Deduplicated Count: {len(df_final)} messages")
    print("Class Distribution:")
    print(df_final['label'].value_counts())
    print(f"Ham ratio:  {(df_final['label']=='ham').mean():.2%}")
    print(f"Spam ratio: {(df_final['label']=='spam').mean():.2%}")
    
    df_final.to_csv(OUTPUT_CSV, index=False)
    df_final.to_csv(OUTPUT_COMPAT_CSV, index=False)
    print(f"\nSaved to '{OUTPUT_CSV}' and '{OUTPUT_COMPAT_CSV}' successfully.")

if __name__ == "__main__":
    main()
