// import React, { useState } from 'react';
// import { Menu, X, Sun, Moon, Trash2, Info, RefreshCw } from 'lucide-react';
// import './AccessBar.css';

// const AccessBar = () => {
//   const [isOpen, setIsOpen] = useState(false);
//   const [displayMode, setDisplayMode] = useState('all'); // 'all' or 'specific'
//   const [specificIds, setSpecificIds] = useState([]);
//   const [newId, setNewId] = useState('');
//   const [filterInfo, setFilterInfo] = useState(null);

//   const toggleAccessBar = () => {
//     setIsOpen(!isOpen);
//   };

//   const closeAccessBar = () => {
//     setIsOpen(false);
//   };

//   const handleDisplayModeChange = (mode) => {
//     setDisplayMode(mode);
    
//     // Only trigger endpoint for 'all' mode immediately
//     if (mode === 'all') {
//       triggerEndpoint('/render-all-ids');
//     }
//     // For 'specific' mode, we'll wait for user to click "Apply Filter" button
//   };

//   const addSpecificId = () => {
//     if (newId.trim() && !specificIds.includes(newId.trim())) {
//       const updatedIds = [...specificIds, newId.trim()];
//       setSpecificIds(updatedIds);
//       setNewId('');
//       // Don't trigger endpoint automatically - wait for "Apply Filter" button
//     }
//   };

//   const removeSpecificId = (idToRemove) => {
//     // Remove the ID from the list
//     const updatedIds = specificIds.filter(id => id !== idToRemove);
//     setSpecificIds(updatedIds);
//     // Don't trigger endpoint automatically - wait for "Apply Filter" button
//   };

//   // New function to apply the specific IDs filter
//   const applySpecificIdsFilter = () => {
//     if (displayMode === 'specific') {
//       triggerEndpoint('/render-specific-ids', specificIds);
//     }
//   };

//   const handleKeyPress = (e) => {
//     if (e.key === 'Enter') {
//       addSpecificId();
//     }
//   };

//   const triggerEndpoint = async (endpoint, ids = null) => {
//     try {
//       const requestBody = endpoint === '/render-specific-ids' ? { ids } : {};
      
//       // Add base URL if needed
//       const baseUrl = 'http://127.0.0.1:5000'; // Adjust if your Flask server runs on different host/port
//       const fullUrl = `${baseUrl}${endpoint}`;
      
//       console.log(`Calling endpoint: ${fullUrl}`, requestBody);
      
//       const response = await fetch(fullUrl, {
//         method: 'POST',
//         headers: {
//           'Content-Type': 'application/json',
//         },
//         body: JSON.stringify(requestBody),
//       });
      
//       if (!response.ok) {
//         const errorText = await response.text();
//         console.error(`Failed to call ${endpoint}:`, response.status, errorText);
//       } else {
//         const responseData = await response.json();
//         console.log(`Successfully called ${endpoint}:`, responseData);
//       }
//     } catch (error) {
//       console.error(`Error calling ${endpoint}:`, error);
//     }
//   };

//   // New function to get display filter info
//   const getDisplayFilterInfo = async () => {
//     try {
//       const baseUrl = 'http://127.0.0.1:5000';
//       const response = await fetch(`${baseUrl}/get-display-filter-info`, {
//         method: 'GET',
//         headers: {
//           'Content-Type': 'application/json',
//         },
//       });
      
//       if (response.ok) {
//         const data = await response.json();
//         setFilterInfo(data.filter_info);
//         console.log('Filter info:', data.filter_info);
//       } else {
//         const errorText = await response.text();
//         console.error('Failed to get display filter info:', response.status, errorText);
//       }
//     } catch (error) {
//       console.error('Error getting display filter info:', error);
//     }
//   };

//   // New function to clear specific IDs
//   const clearSpecificIds = async () => {
//     try {
//       const baseUrl = 'http://127.0.0.1:5000';
//       const response = await fetch(`${baseUrl}/clear-specific-ids`, {
//         method: 'POST',
//         headers: {
//           'Content-Type': 'application/json',
//         },
//       });
      
