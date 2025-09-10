import cv2
import pandas as pd
import logging
import os
import subprocess
import numpy as np
from utils.storage import video_storage

def draw_bounding_boxes(video_path, csv_path):
    try:
        data = pd.read_csv(csv_path)
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Cannot open video {video_path}")

        frame_width, frame_height = int(cap.get(3)), int(cap.get(4))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        output_path = os.path.join('temp', os.path.basename(video_path).replace('.mp4', '_processed.avi'))

        out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))
        frame_idx = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break

            frame_boxes = data[data['frame'] == frame_idx]
            for _, row in frame_boxes.iterrows():
                x1, y1, x2, y2 = map(int, [row['x1'], row['y1'], row['x2'], row['y2']])
                track_id, class_id, conf = row['track_id'], row['class_id'], row['confidence']
                color = (0, 255, 0)
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                label = f'ID:{track_id}, Class:{class_id}, Conf:{conf:.2f}'
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

            out.write(frame)
            frame_idx += 1

        cap.release()
        out.release()
        return output_path
    except Exception as e:
        logging.error(f"Video processing error: {e}")
        raise

# def draw_bounding_boxes_on_frame(frame, frame_data, frame_idx):
#     """Draw bounding boxes on a single frame"""
#     try:
#         if frame_data is None or frame_data.empty:
#             return frame
        
#         # Filter data for current frame
#         frame_boxes = frame_data[frame_data['frame'] == frame_idx]
        
#         for _, row in frame_boxes.iterrows():
#             try:
#                 x1, y1, x2, y2 = map(int, [row['x1'], row['y1'], row['x2'], row['y2']])
#                 track_id = row['track_id']
#                 class_id = row.get('class_id', 0)
#                 conf = row.get('confidence', 1.0)
                
#                 # Choose color based on track_id for consistency
#                 colors = [(0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]
#                 # color = colors[int(track_id) % len(colors)]
#                 color = (0, 255, 0)
                
#                 # Draw rectangle
#                 cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                
#                 # Draw label
#                 label = f'ID:{track_id}, Class:{class_id}, Conf:{conf:.2f}'
#                 label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
                
#                 # Background rectangle for text
#                 cv2.rectangle(frame, (x1, y1 - label_size[1] - 10), 
#                              (x1 + label_size[0], y1), (255, 255, 255), -1)
#                 # Text
#                 cv2.putText(frame, label, (x1, y1 - 5), 
#                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
#             except Exception as e:
#                 logging.warning(f"Error drawing box for row {row}: {e}")
#                 continue
                
#         return frame
#     except Exception as e:
#         logging.error(f"Error drawing bounding boxes on frame: {e}")
#         return frame

