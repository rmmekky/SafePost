import pandas as pd
from datetime import datetime

CSV_FILE = "data.csv"

def init_csv():
    try:
        pd.read_csv(CSV_FILE)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["Input", "Classification", "Timestamp"])
        df.to_csv(CSV_FILE, index=False)

def save_to_csv(text, classification):
    df = pd.read_csv(CSV_FILE)
    new_row = {"Input": text, "Classification": classification, "Timestamp": datetime.now()}
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)

def load_csv():
    return pd.read_csv(CSV_FILE)