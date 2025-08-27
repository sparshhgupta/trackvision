from flask import Blueprint, request, jsonify, send_file, Response
import os
import logging
from services.video_service import draw_bounding_boxes, convert_to_mp4, initialize_stream_processor
from services.stream_service import StreamProcessor
from utils.storage import video_storage

upload_bp = Blueprint('upload', __name__)
stream_processor = None

@upload_bp.route('/upload-video', methods=['POST'])
def upload_video():
    global stream_processor
    try:
        video_file = request.files.get('video')
        if not video_file:
            return jsonify({'error': 'Video file is required'}), 400

        video_path = os.path.join('temp', video_file.filename)
        video_file.save(video_path)
        logging.info(f"Received video: {video_path}")

        video_storage['video_path'] = video_path
        
        # Initialize stream processor for this video
        stream_processor = StreamProcessor(video_path)
        
        return jsonify({'success': True}), 200
    except Exception as e:
        logging.error(f"Error in /upload-video: {e}")
        return jsonify({'error': str(e)}), 500

@upload_bp.route('/upload-csv', methods=['POST'])
def upload_csv():
    global stream_processor
    try:
        csv_file = request.files.get('csv')
        if not csv_file:
            return jsonify({'error': 'CSV file is required'}), 400

        csv_path = os.path.join('temp', csv_file.filename)
        csv_file.save(csv_path)
        logging.info(f"Received CSV: {csv_path}")

        video_path = video_storage.get('video_path')
        if not video_path or not os.path.exists(video_path):
            return jsonify({'error': 'Video missing, upload via /upload-video first'}), 400

        # Initialize or update stream processor with CSV data
        if stream_processor is None:
            stream_processor = StreamProcessor(video_path, csv_path)
        else:
            stream_processor.load_csv_data(csv_path)

        return jsonify({'success': True}), 200
    except Exception as e:
        logging.error(f"Error in /upload-csv: {e}")
        return jsonify({'error': f"Internal Server Error: {str(e)}"}), 500

@upload_bp.route('/upload', methods=['POST'])
def upload_files():
    try:
        csv_file = request.files.get('csv')
        if not csv_file:
            return jsonify({'error': 'CSV file is required'}), 400

        csv_path = os.path.join('temp', csv_file.filename)
        csv_file.save(csv_path)
        logging.info(f"Received CSV: {csv_path}")

        video_path = video_storage.get('video_path')
        if not video_path or not os.path.exists(video_path):
            return jsonify({'error': 'Video missing, upload via /upload-video first'}), 400

        avi_output_path = draw_bounding_boxes(video_path, csv_path)
        mp4_output_path = avi_output_path.replace('.avi', '.mp4')
        convert_to_mp4(avi_output_path, mp4_output_path)

        return send_file(mp4_output_path, as_attachment=True)
    except Exception as e:
        logging.error(f"Error in /upload: {e}")
        return jsonify({'error': f"Internal Server Error: {str(e)}"}), 500

@upload_bp.route('/mjpeg-stream')
def mjpeg_stream():
    global stream_processor
    if stream_processor is None:
        return jsonify({'error': 'Stream not initialized'}), 400
    
    def generate():
        try:
            for frame in stream_processor.get_frame_generator():
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        except Exception as e:
            logging.error(f"Error in MJPEG stream: {e}")
    
    return Response(generate(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

import threading
from flask import jsonify, request
import logging

# Global lock for stream processor operations
stream_lock = threading.RLock()  # Using RLock to allow nested locking
logger = logging.getLogger(__name__)

@upload_bp.route('/toggle-playback', methods=['POST'])
def toggle_playback():
    global stream_processor
    
    with stream_lock:
        if stream_processor is None:
            return jsonify({'error': 'Stream not initialized'}), 400
        
        try:
            is_playing = stream_processor.toggle_playback()
            logger.info(f"Playback toggled: {is_playing}")
            return jsonify({
                'success': True,
                'is_playing': is_playing
            })
        except Exception as e:
            logger.error(f"Error toggling playback: {str(e)}")
            return jsonify({'error': f'Failed to toggle playback: {str(e)}'}), 500

@upload_bp.route('/seek-frame', methods=['POST'])
def seek_frame():
    global stream_processor
    
    with stream_lock:
        if stream_processor is None:
            return jsonify({'error': 'Stream not initialized'}), 400
        
        data = request.json
        frame_number = data.get('frame')
        
        if frame_number is None:
            return jsonify({'error': 'Frame number required'}), 400
        
        try:
            # Validate frame number
            if frame_number < 0:
                return jsonify({'error': 'Frame number must be non-negative'}), 400
            
            total_frames = stream_processor.get_total_frames()
            if total_frames and frame_number >= total_frames:
                return jsonify({'error': f'Frame number {frame_number} exceeds total frames {total_frames}'}), 400
            
            logger.info(f"Seeking to frame: {frame_number}")
            success = stream_processor.seek_to_frame(frame_number)
            
            if success:
                current_frame = stream_processor.get_current_frame()
                logger.info(f"Seek successful, current frame: {current_frame}")
                return jsonify({
                    'success': True,
                    'current_frame': current_frame
                })
            else:
                logger.warning(f"Seek to frame {frame_number} failed")
                return jsonify({
                    'success': False,
                    'error': f'Failed to seek to frame {frame_number}'
                }), 400
                
        except Exception as e:
            logger.error(f"Error seeking to frame {frame_number}: {str(e)}")
            return jsonify({'error': f'Seek operation failed: {str(e)}'}), 500

@upload_bp.route('/current-frame', methods=['GET'])
def get_current_frame():
    global stream_processor
    
    with stream_lock:
        if stream_processor is None:
            logger.warning("Current frame requested but stream not initialized")
            return jsonify({'error': 'Stream not initialized'}), 400
        
        try:
            current_frame = stream_processor.get_current_frame()
            total_frames = stream_processor.get_total_frames()
            is_playing = stream_processor.is_playing()
            
            # Validate that we got valid data
            if current_frame is None:
                logger.warning("Current frame is None")
                return jsonify({'error': 'Unable to get current frame'}), 400
            
            return jsonify({
                'current_frame': current_frame,
                'total_frames': total_frames,
                'is_playing': is_playing
            })
            
        except Exception as e:
            logger.error(f"Error getting current frame: {str(e)}")
            return jsonify({'error': f'Failed to get current frame: {str(e)}'}), 500

# Additional helper endpoint to check stream health
@upload_bp.route('/stream-status', methods=['GET'])
def get_stream_status():
    global stream_processor
    
    with stream_lock:
        if stream_processor is None:
            return jsonify({
                'initialized': False,
                'error': 'Stream not initialized'
            })
        
        try:
            return jsonify({
                'initialized': True,
                'is_playing': stream_processor.is_playing(),
                'current_frame': stream_processor.get_current_frame(),
                'total_frames': stream_processor.get_total_frames()
            })
        except Exception as e:
            logger.error(f"Error getting stream status: {str(e)}")
            return jsonify({
                'initialized': False,
                'error': str(e)
            })

@upload_bp.route('/temp/<filename>', methods=['GET'])
def get_processed_video(filename):
    try:
        return send_file(os.path.join('temp', filename), as_attachment=False)
    except Exception as e:
        logging.error(f"Error serving video {filename}: {e}")
        return jsonify({'error': 'File not found'}), 404
