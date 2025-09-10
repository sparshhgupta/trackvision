import React from "react";
import { useNavigate } from "react-router-dom";
import DownloadCsvButton from "../components/DownloadCsvButton"; 
import "./OutputsPage.css";

const OutputsPage = () => {
  const navigate = useNavigate();

  return (
    <div className="outputs-page">
      <h1 className="outputs-title">Outputs</h1>
      <p className="outputs-description">
        Here you can download your processed outputs. The CSV file contains the
        updated annotations.
      </p>

      <div className="outputs-actions">
        <DownloadCsvButton />
      </div>

      {/* <div className="analytics-section">
        <button 
          className="go-to-analytics-btn"
          onClick={() => navigate("/analytics")}
        >
          Go to Analytics
        </button>
      </div> */}
    </div>
  );
};

export default OutputsPage;
