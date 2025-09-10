from flask import Blueprint, request, jsonify
import logging
import os
from services.csv_service import get_uploaded_csv_path, update_csv_ids, update_class_ids
from services.video_service import process_video_with_updated_csv
from services.stream_service import get_stream_processor

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
    
    stream_processor = get_stream_processor()

    # Update CSV with all log entries
    for log in logs:
        old_id = log.get('A')
        new_id = log.get('B')
        new_class_id = log.get('newClassId')
        if(new_class_id):
            update_class_ids(csv_path, old_id, new_class_id)
        if(new_id):
            if old_id in stream_processor.ids_to_display:
                stream_processor.ids_to_display.remove(old_id)
                stream_processor.ids_to_display.append(new_id)
            stream_processor.switch_mapping[old_id] = new_id;
            update_csv_ids(csv_path, old_id, new_id)
    
    

    # Update the stream processor with new CSV data
    if stream_processor:
        stream_processor.load_csv_data(csv_path)
        return jsonify({'success': True}), 200
    else:
        # Fallback to video processing if stream not available
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

        # Update CSV file
        update_csv_ids(csv_path, current_id, new_id)

        # Update the stream processor with new CSV data
        stream_processor = get_stream_processor()
        if stream_processor:
            stream_processor.load_csv_data(csv_path)
            return jsonify({'success': True}), 200
        else:
            # Fallback to video processing if stream not available
            mp4_output_path, error = process_video_with_updated_csv(csv_path)
            if error:
                return jsonify({'success': False, 'error': error}), 400
            return jsonify({'success': True, 'new_video': os.path.basename(mp4_output_path)}), 200

    except Exception as e:
        logging.error(f"Error in /update-id: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500