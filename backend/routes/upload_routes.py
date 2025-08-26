from flask import Blueprint, request, jsonify, send_file
import os
import logging
from services.video_service import draw_bounding_boxes,draw_bounding_boxes_on_frame, convert_to_mp4
from utils.storage import video_storage

upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/upload-video', methods=['POST'])
def upload_video():
    try:
        video_file = request.files.get('video')
        if not video_file:
            return jsonify({'error': 'Video file is required'}), 400

        video_path = os.path.join('temp', video_file.filename)
        video_file.save(video_path)
        logging.info(f"Received video: {video_path}")

        video_storage['video_path'] = video_path
        return jsonify({'success': True}), 200
    except Exception as e:
        logging.error(f"Error in /upload-video: {e}")
        return jsonify({'error': str(e)}), 500

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




@upload_bp.route('/temp/<filename>', methods=['GET'])
def get_processed_video(filename):
    try:
        return send_file(os.path.join('temp', filename), as_attachment=False)
    except Exception as e:
        logging.error(f"Error serving video {filename}: {e}")
        return jsonify({'error': 'File not found'}), 404



# import cv2

# from flask import send_from_directory, jsonify

# def process_first_batch(video_path, csv_path, output_path, batch_size=100):
#     cap = cv2.VideoCapture(video_path)
#     frame_width, frame_height = int(cap.get(3)), int(cap.get(4))
#     fps = int(cap.get(cv2.CAP_PROP_FPS))
#     total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
#     cap.release()

#     fourcc = cv2.VideoWriter_fourcc(*'mp4v')
#     out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

#     for frame_idx in range(min(batch_size, total_frames)):
#         frame = draw_bounding_boxes_on_frame(video_path, csv_path, frame_idx)
#         out.write(frame)

#     out.release()


# def process_remaining_batches(video_path, csv_path, output_path, batch_size=100):
#     cap = cv2.VideoCapture(video_path)
#     total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
#     frame_width, frame_height = int(cap.get(3)), int(cap.get(4))
#     fps = int(cap.get(cv2.CAP_PROP_FPS))
#     cap.release()

#     fourcc = cv2.VideoWriter_fourcc(*'mp4v')
#     out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

#     # Skip first batch (already processed)
#     for start in range(batch_size, total_frames, batch_size):
#         end = min(start + batch_size, total_frames)
#         for frame_idx in range(start, end):
#             frame = draw_bounding_boxes_on_frame(video_path, csv_path, frame_idx)
#             out.write(frame)

#     out.release()
#     logging.info(f"Finished processing all {total_frames} frames.")


# VIDEO_OUTPUT_NAME = "processed_video.mp4"

# @upload_bp.route('/upload', methods=['POST'])
# def upload_files():
#     try:
#         csv_file = request.files.get('csv')
#         if not csv_file:
#             return jsonify({'error': 'CSV file is required'}), 400

#         csv_path = os.path.join('temp', csv_file.filename)
#         csv_file.save(csv_path)
#         logging.info(f"Received CSV: {csv_path}")

#         video_path = video_storage.get('video_path')
#         if not video_path or not os.path.exists(video_path):
#             return jsonify({'error': 'Video missing, upload via /upload-video first'}), 400

#         # Prepare output path
#         output_path = os.path.join("temp", VIDEO_OUTPUT_NAME)

#         # Process first batch immediately
#         process_first_batch(video_path, csv_path, output_path)

#         # Start background thread for remaining frames
#         import threading
#         threading.Thread(target=process_remaining_batches, args=(video_path, csv_path, output_path), daemon=True).start()

#         # Return the streaming URL instead of file
#         return jsonify({
#             "video_url": f"http://127.0.0.1:5000/video/{VIDEO_OUTPUT_NAME}"
#         })

#     except Exception as e:
#         logging.error(f"Error in /upload: {e}")
#         return jsonify({'error': f"Internal Server Error: {str(e)}"}), 500

# @upload_bp.route('/video/<path:filename>')
# def serve_video(filename):
#     return send_from_directory('temp', filename)
