import cv2
import pandas as pd
import logging
import os
import subprocess
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



                    #### CHANGES ####
def draw_bounding_boxes_on_frame(video_path, csv_path, frame_idx, save=False, output_dir="temp"):
    try:
        # Load bounding box data
        data = pd.read_csv(csv_path)

        # Open video
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Cannot open video {video_path}")

        # Jump directly to desired frame
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = cap.read()
        if not ret:
            raise ValueError(f"Cannot read frame {frame_idx} from {video_path}")

        # Get bounding boxes for this frame
        frame_boxes = data[data['frame'] == frame_idx]

        # Draw each bounding box
        for _, row in frame_boxes.iterrows():
            x1, y1, x2, y2 = map(int, [row['x1'], row['y1'], row['x2'], row['y2']])
            track_id, class_id, conf = row['track_id'], row['class_id'], row['confidence']
            color = (0, 255, 0)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            label = f'ID:{track_id}, Class:{class_id}, Conf:{conf:.2f}'
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

        cap.release()

        # Save or return
        if save:
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f"frame_{frame_idx}_processed.jpg")
            cv2.imwrite(output_path, frame)
            return output_path
        else:
            return frame  # returns numpy array (BGR)

    except Exception as e:
        logging.error(f"Frame processing error: {e}")
        raise


## USAGE

            # # Return numpy array of the processed frame
            # frame_img = draw_bounding_boxes_on_frame("video.mp4", "boxes.csv", frame_idx=100)

            # # OR save to file
            # output_path = draw_bounding_boxes_on_frame("video.mp4", "boxes.csv", frame_idx=100, save=True)
            # print("Saved:", output_path)
