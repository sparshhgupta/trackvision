// import React, { useState } from 'react';
// import { BrowserRouter, Routes, Route, useNavigate } from 'react-router-dom';
// import LandingPage from './components/LandingPage';
// import UploadSection from './components/UploadSection';
// import VideoPlayer from './components/VideoPlayer';
// import DownloadCsvButton from './components/DownloadCsvButton';
// import OutputsPage from './components/OutputsPage';
// import './App.css';

// function MainApp() {
//   const [csvFile, setCsvFile] = useState(null);
//   const [end_frames, setEndFrames] = useState([]);
//   const navigate = useNavigate();

//   const handleCsvUploadSuccess = (file, end_frames) => {
//     setCsvFile(file);
//     setEndFrames(end_frames);
//   };

//   return (
//     <div className="app">
//       <div className="sidebar">
//         <UploadSection csvFile={csvFile} onCsvUpload={handleCsvUploadSuccess} />
//       </div>
//       <div className="main">
//         <VideoPlayer csvFile={csvFile} />
//       </div>
//       <div className="actions">
//         {/* Render only if CSV is uploaded */}
//         {csvFile && (
//           <button 
//             onClick={() => navigate('/outputs')} 
//             className="go-to-outputs-btn"
//           >
//             Go to Outputs
//           </button>
//         )}
//       </div>
//     </div>
//   );
// }

// function App() {
//   return (
//     <BrowserRouter>
//       <Routes>
//         <Route path="/" element={<LandingPage />} />
//         <Route path="/app" element={<MainApp />} />
//         <Route path="/outputs" element={<OutputsPage />} />
//       </Routes>
//     </BrowserRouter>
//   );
// }

// export default App;

import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, useNavigate } from 'react-router-dom';
import LandingPage from './components/LandingPage';
import UploadSection from './components/UploadSection';
import VideoPlayer from './components/VideoPlayer';
import OutputsPage from './components/OutputsPage';
import AccessBar from './components/AccessBar';
import './App.css';
import { Sun, Moon } from "lucide-react";


function MainApp() {
  const [csvFile, setCsvFile] = useState(null);
  const [end_frames, setEndFrames] = useState([]);
  const [darkMode, setDarkMode] = useState(false);
  const navigate = useNavigate();

  const handleCsvUploadSuccess = (file, end_frames) => {
    setCsvFile(file);
    setEndFrames(end_frames);
  };

  return (
    <div className={`app ${darkMode ? "dark-mode" : "light-mode"}`}>
      {/* Sidebar */}
      <div className="sidebar">
        <UploadSection csvFile={csvFile} onCsvUpload={handleCsvUploadSuccess} />
        <AccessBar />
        <button 
          onClick={() => setDarkMode(!darkMode)} 
          className="toggle-theme-btn"
        >
          {darkMode ? <Sun size={20} /> : <Moon size={20} />}
        </button>
      </div>

      {/* <div className="access-bar-container">
        <AccessBar />
      </div> */}

      {/* Main Video Player */}
      <div className="main">
        <VideoPlayer csvFile={csvFile} />
      </div>

      {/* Action Button */}
      <div className="actions">
        {csvFile && (
          <button 
            onClick={() => navigate('/outputs')} 
            className="go-to-outputs-btn"
          >
            Go to Outputs
          </button>
        )}
      </div>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/app" element={<MainApp />} />
        <Route path="/outputs" element={<OutputsPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;


// import React, { useState, useEffect } from 'react';
// import { BrowserRouter, Routes, Route, useNavigate } from 'react-router-dom';
// import LandingPage from './components/LandingPage';
// import UploadSection from './components/UploadSection';
// import VideoPlayer from './components/VideoPlayer';
// import OutputsPage from './components/OutputsPage';
// import AccessBar from './components/AccessBar';
// import './App.css';

// function MainApp() {
//   const [csvFile, setCsvFile] = useState(null);
//   const [end_frames, setEndFrames] = useState([]);
//   const [darkMode, setDarkMode] = useState(false);
//   const navigate = useNavigate();

//   const handleCsvUploadSuccess = (file, end_frames) => {
//     setCsvFile(file);
//     setEndFrames(end_frames);
//   };

//   // Apply theme to document root
//   useEffect(() => {
//     if (darkMode) {
//       document.documentElement.setAttribute('data-theme', 'dark');
//     } else {
//       document.documentElement.removeAttribute('data-theme');
//     }
//   }, [darkMode]);

//   return (
//     <div className="app">
//       {/* Access Bar Component */}
//       <AccessBar darkMode={darkMode} setDarkMode={setDarkMode} />

//       {/* Sidebar */}
//       <div className="sidebar">
//         <UploadSection onCsvUploadSuccess={handleCsvUploadSuccess} />
//       </div>

//       {/* Main Video Player */}
//       <div className="main-content">
//         <VideoPlayer csvFile={csvFile} end_frames={end_frames} />
//       </div>

//       {/* Action Button */}
//       <div className="action-section">
//         {csvFile && (
//           <button
//             onClick={() => navigate('/outputs')}
//             className="go-to-outputs-btn"
//           >
//             Go to Outputs
//           </button>
//         )}
//       </div>
//     </div>
//   );
// }

// function App() {
//   return (
//     <BrowserRouter>
//       <Routes>
//         <Route path="/" element={<LandingPage />} />
//         <Route path="/main" element={<MainApp />} />
//         <Route path="/outputs" element={<OutputsPage />} />
//       </Routes>
//     </BrowserRouter>
//   );
// }

// export default App;