//       if (response.ok) {
//         const responseData = await response.json();
//         setSpecificIds([]);
//         setDisplayMode('all');
//         console.log('Successfully cleared specific IDs:', responseData);
//       } else {
//         const errorText = await response.text();
//         console.error('Failed to clear specific IDs:', response.status, errorText);
//       }
//     } catch (error) {
//       console.error('Error clearing specific IDs:', error);
//     }
//   };

//   return (
//     <>
//       {/* Hamburger Menu Button */}
//       <button 
//         onClick={toggleAccessBar}
//         className="hamburger-btn"
//         aria-label="Open access menu"
//       >
//         <Menu size={24} />
//       </button>

//       {/* Overlay */}
//       {isOpen && <div className="access-overlay" onClick={closeAccessBar}></div>}

//       {/* Access Bar Panel */}
//       <div className={`access-bar ${isOpen ? 'open' : ''}`}>
//         {/* Header with close button */}
//         <div className="access-header">
//           <h2>Menu</h2>
//           <button 
//             onClick={closeAccessBar}
//             className="close-btn"
//             aria-label="Close access menu"
//           >
//             <X size={24} />
//           </button>
//         </div>

//         {/* Navigation Content */}
//         <div className="access-content">

//           {/* Display Section */}
//           <div className="nav-section">
//             <h3>Display</h3>
//             <div className="nav-items">
//               {/* Radio buttons for display mode */}
//               <div className="radio-group">
//                 <label className="radio-option">
//                   <input
//                     type="radio"
//                     name="displayMode"
//                     value="all"
//                     checked={displayMode === 'all'}
//                     onChange={() => handleDisplayModeChange('all')}
//                   />
//                   <span>All IDs</span>
//                 </label>
                
//                 <label className="radio-option">
//                   <input
//                     type="radio"
//                     name="displayMode"
//                     value="specific"
//                     checked={displayMode === 'specific'}
//                     onChange={() => handleDisplayModeChange('specific')}
//                   />
//                   <span>Specific IDs</span>
//                 </label>
//               </div>

//               {/* Specific IDs input section */}
//               {displayMode === 'specific' && (
//                 <div className="specific-ids-section">
//                   <div className="id-input-container">
//                     <input
//                       type="text"
//                       value={newId}
//                       onChange={(e) => setNewId(e.target.value)}
//                       onKeyPress={handleKeyPress}
//                       placeholder="Enter ID"
//                       className="id-input"
//                     />
//                     <button
//                       onClick={addSpecificId}
//                       className="add-id-btn"
//                       disabled={!newId.trim() || specificIds.includes(newId.trim())}
//                     >
//                       Add
//                     </button>
//                   </div>

//                   {/* Display list of specific IDs */}
//                   {specificIds.length > 0 && (
//                     <div className="ids-list">
//                       {specificIds.map((id, index) => (
//                         <div key={index} className="id-item">
//                           <span className="id-text">{id}</span>
//                           <button
//                             onClick={() => removeSpecificId(id)}
//                             className="remove-id-btn"
//                             aria-label={`Remove ID ${id}`}
//                           >
//                             <Trash2 size={16} />
//                           </button>
//                         </div>
//                       ))}
                      
//                       {/* Apply Filter Button */}
//                       <div className="apply-filter-container">
//                         <button 
//                           onClick={applySpecificIdsFilter}
//                           className="apply-filter-btn"
//                         >
//                           Apply Filter ({specificIds.length} IDs)
//                         </button>
//                       </div>
//                     </div>
//                   )}
//                 </div>
//               )}
//             </div>
//           </div>
//         </div>
//       </div>
//     </>
//   );
// };

// export default AccessBar;

import React, { useState } from 'react';
import { Menu, X, Sun, Moon, Trash2, Info, RefreshCw } from 'lucide-react';
import './AccessBar.css';

