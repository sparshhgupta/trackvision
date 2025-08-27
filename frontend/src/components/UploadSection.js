import React, { useState, useEffect } from "react";
import axios from 'axios';

// frame_numbers = [30, 40, 50];
let exportedFrameNumbers = [];

function UploadSection({ csvFile, onCsvUpload }) {
  const [csvUploaded, setCsvUploaded] = useState(false);
  const [logEntries, setLogEntries] = useState([]);
  const [frameNumber, setFrameNumber] = useState("");
  const [A, setA] = useState("");
  const [B, setB] = useState("");
  const [streamActive, setStreamActive] = useState(false);

  useEffect(() => {
    setCsvUploaded(!!csvFile);
  }, [csvFile]);

  const fetchFrameNumbers = async () => {
    try {
      const response = await axios.get('http://127.0.0.1:5000/get-frame-numbers');
      if (response.data?.end_frames) {
        exportedFrameNumbers = response.data.end_frames; // Update exported variable
        alert(`Received frames: ${exportedFrameNumbers.join(', ')}`);
      }
    } catch (error) {
      console.error('Error fetching frames:', error);
    }
  };

  const startMjpegStream = () => {
    const mjpegContainer = document.querySelector('#mjpeg-container');
    if (mjpegContainer) {
      const timestamp = Date.now();
      mjpegContainer.innerHTML = `
        <img 
          src="http://127.0.0.1:5000/mjpeg-stream?t=${timestamp}" 
          alt="MJPEG Stream" 
          data-mjpeg-stream="true"
          style="max-width: 100%; height: auto; border: 1px solid #ccc;"
          onload="this.style.opacity = '1'"
          onerror="console.error('MJPEG stream error')"
        />
      `;
      setStreamActive(true);
    }
  };

  const handleCsvUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    if (file.type !== 'text/csv') {
      alert('Please upload a valid CSV file.');
      return;
    }

    const formData = new FormData();
    formData.append('csv', file);

    try {
      // Send CSV to backend for processing
      const response = await axios.post('http://127.0.0.1:5000/upload-csv', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.status === 200) {
        alert('CSV file processed successfully. Starting MJPEG stream...');
        
        // Fetch frame numbers after successful upload
        await fetchFrameNumbers();
        
        // Start the MJPEG stream
        startMjpegStream();
        
        onCsvUpload(file, exportedFrameNumbers);
        setCsvUploaded(true);
      } else {
        throw new Error('Server returned non-200 status');
      }
    } catch (error) {
      console.error('CSV upload error:', error);
      
      let errorMessage = 'Error uploading CSV file';
      if (error.response) {
        errorMessage = error.response.data?.message || error.response.statusText || errorMessage;
      } else {
        errorMessage = error.message || errorMessage;
      }
      
      alert(errorMessage);
    }
  };

  const handleLogChanges = () => {
    if (!frameNumber.trim() || !A.trim() || !B.trim()) {
      alert("Please enter all values before logging.");
      return;
    }
    
    setLogEntries([...logEntries, { frameNumber, A, B }]);
    setFrameNumber("");
    setA("");
    setB("");
  };

  const handleClearTable = async () => {
    if (logEntries.length === 0) {
      alert("No data to send.");
      return;
    }
    
    try {
      const response = await fetch("http://localhost:5000/save-logs", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ logs: logEntries }),
      });
      
      const data = await response.json();
      
      if (response.ok && data.success) {
        // For MJPEG stream, we just need to refresh the image source
        // The backend will automatically serve the updated frames
        const mjpegImage = document.querySelector('img[data-mjpeg-stream]');
        if (mjpegImage) {
          // Force refresh by adding timestamp to prevent caching
          const baseUrl = `http://127.0.0.1:5000/mjpeg-stream`;
          const timestamp = Date.now();
          mjpegImage.src = `${baseUrl}?t=${timestamp}`;
        }
        alert("Logs successfully saved to backend. Stream will update automatically.");
        setLogEntries([]);
      } else {
        alert(data.message || "Failed to update ID and reprocess video.");
      }
    } catch (error) {
      console.error("Error updating ID:", error);
      alert(error.message || "Error updating ID.");
    }
  };

  const refreshStream = () => {
    const mjpegImage = document.querySelector('img[data-mjpeg-stream]');
    if (mjpegImage) {
      const timestamp = Date.now();
      mjpegImage.src = `http://127.0.0.1:5000/mjpeg-stream?t=${timestamp}`;
    }
  };

  return (
    <div className="upload-section">
      {!csvUploaded ? (
        <>
          <label htmlFor="csv-upload" className="upload-btn">Upload CSV</label>
          <input
            id="csv-upload"
            type="file"
            accept=".csv"
            style={{ display: "none" }}
            onChange={handleCsvUpload}
          />
        </>
      ) : (
        <div className="stream-section">
          {/* MJPEG Stream Container */}
          <div className="stream-container">
            <h3>Live Stream</h3>
            <div id="mjpeg-container" style={{ textAlign: 'center', marginBottom: '20px' }}>
              {streamActive ? null : <p>Loading stream...</p>}
            </div>
            <button onClick={refreshStream} style={{ marginBottom: '20px' }}>
              Refresh Stream
            </button>
          </div>

          {/* Log Section */}
          <div className="log-section">
            <h3>Log Table</h3>
            <div className="input-group" style={{ marginBottom: '10px' }}>
              <input
                type="text"
                placeholder="Frame Number"
                value={frameNumber}
                onChange={(e) => setFrameNumber(e.target.value)}
                style={{ marginRight: '10px', padding: '5px' }}
              />
              <input
                type="text"
                placeholder="A"
                value={A}
                onChange={(e) => setA(e.target.value)}
                style={{ marginRight: '10px', padding: '5px' }}
              />
              <input
                type="text"
                placeholder="B"
                value={B}
                onChange={(e) => setB(e.target.value)}
                style={{ marginRight: '10px', padding: '5px' }}
              />
            </div>
            <div className="button-group" style={{ marginBottom: '20px' }}>
              <button onClick={handleLogChanges} style={{ marginRight: '10px' }}>
                Register Changes
              </button>
              <button onClick={handleClearTable}>
                Make Changes
              </button>
            </div>

            {logEntries.length > 0 && (
              <table className="log-table" style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr>
                    <th style={{ border: '1px solid #ccc', padding: '8px' }}>Frame Number</th>
                    <th style={{ border: '1px solid #ccc', padding: '8px' }}>A</th>
                    <th style={{ border: '1px solid #ccc', padding: '8px' }}>B</th>
                  </tr>
                </thead>
                <tbody>
                  {logEntries.map((entry, index) => (
                    <tr key={index}>
                      <td style={{ border: '1px solid #ccc', padding: '8px' }}>{entry.frameNumber}</td>
                      <td style={{ border: '1px solid #ccc', padding: '8px' }}>{entry.A}</td>
                      <td style={{ border: '1px solid #ccc', padding: '8px' }}>{entry.B}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

// export { exportedFrameNumbers };
export default UploadSection;