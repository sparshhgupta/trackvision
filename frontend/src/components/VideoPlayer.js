import React, { useRef, useState, useEffect } from 'react';
import './VideoPlayer.css';
import axios from "axios";

function VideoPlayer({ csvFile }) {
  const [streamSrc, setStreamSrc] = useState(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [showIdPopup, setShowIdPopup] = useState(false);
  const [csvUploaded, setCsvUploaded] = useState(false);
  const [currentId, setCurrentId] = useState("");
  const [newId, setNewId] = useState("");
  const [currentFrame, setCurrentFrame] = useState(0);
  const [frameData, setFrameData] = useState({
    frames: [],
    trackIds: []
  });
  const [currentTrackId, setCurrentTrackId] = useState(null);
  const [currentFrameIndex, setCurrentFrameIndex] = useState(-1);
  const [isProcessing, setIsProcessing] = useState(false);
  const streamRef = useRef(null);
  const frameUpdateInterval = useRef(null);

  useEffect(() => {
    setCsvUploaded(!!csvFile);
    if (csvFile) {
      fetchFrameNumbers();
    }
  }, [csvFile]);

  const fetchFrameNumbers = async () => {
    try {
      const response = await axios.get('http://127.0.0.1:5000/get-frame-numbers');
      if (response.data.end_frames && response.data.track_ids) {
        setFrameData({
          frames: response.data.end_frames,
          trackIds: response.data.track_ids
        });
        console.log("Fetched frame data:", response.data);
      }
    } catch (error) {
      console.error("Error fetching frame numbers:", error);
    }
  };

  const handleVideoUpload = async (event) => {
    const file = event.target.files[0];
    if (file && file.type.startsWith('video/')) {
      const formData = new FormData();
      formData.append('video', file);

      try {
        const response = await axios.post('http://127.0.0.1:5000/upload-video', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
        if (response.data.success) {
          // Start MJPEG stream instead of setting video source
          startMjpegStream();
          alert('Video uploaded successfully. Starting stream...');
        } else {
          alert('Error uploading video.');
        }
      } catch (error) {
        console.error('Video upload error:', error);
        alert('Error uploading video.');
      }
    } else {
      alert('Please upload a valid video file.');
    }
  };

  const startMjpegStream = () => {
    const timestamp = Date.now();
    setStreamSrc(`http://127.0.0.1:5000/mjpeg-stream?t=${timestamp}`);
    setIsStreaming(true);
    
    // Start periodic frame updates to track current frame
    startFrameTracking();
  };

  const startFrameTracking = () => {
    // Clear any existing interval first
    stopFrameTracking();
    
    // Poll backend for current frame information
    frameUpdateInterval.current = setInterval(async () => {
      try {
        const response = await axios.get('http://127.0.0.1:5000/current-frame');
        if (response.data.current_frame !== undefined && response.data.current_frame !== null) {
          setCurrentFrame(response.data.current_frame);
          updateCurrentFrameIndex(response.data.current_frame);
        }
      } catch (error) {
        console.error("Error fetching current frame:", error);
        // If we get persistent 400 errors, stop polling temporarily
        if (error.response && error.response.status === 400) {
          console.warn("Backend not ready, pausing frame tracking");
          stopFrameTracking();
          // Retry after 2 seconds
          setTimeout(() => {
            if (isStreaming && !isProcessing) {
              startFrameTracking();
            }
          }, 2000);
        }
      }
    }, 150); // Slightly slower polling to reduce load
  };

  const stopFrameTracking = () => {
    if (frameUpdateInterval.current) {
      clearInterval(frameUpdateInterval.current);
      frameUpdateInterval.current = null;
    }
  };
  
  const handleEditId = () => {
    setShowIdPopup(true);
    // Pause the stream tracking when editing
    stopFrameTracking();
  };

  const togglePlayPause = async () => {
    if (isProcessing) return; // Prevent double clicks
    
    setIsProcessing(true);
    try {
      const response = await axios.post('http://127.0.0.1:5000/toggle-playback');
      if (response.data.success) {
        setIsStreaming(response.data.is_playing);
        if (response.data.is_playing) {
          startFrameTracking();
        } else {
          stopFrameTracking();
        }
      }
    } catch (error) {
      console.error("Error toggling playback:", error);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleFrameSeek = async (frame) => {
    if (isProcessing) return; // Prevent multiple simultaneous seeks
    
    setIsProcessing(true);
    try {
      // Stop tracking before seeking
      stopFrameTracking();
      
      const response = await axios.post('http://127.0.0.1:5000/seek-frame', {
        frame: frame
      });
      
      if (response.data.success) {
        setCurrentFrame(frame);
        updateCurrentFrameIndex(frame);
        
        // Wait a moment for backend to process the seek
        await new Promise(resolve => setTimeout(resolve, 200));
        
        // Refresh stream to show new frame
        refreshStream();
        
        // Restart frame tracking after a short delay to ensure backend is ready
        setTimeout(() => {
          if (isStreaming && !isProcessing) {
            startFrameTracking();
          }
        }, 300);
      }
    } catch (error) {
      console.error("Error seeking frame:", error);
      // Restart tracking even if seek failed
      setTimeout(() => {
        if (isStreaming) {
          startFrameTracking();
        }
      }, 300);
    } finally {
      setTimeout(() => setIsProcessing(false), 500); // Ensure processing state is cleared
    }
  };

  const refreshStream = () => {
    if (streamRef.current) {
      const timestamp = Date.now();
      const baseUrl = `http://127.0.0.1:5000/mjpeg-stream`;
      streamRef.current.src = `${baseUrl}?t=${timestamp}`;
    }
  };

  const handleSaveId = async () => {
    try {
      const response = await axios.post('http://127.0.0.1:5000/update-id', {
        currentFrame: currentFrame,
        currentId: currentId,
        newId: newId,
      });
  
      if (response.data.success) {
        // Refresh the stream to show updated annotations
        refreshStream();
        alert("ID updated successfully and stream refreshed.");
        
        // Wait a moment then restart frame tracking
        setTimeout(() => {
          startFrameTracking();
        }, 200);
      } else {
        alert("Failed to update ID.");
      }
    } catch (error) {
      console.error("Error updating ID:", error);
      alert("Error updating ID.");
    }
  
    setShowIdPopup(false);
    setCurrentId("");
    setNewId("");
  };

  const updateCurrentFrameIndex = (frame) => {
    const index = frameData.frames.findIndex(f => f === frame);
    setCurrentFrameIndex(index);
    if (index >= 0) {
      setCurrentTrackId(frameData.trackIds[index]);
    } else {
      setCurrentTrackId(null);
    }
  };

  const navigateToFrame = (frame) => {
    handleFrameSeek(frame);
  };

  const navigatePrev = () => {
    if (frameData.frames.length === 0) {
      alert("No frame data available. Please upload a CSV file first.");
      return;
    }

    if (currentFrameIndex > 0) {
      // Move to previous frame in the array
      navigateToFrame(frameData.frames[currentFrameIndex - 1]);
    } else if (currentFrameIndex === 0) {
      // Already at first frame, optionally wrap to last frame
      navigateToFrame(frameData.frames[frameData.frames.length - 1]);
    } else {
      // currentFrameIndex is -1 (current frame not in array)
      // Find the closest previous frame in the array
      const closestPrevIndex = frameData.frames.findIndex(frame => frame >= currentFrame) - 1;
      if (closestPrevIndex >= 0) {
        navigateToFrame(frameData.frames[closestPrevIndex]);
      } else {
        // No previous frame found, go to last frame in array
        navigateToFrame(frameData.frames[frameData.frames.length - 1]);
      }
    }
  };

  const navigateNext = () => {
    if (frameData.frames.length === 0) {
      alert("No frame data available. Please upload a CSV file first.");
      return;
    }

    if (currentFrameIndex >= 0 && currentFrameIndex < frameData.frames.length - 1) {
      // Move to next frame in the array
      navigateToFrame(frameData.frames[currentFrameIndex + 1]);
    } else if (currentFrameIndex === frameData.frames.length - 1) {
      // Already at last frame, optionally wrap to first frame
      navigateToFrame(frameData.frames[0]);
    } else {
      // currentFrameIndex is -1 (current frame not in array)
      // Find the closest next frame in the array
      const closestNextIndex = frameData.frames.findIndex(frame => frame > currentFrame);
      if (closestNextIndex >= 0) {
        navigateToFrame(frameData.frames[closestNextIndex]);
      } else {
        // No next frame found, go to first frame in array
        navigateToFrame(frameData.frames[0]);
      }
    }
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopFrameTracking();
    };
  }, []);

  return (
    <div className="video-player">
      {!streamSrc && (
        <>
          <label htmlFor="video-upload" className="upload-btn">Upload Video</label>
          <input
            id="video-upload"
            type="file"
            accept="video/*"
            style={{ display: 'none' }}
            onChange={handleVideoUpload}
          />
        </>
      )}

      {streamSrc && (
        <div style={{ position: 'relative', width: '100%' }}>
          <img
            ref={streamRef}
            className="stream-element"
            src={streamSrc}
            alt="MJPEG Stream"
            style={{
              width: '100%',
              height: 'auto',
              maxHeight: '500px',
              border: '1px solid #ccc',
              filter: showIdPopup ? 'brightness(0.8)' : 'none'
            }}
            onError={(e) => {
              console.error("Stream error:", e);
              // Try to refresh the stream on error
              setTimeout(refreshStream, 1000);
            }}
          />
          {showIdPopup && <div className="dimming-overlay" />}
        </div>
      )}

      {streamSrc && (
        <div className="controls">
          <button onClick={togglePlayPause} disabled={isProcessing}>
            {isProcessing ? 'Processing...' : (isStreaming ? 'Pause Stream' : 'Resume Stream')}
          </button>
          <button onClick={refreshStream} style={{ marginLeft: '10px' }}>
            Refresh Stream
          </button>
          <div className="frame-info">
            <span>Frame: {currentFrame}</span>
            {currentTrackId !== null && (
              <span className="track-id">| Track ID: {currentTrackId}</span>
            )}
          </div>
        </div>
      )}

      {streamSrc && (
        <div className="frame-navigation">
          <button onClick={navigatePrev} disabled={isProcessing}>Previous Frame</button>
          <button onClick={navigateNext} disabled={isProcessing}>Next Frame</button>
          
          {/* Frame info display */}
          <div className="frame-info">
            {frameData.frames.length > 0 && (
              <>
                <span>Available frames: {frameData.frames.length} | </span>
                <span>
                  Position: {currentFrameIndex >= 0 ? currentFrameIndex + 1 : 'N/A'} of {frameData.frames.length}
                </span>
              </>
            )}
          </div>
          
          {/* Jump to specific frame from available frames */}
          <div className="frame-jump">
            <label>Jump to Frame: </label>
            <select 
              onChange={(e) => {
                const selectedFrame = parseInt(e.target.value);
                if (!isNaN(selectedFrame)) {
                  navigateToFrame(selectedFrame);
                }
              }}
              value={frameData.frames.includes(currentFrame) ? currentFrame : ''}
              style={{ marginLeft: '5px', padding: '2px' }}
            >
              <option value="">Select frame...</option>
              {frameData.frames.map((frame, index) => (
                <option key={index} value={frame}>
                  Frame {frame} (Track ID: {frameData.trackIds[index]})
                </option>
              ))}
            </select>
          </div>
          
          {/* Manual frame input */}
          <div className="frame-input">
            <label>Or enter frame number: </label>
            <input
              type="number"
              min="0"
              placeholder="Frame number"
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  const frame = parseInt(e.target.value);
                  if (!isNaN(frame) && frame >= 0) {
                    navigateToFrame(frame);
                    e.target.value = '';
                  }
                }
              }}
              style={{ marginLeft: '5px', width: '100px' }}
            />
          </div>
        </div>
      )}

      {/* <div className="save-download">
        <button
          onClick={() => {
            if (csvUploaded) {
              handleEditId();
            } else {
              alert("Please upload a CSV file first to enable editing.");
            }
          }}
          disabled={!csvUploaded}
        >
          Edit ID
        </button>
      </div> */}

      {/* {showIdPopup && (
        <div className="id-popup">
          <h3>Update ID</h3>
          <input
            type="text"
            placeholder="Current ID"
            value={currentId}
            onChange={(e) => setCurrentId(e.target.value)}
          />
          <input
            type="text"
            placeholder="New ID"
            value={newId}
            onChange={(e) => setNewId(e.target.value)}
          />
          <button onClick={handleSaveId}>Save ID</button>
          <button onClick={() => { 
            setShowIdPopup(false);
            startFrameTracking(); // Resume tracking when closing popup
          }}>Close</button>
        </div>
      )} */}
    </div>
  );
}

export default VideoPlayer;