const AccessBar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [displayMode, setDisplayMode] = useState('all'); // 'all' or 'specific'
  const [includeIds, setIncludeIds] = useState([]);
  const [excludeIds, setExcludeIds] = useState([]);
  const [newId, setNewId] = useState('');
  const [filterInfo, setFilterInfo] = useState(null);

  const toggleAccessBar = () => {
    setIsOpen(!isOpen);
  };

  const closeAccessBar = () => {
    setIsOpen(false);
  };

  const handleDisplayModeChange = (mode) => {
    setDisplayMode(mode);
    
    // Only trigger endpoint for 'all' mode immediately
    if (mode === 'all') {
      triggerEndpoint('/render-all-ids');
    }
    // For 'specific' mode, we'll wait for user to click "Apply Filter" button
  };

  const addToIncludeIds = () => {
    if (newId.trim() && !includeIds.includes(newId.trim()) && !excludeIds.includes(newId.trim())) {
      const updatedIds = [...includeIds, newId.trim()];
      setIncludeIds(updatedIds);
      setNewId('');
    }
  };

  const addToExcludeIds = () => {
    if (newId.trim() && !excludeIds.includes(newId.trim()) && !includeIds.includes(newId.trim())) {
      const updatedIds = [...excludeIds, newId.trim()];
      setExcludeIds(updatedIds);
      setNewId('');
    }
  };

  const removeFromIncludeIds = (idToRemove) => {
    const updatedIds = includeIds.filter(id => id !== idToRemove);
    setIncludeIds(updatedIds);
  };

  const removeFromExcludeIds = (idToRemove) => {
    const updatedIds = excludeIds.filter(id => id !== idToRemove);
    setExcludeIds(updatedIds);
  };

  // Check if ID already exists in either list
  const isIdDuplicate = () => {
    return newId.trim() && (includeIds.includes(newId.trim()) || excludeIds.includes(newId.trim()));
  };

  // Function to apply the specific IDs filter
  const applySpecificIdsFilter = () => {
    if (displayMode === 'specific') {
      // Handle different scenarios
      if (includeIds.length > 0 && excludeIds.length === 0) {
        // Only include mode
        console.log('Including only IDs:', includeIds);
        triggerEndpoint('/render-specific-ids', includeIds, 'include');
      } else if (excludeIds.length > 0 && includeIds.length === 0) {
        // Only exclude mode
        console.log('Excluding IDs:', excludeIds);
        triggerEndpoint('/render-specific-ids', excludeIds, 'exclude');
      } else if (includeIds.length > 0 && excludeIds.length > 0) {
        // Both include and exclude - prioritize include
        console.warn('Both include and exclude IDs specified - prioritizing include mode');
        triggerEndpoint('/render-specific-ids', includeIds, 'include');
      } else {
        console.warn('No IDs specified for filtering');
      }
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      // Default to Include when Enter is pressed, if ID is valid and not duplicate
      if (!isIdDuplicate() && newId.trim()) {
        addToIncludeIds();
      }
    }
  };

  const triggerEndpoint = async (endpoint, ids = null, mode = null) => {
    try {
      let requestBody = {};
      
      if (endpoint === '/render-specific-ids') {
        requestBody = { ids };
        if (mode) {
          requestBody.mode = mode;
        }
      }
      
      // Add base URL if needed
      const baseUrl = 'http://127.0.0.1:5000'; // Adjust if your Flask server runs on different host/port
      const fullUrl = `${baseUrl}${endpoint}`;
      
      console.log(`Calling endpoint: ${fullUrl}`, requestBody);
      
      const response = await fetch(fullUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error(`Failed to call ${endpoint}:`, response.status, errorText);
      } else {
        const responseData = await response.json();
        console.log(`Successfully called ${endpoint}:`, responseData);
      }
    } catch (error) {
      console.error(`Error calling ${endpoint}:`, error);
    }
  };

  // Function to get display filter info
  const getDisplayFilterInfo = async () => {
    try {
      const baseUrl = 'http://127.0.0.1:5000';
      const response = await fetch(`${baseUrl}/get-display-filter-info`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setFilterInfo(data.filter_info);
        console.log('Filter info:', data.filter_info);
      } else {
        const errorText = await response.text();
        console.error('Failed to get display filter info:', response.status, errorText);
      }
    } catch (error) {
      console.error('Error getting display filter info:', error);
    }
  };

  // Function to clear all specific IDs
  const clearAllSpecificIds = async () => {
    try {
      const baseUrl = 'http://127.0.0.1:5000';
      const response = await fetch(`${baseUrl}/clear-specific-ids`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        const responseData = await response.json();
        // Clear frontend state immediately after successful backend call
        setIncludeIds([]);
        setExcludeIds([]);
        setDisplayMode('all');
        console.log('Successfully cleared specific IDs:', responseData);
        
        // The backend already handles switching to 'all' mode, so no need to call render-all-ids again
      } else {
        const errorText = await response.text();
        console.error('Failed to clear specific IDs:', response.status, errorText);
      }
    } catch (error) {
      console.error('Error clearing specific IDs:', error);
    }
  };

  const totalIds = includeIds.length + excludeIds.length;

  return (
    <>
      {/* Hamburger Menu Button */}
      <button 
        onClick={toggleAccessBar}
        className="hamburger-btn"
        aria-label="Open access menu"
      >
        <Menu size={24} />
      </button>

      {/* Overlay */}
      {isOpen && <div className="access-overlay" onClick={closeAccessBar}></div>}

      {/* Access Bar Panel */}
      <div className={`access-bar ${isOpen ? 'open' : ''}`}>
        {/* Header with close button */}
        <div className="access-header">
          <h2>Menu</h2>
          <button 
            onClick={closeAccessBar}
            className="close-btn"
            aria-label="Close access menu"
          >
            <X size={24} />
          </button>
        </div>

        {/* Navigation Content */}
        <div className="access-content">

          {/* Display Section */}
          <div className="nav-section">
            <h3>Display</h3>
            <div className="nav-items">
              {/* Radio buttons for display mode */}
              <div className="radio-group">
                <label className="radio-option">
                  <input
                    type="radio"
                    name="displayMode"
                    value="all"
                    checked={displayMode === 'all'}
                    onChange={() => handleDisplayModeChange('all')}
                  />
                  <span>All IDs</span>
                </label>
                
                <label className="radio-option">
                  <input
                    type="radio"
                    name="displayMode"
                    value="specific"
                    checked={displayMode === 'specific'}
                    onChange={() => handleDisplayModeChange('specific')}
                  />
                  <span>Specific IDs</span>
                </label>
              </div>

              {/* Specific IDs input section */}
              {displayMode === 'specific' && (
                <div className="specific-ids-section">
                  <div className="id-input-container">
                    <input
                      type="text"
                      value={newId}
                      onChange={(e) => setNewId(e.target.value)}
                      onKeyPress={handleKeyPress}
                      placeholder="Enter ID"
                      className="id-input"
                    />
                    <div className="action-buttons">
                      <button
                        onClick={addToIncludeIds}
                        className="include-id-btn"
                        disabled={!newId.trim() || isIdDuplicate()}
                      >
                        Include
                      </button>
                      <button
                        onClick={addToExcludeIds}
                        className="exclude-id-btn"
                        disabled={!newId.trim() || isIdDuplicate()}
                      >
                        Exclude
                      </button>
                    </div>
                  </div>

                  {/* Display duplicate warning */}
                  {isIdDuplicate() && (
                    <div className="duplicate-warning">
                      ID already exists in one of the lists
                    </div>
                  )}

                  {/* Display list of include IDs */}
                  {includeIds.length > 0 && (
                    <div className="ids-list">
                      <h4 className="list-title include-title">Include IDs (Show Only These)</h4>
                      {includeIds.map((id, index) => (
                        <div key={index} className="id-item include-id">
                          <span className="id-text">{id}</span>
                          <button
                            onClick={() => removeFromIncludeIds(id)}
                            className="delete-id-btn"
                            aria-label={`Delete ID ${id}`}
                          >
                            <Trash2 size={16} />
                          </button>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Display list of exclude IDs */}
                  {excludeIds.length > 0 && (
                    <div className="ids-list">
                      <h4 className="list-title exclude-title">Exclude IDs (Hide These)</h4>
                      {excludeIds.map((id, index) => (
                        <div key={index} className="id-item exclude-id">
                          <span className="id-text">{id}</span>
                          <button
                            onClick={() => removeFromExcludeIds(id)}
                            className="delete-id-btn"
                            aria-label={`Delete ID ${id}`}
                          >
                            <Trash2 size={16} />
                          </button>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Action buttons */}
                  {totalIds > 0 && (
                    <div className="filter-actions">
                      <button 
                        onClick={applySpecificIdsFilter}
                        className="apply-filter-btn"
                      >
                        Apply Filter ({totalIds} IDs)
                      </button>
                      
                      <button 
                        onClick={clearAllSpecificIds}
                        className="clear-all-btn"
                      >
                        <RefreshCw size={16} />
                        Clear All
                      </button>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default AccessBar;