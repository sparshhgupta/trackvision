from flask import Blueprint, jsonify
import logging
from services.assessment_service import get_track_end_frames_with_ids
from services.csv_service import get_uploaded_csv_path

frame_bp = Blueprint('frame', __name__)

@frame_bp.route('/get-frame-numbers', methods=['GET'])
def get_frame_numbers():
    try:
        csv_path = get_uploaded_csv_path()
        if not csv_path:
            return jsonify({'error': 'CSV file not found'}), 400

        frames_data = get_track_end_frames_with_ids(csv_path)
        if not frames_data:
            return jsonify({'error': 'No tracks found in CSV'}), 400

        logging.info(f"End frames with IDs: {frames_data}")
        return jsonify({
            'end_frames': [frame for frame, _ in frames_data],
            'track_ids': [track_id for _, track_id in frames_data]
        })
    except Exception as e:
        logging.error(f"Error in /get-frame-numbers: {e}")
        return jsonify({'error': str(e)}), 500
