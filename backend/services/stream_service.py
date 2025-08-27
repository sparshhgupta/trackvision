import cv2
import pandas as pd
import numpy as np
import threading
import time
import logging
from services.video_service import draw_bounding_boxes_on_frame

# Global stream processor instance
_stream_processor_instance = None
_instance_lock = threading.RLock()

class StreamProcessor:
    def __init__(self, video_path, csv_path=None):
        global _stream_processor_instance
        
        self.video_path = video_path
        self.csv_path = csv_path
        self.csv_data = None
        self.cap = None
        self.current_frame_idx = 0
        self.total_frames = 0
        self.is_playing_flag = False
        self.fps = 30
        
        # Use RLock for nested locking scenarios
        self.frame_lock = threading.RLock()
        self.video_lock = threading.RLock()
        self.csv_lock = threading.RLock()
        
        self.current_frame_image = None
        self.last_seek_frame = -1
        self.is_seeking = False
        
        # Initialize video capture
        self._initialize_video()
        
        # Load CSV data if provided
        if csv_path:
            self.load_csv_data(csv_path)
        
        # Set global instance with thread safety
        with _instance_lock:
            _stream_processor_instance = self
        
        logging.info(f"StreamProcessor initialized for {video_path}")
    
    def _initialize_video(self):
        """Initialize video capture with thread safety"""
        with self.video_lock:
            try:
                # Clean up existing capture if any
                if self.cap:
                    self.cap.release()
                
                self.cap = cv2.VideoCapture(self.video_path)
                if not self.cap.isOpened():
                    raise ValueError(f"Cannot open video {self.video_path}")
                
                # Set threading mode for OpenCV
                self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                
                self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
                self.fps = max(self.cap.get(cv2.CAP_PROP_FPS), 1.0)  # Ensure minimum FPS
                
                # Read first frame
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = self.cap.read()
                if ret:
                    self.current_frame_image = frame.copy()
                    self.current_frame_idx = 0
                else:
                    raise ValueError("Cannot read first frame from video")
                
                logging.info(f"Video initialized: {self.total_frames} frames at {self.fps} FPS")
            except Exception as e:
                logging.error(f"Error initializing video: {e}")
                if self.cap:
                    self.cap.release()
                    self.cap = None
                raise
    
    def load_csv_data(self, csv_path):
        """Load and update CSV data with thread safety"""
        with self.csv_lock:
            try:
                self.csv_path = csv_path
                self.csv_data = pd.read_csv(csv_path)
                logging.info(f"CSV data loaded: {len(self.csv_data)} rows")
                return True
            except Exception as e:
                logging.error(f"Error loading CSV data: {e}")
                self.csv_data = None
                return False
    
    def get_current_frame(self):
        """Get current frame number with thread safety"""
        with self.frame_lock:
            return self.current_frame_idx
    
    def get_total_frames(self):
        """Get total number of frames"""
        return self.total_frames
    
    def is_playing(self):
        """Check if stream is playing"""
        return self.is_playing_flag
    
    def toggle_playback(self):
        """Toggle play/pause state with thread safety"""
        with self.frame_lock:
            self.is_playing_flag = not self.is_playing_flag
            logging.info(f"Playback toggled: {self.is_playing_flag}")
            return self.is_playing_flag
    
    def seek_to_frame(self, frame_number):
        """Seek to specific frame with enhanced thread safety"""
        if frame_number < 0 or frame_number >= self.total_frames:
            logging.warning(f"Frame {frame_number} out of bounds (0-{self.total_frames-1})")
            return False
        
        with self.frame_lock:
            try:
                # Set seeking flag to prevent conflicts
                self.is_seeking = True
                
                # Pause playback during seeking
                was_playing = self.is_playing_flag
                self.is_playing_flag = False
                
                with self.video_lock:
                    if not self.cap or not self.cap.isOpened():
                        logging.error("Video capture not available")
                        return False
                    
                    # Seek to the frame
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
                    ret, frame = self.cap.read()
                    
                    if ret:
                        self.current_frame_image = frame.copy()
                        self.current_frame_idx = frame_number
                        self.last_seek_frame = frame_number
                        
                        logging.info(f"Successfully seeked to frame {frame_number}")
                        
                        # Restore playback state
                        self.is_playing_flag = was_playing
                        return True
                    else:
                        logging.error(f"Failed to read frame {frame_number}")
                        # Try to recover by seeking to a nearby frame
                        recovery_frame = max(0, frame_number - 1)
                        self.cap.set(cv2.CAP_PROP_POS_FRAMES, recovery_frame)
                        ret, frame = self.cap.read()
                        if ret:
                            self.current_frame_image = frame.copy()
                            self.current_frame_idx = recovery_frame
                            logging.info(f"Recovered by seeking to frame {recovery_frame}")
                        
                        self.is_playing_flag = was_playing
                        return False
                        
            except Exception as e:
                logging.error(f"Error seeking to frame {frame_number}: {e}")
                return False
            finally:
                self.is_seeking = False
    
    def get_frame_with_annotations(self, frame_idx=None):
        """Get frame with bounding box annotations with thread safety"""
        with self.frame_lock:
            try:
                target_frame = frame_idx if frame_idx is not None else self.current_frame_idx
                
                # If we're seeking or the requested frame is the last seeked frame, use cached frame
                if self.is_seeking or (self.current_frame_image is not None and target_frame == self.current_frame_idx):
                    frame = self.current_frame_image.copy()
                else:
                    # Need to read a different frame
                    with self.video_lock:
                        if self.cap and self.cap.isOpened():
                            current_pos = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
                            
                            # Only seek if we're not already at the target frame
                            if current_pos != target_frame:
                                self.cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
                            
                            ret, frame = self.cap.read()
                            if ret:
                                frame = frame.copy()
                                # Update cached frame if this is the current frame
                                if target_frame == self.current_frame_idx:
                                    self.current_frame_image = frame.copy()
                            else:
                                # Use cached frame as fallback
                                frame = self.current_frame_image.copy() if self.current_frame_image is not None else self._get_black_frame()
                        else:
                            frame = self.current_frame_image.copy() if self.current_frame_image is not None else self._get_black_frame()
                
                # Add bounding boxes if CSV data is available
                with self.csv_lock:
                    if self.csv_data is not None:
                        try:
                            frame = draw_bounding_boxes_on_frame(frame, self.csv_data, target_frame)
                        except Exception as e:
                            logging.warning(f"Error drawing bounding boxes: {e}")
                
                return frame
                
            except Exception as e:
                logging.error(f"Error getting frame {target_frame}: {e}")
                return self._get_black_frame()
    
    def _get_black_frame(self):
        """Get a black frame as fallback"""
        if self.current_frame_image is not None:
            h, w = self.current_frame_image.shape[:2]
            return np.zeros((h, w, 3), dtype=np.uint8)
        else:
            return np.zeros((480, 640, 3), dtype=np.uint8)
    
    def get_frame_generator(self):
        """Generator that yields JPEG encoded frames for MJPEG streaming"""
        frame_count = 0
        last_frame_time = time.time()
        
        while True:
            try:
                # Get current frame with annotations
                current_frame_idx = self.get_current_frame()
                frame = self.get_frame_with_annotations(current_frame_idx)
                
                # Encode frame as JPEG with error handling
                encode_params = [cv2.IMWRITE_JPEG_QUALITY, 85]
                ret, buffer = cv2.imencode('.jpg', frame, encode_params)
                
                if not ret:
                    logging.warning(f"Failed to encode frame {current_frame_idx} as JPEG")
                    # Create a simple error frame
                    error_frame = self._get_black_frame()
                    ret, buffer = cv2.imencode('.jpg', error_frame, encode_params)
                    if not ret:
                        time.sleep(0.1)
                        continue
                
                frame_bytes = buffer.tobytes()
                
                # Update current frame if playing (but not during seeking)
                if self.is_playing_flag and not self.is_seeking:
                    with self.frame_lock:
                        self.current_frame_idx += 1
                        if self.current_frame_idx >= self.total_frames:
                            self.current_frame_idx = 0  # Loop back to start
                
                yield frame_bytes
                
                # Control frame rate with adaptive timing
                current_time = time.time()
                if self.is_playing_flag and not self.is_seeking:
                    target_interval = 1.0 / self.fps
                    elapsed = current_time - last_frame_time
                    sleep_time = max(0, target_interval - elapsed)
                    if sleep_time > 0:
                        time.sleep(sleep_time)
                else:
                    time.sleep(0.05)  # Faster refresh when paused for responsiveness
                
                last_frame_time = current_time
                frame_count += 1
                
                # Log status periodically
                if frame_count % 300 == 0:  # Every ~10 seconds at 30fps
                    logging.debug(f"Stream generator: frame {current_frame_idx}, playing: {self.is_playing_flag}")
                
            except Exception as e:
                logging.error(f"Error in frame generator: {e}")
                time.sleep(0.1)
                continue
    
    def update_csv_id(self, frame_number, old_id, new_id):
        """Update ID in CSV data with thread safety"""
        with self.csv_lock:
            if self.csv_data is None:
                logging.warning("No CSV data available for ID update")
                return False
            
            try:
                # Find rows matching the frame and old ID
                mask = (self.csv_data['frame'] == frame_number) & (self.csv_data['id'] == old_id)
                matching_rows = self.csv_data[mask]
                
                if len(matching_rows) == 0:
                    logging.warning(f"No matching rows found for frame {frame_number} with ID {old_id}")
                    return False
                
                # Update the ID
                self.csv_data.loc[mask, 'id'] = new_id
                
                # Save the updated CSV
                if self.csv_path:
                    self.csv_data.to_csv(self.csv_path, index=False)
                    logging.info(f"Updated {len(matching_rows)} rows: changed ID from {old_id} to {new_id} at frame {frame_number}")
                
                return True
                
            except Exception as e:
                logging.error(f"Error updating CSV ID: {e}")
                return False
    
    def get_frame_data(self, frame_number):
        """Get data for a specific frame from CSV"""
        with self.csv_lock:
            if self.csv_data is None:
                return []
            
            try:
                frame_data = self.csv_data[self.csv_data['frame'] == frame_number]
                return frame_data.to_dict('records')
            except Exception as e:
                logging.error(f"Error getting frame data: {e}")
                return []
    
    def cleanup(self):
        """Clean up resources with thread safety"""
        with self.video_lock:
            with self.frame_lock:
                with self.csv_lock:
                    self.is_playing_flag = False
                    self.is_seeking = True  # Prevent any ongoing operations
                    
                    if self.cap:
                        try:
                            self.cap.release()
                        except Exception as e:
                            logging.error(f"Error releasing video capture: {e}")
                        finally:
                            self.cap = None
                    
                    self.current_frame_image = None
                    self.csv_data = None
                    
                    logging.info("StreamProcessor cleaned up")

def get_stream_processor():
    """Get the global stream processor instance with thread safety"""
    with _instance_lock:
        return _stream_processor_instance

def cleanup_stream_processor():
    """Clean up the global stream processor with thread safety"""
    global _stream_processor_instance
    with _instance_lock:
        if _stream_processor_instance:
            _stream_processor_instance.cleanup()
            _stream_processor_instance = None
            logging.info("Global stream processor cleaned up")

def create_stream_processor(video_path, csv_path=None):
    """Create a new stream processor instance"""
    global _stream_processor_instance
    with _instance_lock:
        # Clean up existing instance
        if _stream_processor_instance:
            cleanup_stream_processor()
        
        # Create new instance
        try:
            _stream_processor_instance = StreamProcessor(video_path, csv_path)
            return _stream_processor_instance
        except Exception as e:
            logging.error(f"Failed to create stream processor: {e}")
            return None