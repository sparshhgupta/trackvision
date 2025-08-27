import React from "react";
import "./DownloadCsvButton.css";

const DownloadCsvButton = () => {
  const handleDownload = async () => {
    try {
      const response = await fetch("http://127.0.0.1:5000/download_csv", {
        method: "GET",
      });

      if (!response.ok) {
        throw new Error("Failed to download CSV");
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);

      const a = document.createElement("a");
      a.href = url;
      a.download = "updated_annotations.csv";
      document.body.appendChild(a);
      a.click();

      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Error downloading CSV:", error);
      alert("Failed to download CSV");
    }
  };

  return (
    <button onClick={handleDownload} className="download-csv-btn">
      Download Updated CSV
    </button>
  );
};

export default DownloadCsvButton;
