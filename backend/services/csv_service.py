import os
import pandas as pd
import logging
from flask import send_file

def get_uploaded_csv_path():
    uploaded_csv = next((f for f in os.listdir('temp') if f.endswith('.csv')), None)
    return os.path.join('temp', uploaded_csv) if uploaded_csv else None

def update_csv_ids(csv_path, current_id, new_id):
    df = pd.read_csv(csv_path)
    df.loc[df['track_id'] == int(current_id), 'track_id'] = int(new_id)
    df.to_csv(csv_path, index=False)
    logging.info(f"Updated track_id {current_id} -> {new_id}")

def update_class_ids(csv_path, old_id, new_class_id):
    df = pd.read_csv(csv_path)
    df.loc[df['track_id'] == int(old_id), 'class_id'] = int(new_class_id)
    df.to_csv(csv_path, index=False)
    logging.info(f"Updated class_id for track {old_id} -> {new_class_id}")

def download_updated_csv():
    """
    Returns the updated CSV file for download.
    """
    csv_path = get_uploaded_csv_path()
    if not csv_path or not os.path.exists(csv_path):
        logging.error("No updated CSV found in temp/")
        return None
    
    return send_file(
        csv_path,
        as_attachment=True,
        download_name="updated_annotations.csv",  # name shown to user
        mimetype="text/csv"
    )