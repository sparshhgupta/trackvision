import os
import pandas as pd
import logging

def get_uploaded_csv_path():
    uploaded_csv = next((f for f in os.listdir('temp') if f.endswith('.csv')), None)
    return os.path.join('temp', uploaded_csv) if uploaded_csv else None

def update_csv_ids(csv_path, current_id, new_id):
    df = pd.read_csv(csv_path)
    df.loc[df['track_id'] == int(current_id), 'track_id'] = int(new_id)
    df.to_csv(csv_path, index=False)
    logging.info(f"Updated track_id {current_id} -> {new_id}")