def draw_bounding_boxes_on_frame(frame, frame_data, frame_idx, display_all_ids=True, ids_to_display=[], filter_mode='include'):
    """
    Draw bounding boxes on a single frame with ID filtering support
    
    Args:
        frame: The video frame to draw on
        frame_data: DataFrame containing bounding box data
        frame_idx: Current frame index
        display_all_ids: Boolean, if True displays all IDs, if False filters by ids_to_display
        ids_to_display: List of specific track_ids to display when display_all_ids is False
        filter_mode: 'include' or 'exclude' mode for filtering IDs
    
    Returns:
        Frame with bounding boxes drawn
    """
    try:
        if frame_data is None or frame_data.empty:
            return frame
        
        # Filter data for current frame
        frame_boxes = frame_data[frame_data['frame'] == frame_idx]
        
        # Apply ID filtering if display_all_ids is False
        if not display_all_ids:
            if not ids_to_display:  # If array is empty, show nothing
                return frame
            
            # Filter to only show specific track_ids
            if 'track_id' in frame_boxes.columns:
                # Debug: Log what we're working with
                if not frame_boxes.empty:
                    logging.info(f"Sample track_id from data: {frame_boxes['track_id'].iloc[0]} (type: {type(frame_boxes['track_id'].iloc[0])})")
                    logging.info(f"Unique track_ids in frame {frame_idx}: {frame_boxes['track_id'].unique().tolist()}")
                
                # Convert ids_to_display to both string and numeric formats
                string_ids = [str(id_val).strip() for id_val in ids_to_display]
                numeric_ids = []
                
                for id_val in ids_to_display:
                    try:
                        # Try to convert to int first, then float
                        if '.' in str(id_val):
                            numeric_ids.append(float(str(id_val).strip()))
                        else:
                            numeric_ids.append(int(str(id_val).strip()))
                    except (ValueError, TypeError):
                        logging.warning(f"Could not convert ID '{id_val}' to numeric")
                        continue
                
                logging.info(f"String IDs for filtering: {string_ids}")
                logging.info(f"Numeric IDs for filtering: {numeric_ids}")
                
                # Filter using both string and numeric comparisons
                mask = (
                    frame_boxes['track_id'].astype(str).str.strip().isin(string_ids) |
                    frame_boxes['track_id'].isin(numeric_ids)
                )
                
                # Apply include or exclude logic
                if filter_mode == 'include':
                    frame_boxes = frame_boxes[mask]
                elif filter_mode == 'exclude':
                    frame_boxes = frame_boxes[~mask]
                else:
                    logging.warning(f"Invalid filter_mode '{filter_mode}', using 'include' as default")
                    frame_boxes = frame_boxes[mask]
                
                logging.info(f"After {filter_mode} filtering: {len(frame_boxes)} boxes remaining")
                
            else:
                logging.warning("'track_id' column not found in frame data")
                return frame
        
        # Debug logging to help troubleshoot
        # logging.info(f"Frame {frame_idx}: display_all_ids={display_all_ids}, ids_to_display={ids_to_display}")
        # logging.info(f"Frame {frame_idx}: Found {len(frame_boxes)} boxes after filtering")
        
        # Draw bounding boxes for filtered data
        for _, row in frame_boxes.iterrows():
            try:
                x1, y1, x2, y2 = map(int, [row['x1'], row['y1'], row['x2'], row['y2']])
                track_id = row['track_id']
                class_id = row.get('class_id', 0)
                conf = row.get('confidence', 1.0)
                
                # Choose color based on track_id for consistency
                colors = [(0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]
                color = colors[int(track_id) % len(colors)] if isinstance(track_id, (int, float)) else (0, 255, 0)
                
                # Draw rectangle
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                
                # Draw label
                label = f'ID:{track_id}, Class:{class_id}, Conf:{conf:.2f}'
                label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
                
                # Background rectangle for text
                cv2.rectangle(frame, (x1, y1 - label_size[1] - 10), 
                             (x1 + label_size[0], y1), (255, 255, 255), -1)
                # Text
                cv2.putText(frame, label, (x1, y1 - 5), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
                
            except Exception as e:
                logging.warning(f"Error drawing box for row {row}: {e}")
                continue
                
        return frame
        
    except Exception as e:
        logging.error(f"Error drawing bounding boxes on frame: {e}")
        return frame

# def draw_bounding_boxes_on_frame(frame, frame_data, frame_idx, display_all_ids=True, ids_to_display=[]):
#     """
#     Draw bounding boxes on a single frame with ID filtering support
    
#     Args:
#         frame: The video frame to draw on
#         frame_data: DataFrame containing bounding box data
#         frame_idx: Current frame index
#         display_all_ids: Boolean, if True displays all IDs, if False filters by ids_to_display
#         ids_to_display: List of specific track_ids to display when display_all_ids is False
    
#     Returns:
#         Frame with bounding boxes drawn
#     """
#     try:
#         if frame_data is None or frame_data.empty:
#             return frame
        
#         # Filter data for current frame
#         frame_boxes = frame_data[frame_data['frame'] == frame_idx]
        
#         # Apply ID filtering if display_all_ids is False
#         if not display_all_ids:
#             if not ids_to_display:  # If array is empty, show nothing
#                 return frame
            
#             # Filter to only show specific track_ids
#             if 'track_id' in frame_boxes.columns:
#                 # Debug: Log what we're working with
#                 if not frame_boxes.empty:
#                     logging.info(f"Sample track_id from data: {frame_boxes['track_id'].iloc[0]} (type: {type(frame_boxes['track_id'].iloc[0])})")
#                     logging.info(f"Unique track_ids in frame {frame_idx}: {frame_boxes['track_id'].unique().tolist()}")
                
#                 # Convert ids_to_display to both string and numeric formats
#                 string_ids = [str(id_val).strip() for id_val in ids_to_display]
#                 numeric_ids = []
                
#                 for id_val in ids_to_display:
#                     try:
#                         # Try to convert to int first, then float
#                         if '.' in str(id_val):
#                             numeric_ids.append(float(str(id_val).strip()))
#                         else:
#                             numeric_ids.append(int(str(id_val).strip()))
#                     except (ValueError, TypeError):
#                         logging.warning(f"Could not convert ID '{id_val}' to numeric")
#                         continue
                
#                 logging.info(f"String IDs for filtering: {string_ids}")
#                 logging.info(f"Numeric IDs for filtering: {numeric_ids}")
                
#                 # Filter using both string and numeric comparisons
#                 mask = (
#                     frame_boxes['track_id'].astype(str).str.strip().isin(string_ids) |
#                     frame_boxes['track_id'].isin(numeric_ids)
#                 )
                
#                 frame_boxes = frame_boxes[mask]
#                 logging.info(f"After filtering: {len(frame_boxes)} boxes remaining")
                
#             else:
#                 logging.warning("'track_id' column not found in frame data")
#                 return frame
        
#         # Debug logging to help troubleshoot
#         # logging.info(f"Frame {frame_idx}: display_all_ids={display_all_ids}, ids_to_display={ids_to_display}")
#         # logging.info(f"Frame {frame_idx}: Found {len(frame_boxes)} boxes after filtering")
        
#         # Draw bounding boxes for filtered data
#         for _, row in frame_boxes.iterrows():
#             try:
#                 x1, y1, x2, y2 = map(int, [row['x1'], row['y1'], row['x2'], row['y2']])
#                 track_id = row['track_id']
#                 class_id = row.get('class_id', 0)
#                 conf = row.get('confidence', 1.0)
                
#                 # Choose color based on track_id for consistency
#                 colors = [(0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]
#                 color = colors[int(track_id) % len(colors)] if isinstance(track_id, (int, float)) else (0, 255, 0)
                
#                 # Draw rectangle
#                 cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                
#                 # Draw label
#                 label = f'ID:{track_id}, Class:{class_id}, Conf:{conf:.2f}'
#                 label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
                
#                 # Background rectangle for text
#                 cv2.rectangle(frame, (x1, y1 - label_size[1] - 10), 
#                              (x1 + label_size[0], y1), (255, 255, 255), -1)
#                 # Text
#                 cv2.putText(frame, label, (x1, y1 - 5), 
#                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
                
#             except Exception as e:
#                 logging.warning(f"Error drawing box for row {row}: {e}")
#                 continue
                
#         return frame
        
#     except Exception as e:
#         logging.error(f"Error drawing bounding boxes on frame: {e}")
#         return frame

def convert_to_mp4(avi_path, mp4_path):
    try:
        cmd = ['ffmpeg', '-i', avi_path, '-c:v', 'libx264', '-preset', 'fast',
               '-crf', '23', '-c:a', 'aac', '-strict', 'experimental', mp4_path]
        subprocess.run(cmd, check=True)
        logging.info(f"Converted AVI to MP4: {mp4_path}")
    except subprocess.CalledProcessError:
        raise ValueError("AVI to MP4 conversion failed")

def process_video_with_updated_csv(csv_path):
    video_path = video_storage.get('video_path')
    if not video_path or not os.path.exists(video_path):
        return None, "Video missing"

    avi_output_path = draw_bounding_boxes(video_path, csv_path)
    mp4_output_path = avi_output_path.replace('.avi', '.mp4')
    convert_to_mp4(avi_output_path, mp4_output_path)

    if not os.path.exists(mp4_output_path):
        return None, "Processed MP4 missing"
    return mp4_output_path, None

def initialize_stream_processor(video_path, csv_path=None):
    """Initialize stream processor - this function can be called from upload routes"""
    from services.stream_service import StreamProcessor
    return StreamProcessor(video_path, csv_path)