# Phone_SMS_Spam_Detector

## Model Comparison

![Model Comparison Results](images/model_comparison.png)

LinearSVC has higest Accuracy (98.84%) and F1 Score (95.25%), missing 51 spam messages compared to 120 (Logistic), 233 (Naive Bayes), and 300 (KNN).

---
## Run Demo
```bash
python Basic_Demo.py
```

---

## Datasets 

* [UCI SMS Spam Collection](https://archive.ics.uci.edu/dataset/228/sms+spam+collection)
* [Mendeley SMS Phishing Dataset](https://data.mendeley.com/datasets/f45bk47ycf/1)
* [Smishtank Phishing Corpus (SMISH_DT)](https://github.com/MarazMia/SMISH_DT)
* [IMC 2025 ACM Smishing Dataset](https://github.com/reportsmishing/Smishing-Dataset-IMC25)
* [NUS SMS Corpus](https://github.com/kite1988/nus-sms-corpus)

---

## Data Cleaning

### Cleaning Steps:
* **lowercase**: converts all letters to lowercase.
* **links**: replaces websites, domains, and shortened links with `[url]`.
* **money**: replaces currency symbols, amounts, and phrases (`$500`, `1k`, `1 million dollars`) with `[money]`.
* **phone numbers**: replaces phone numbers and shortcodes with `[phone]`.
* **numbers**: replaces standalone numbers with `[number]`.
* **spaces**: removes extra whitespaces and strips edges.
* **remove duplicates**: drops exact duplicate texts.

---

### Before vs After Cleaning Examples

#### Example 1: Lottery / Prize Scam
* **Before:**
  ```text
  CONGRATULATION, you just won $500 cash! Visit bit.ly/claim or call 800-555-0199 now!
  ```
* **After:**
  ```text
  congratulation, you just won [money] cash! visit [url] or call [phone] now!
  ```

#### Example 2: Package Delivery Scam (Smishing)
* **Before:**
  ```text
  USPS alert: Your package is stuck at transit. Pay 15 dollars fee at https://usps-redelivery.com/pay
  ```
* **After:**
  ```text
  usps alert: your package is stuck at transit. pay [money] fee at [url]
  ```

#### Example 3: Normal Message (Ham)
* **Before:**
  ```text
  Hey Mom, are we meeting for lunch at 12:30 tomorrow?
  ```
* **After:**
  ```text
  hey mom, are we meeting for lunch at [number]:[number] tomorrow?
  ```