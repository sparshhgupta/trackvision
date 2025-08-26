from flask import Blueprint, request, jsonify
import logging
import os
from services.csv_service import get_uploaded_csv_path, update_csv_ids
from services.video_service import process_video_with_updated_csv

update_bp = Blueprint('update', __name__)

@update_bp.route('/save-logs', methods=['POST'])
def save_logs():
    data = request.json
    logs = data.get("logs", [])
    if not logs:
        return jsonify({"message": "No logs received"}), 400

    csv_path = get_uploaded_csv_path()
    if not csv_path:
        return jsonify({'success': False, 'error': 'CSV file missing'}), 400

    for log in logs:
        old_id = log.get('A')
        new_id = log.get('B')
        update_csv_ids(csv_path, old_id, new_id)

    mp4_output_path, error = process_video_with_updated_csv(csv_path)
    if error:
        return jsonify({'success': False, 'error': error}), 400

    return jsonify({'success': True, 'new_video': os.path.basename(mp4_output_path)}), 200


@update_bp.route('/update-id', methods=['POST'])
def update_id():
    try:
        data = request.json
        current_id = data.get('currentId')
        new_id = data.get('newId')

        if not current_id or not new_id:
            return jsonify({'success': False, 'error': 'Invalid request data'}), 400

        csv_path = get_uploaded_csv_path()
        if not csv_path:
            return jsonify({'success': False, 'error': 'CSV missing'}), 400

        update_csv_ids(csv_path, current_id, new_id)

        mp4_output_path, error = process_video_with_updated_csv(csv_path)
        if error:
            return jsonify({'success': False, 'error': error}), 400

        return jsonify({'success': True, 'new_video': os.path.basename(mp4_output_path)}), 200
    except Exception as e:
        logging.error(f"Error in /update-id: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
