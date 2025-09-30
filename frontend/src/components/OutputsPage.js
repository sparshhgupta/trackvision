import React, { useState } from "react";
import { ChevronDown, ChevronRight, Activity, Target, BarChart3, Info, Search, X, Download } from "lucide-react";
import "./OutputsPage.css";
import DownloadCsvButton from "./DownloadCsvButton";
// Mock data structure based on your backend
const mockAnalyticsData = {
  start_frame: 1,
  end_frame: 150,
  metrics: {
    total_tracks: 12,
    total_frames: 150,
    avg_detections_per_frame: 3.2,
    avg_track_duration: 45.3,
    max_track_duration: 89,
    min_track_duration: 12,
    avg_track_fragmentation: 1.2,
    avg_velocity_consistency: 0.85,
    avg_size_consistency: 0.92,
    avg_confidence_stability: 0.78,
    track_stability_score: 0.85
  },
  tracks_summary: {
    1: { start_frame: 1, end_frame: 89, total_detections: 85, gaps: 2, avg_confidence: 0.92 },
    2: { start_frame: 15, end_frame: 145, total_detections: 120, gaps: 1, avg_confidence: 0.87 },
    3: { start_frame: 25, end_frame: 67, total_detections: 40, gaps: 0, avg_confidence: 0.95 },
    4: { start_frame: 45, end_frame: 150, total_detections: 98, gaps: 3, avg_confidence: 0.83 },
    5: { start_frame: 12, end_frame: 34, total_detections: 22, gaps: 1, avg_confidence: 0.89 }
  }
};

const AnalyticsSection = ({ title, icon: Icon, children, defaultOpen = false }) => {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  return (
    <div className="analytics-section-container">
      <button 
        className={`analytics-section-header ${isOpen ? 'open' : ''}`}
        onClick={() => setIsOpen(!isOpen)}
      >
        <div className="section-title-container">
          <Icon size={20} className="section-icon" />
          <h3 className="section-title">{title}</h3>
        </div>
        {isOpen ? <ChevronDown size={20} /> : <ChevronRight size={20} />}
      </button>
      
      <div className={`analytics-section-content ${isOpen ? 'open' : ''}`}>
        <div className="section-content-inner">
          {children}
        </div>
      </div>
    </div>
  );
};

const MetricItem = ({ label, value, type = "default" }) => {
  const formatValue = (val) => {
    if (typeof val === 'number') {
      if (label.toLowerCase().includes('score') || label.toLowerCase().includes('consistency') || label.toLowerCase().includes('stability')) {
        return (val * 100).toFixed(1) + '%';
      }
      return val % 1 === 0 ? val.toString() : val.toFixed(2);
    }
    return val;
  };

  const getMetricClass = () => {
    if (type === 'highlight') return 'metric-highlight';
    if (type === 'warning' && typeof value === 'number' && value < 0.5) return 'metric-warning';
    return 'metric-default';
  };

  return (
    <div className={`metric-item ${getMetricClass()}`}>
      <span className="metric-label">{label.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</span>
      <span className="metric-value">{formatValue(value)}</span>
    </div>
  );
};

const TrackCard = ({ trackId, summary, trackStatus }) => {
  const duration = summary.end_frame - summary.start_frame + 1;

  return (
    <div className={`track-card track-${trackStatus}`}>
      <div className="track-header">
        <span className="track-id">Track {trackId}</span>
        <span className={`track-status ${trackStatus}`}>
          {trackStatus.toUpperCase()}
        </span>
      </div>
      <div className="track-details">
        <div className="track-detail-row">
          <span className="detail-label">Duration:</span>
          <span className="detail-value">{duration} frames ({summary.start_frame}-{summary.end_frame})</span>
        </div>
        <div className="track-detail-row">
          <span className="detail-label">Detections:</span>
          <span className="detail-value">{summary.total_detections}</span>
        </div>
        <div className="track-detail-row">
          <span className="detail-label">Gaps:</span>
          <span className="detail-value">{summary.gaps}</span>
        </div>
        <div className="track-detail-row">
          <span className="detail-label">Avg Confidence:</span>
          <span className="detail-value">{(summary.avg_confidence * 100).toFixed(1)}%</span>
        </div>
      </div>
    </div>
  );
};

const AnalyticsDashboard = () => {
  const [analyticsData, setAnalyticsData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showAnalytics, setShowAnalytics] = useState(true);
  const [trackIdSearch, setTrackIdSearch] = useState("");
  const [frameSearch, setFrameSearch] = useState("");
  const [trackStatusFilter, setTrackStatusFilter] = useState("all");

  const loadAnalytics = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Replace with your actual API call
      const response = await fetch('http://127.0.0.1:5000/analytics');
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to fetch analytics');
      }

      setAnalyticsData(data);
      setShowAnalytics(true);
    } catch (err) {
      console.error('Error loading analytics:', err);
      setError(err.message);
      // For demo purposes, we'll still show mock data
      setShowAnalytics(true);
    } finally {
      setLoading(false);
    }
  };

  const getTrackStatus = (summary) => {
    if (summary.avg_confidence > 0.9) return 'excellent';
    if (summary.avg_confidence > 0.7) return 'good';
    if (summary.avg_confidence > 0.5) return 'fair';
    return 'poor';
  };

  const filteredTracks = () => {
    let tracks = Object.entries(analyticsData.tracks_summary);
    
    // Filter by track ID search
    if (trackIdSearch) {
      tracks = tracks.filter(([trackId]) => {
        return trackId.toString().toLowerCase().includes(trackIdSearch.toLowerCase());
      });
    }
    
    // Filter by frame search (check if frame is within track's range)
    if (frameSearch) {
      const searchFrame = parseInt(frameSearch);
      if (!isNaN(searchFrame)) {
        tracks = tracks.filter(([trackId, summary]) => {
          return searchFrame >= summary.start_frame && searchFrame <= summary.end_frame;
        });
      }
    }
    
    // Filter by status
    if (trackStatusFilter !== "all") {
      tracks = tracks.filter(([trackId, summary]) => {
        return getTrackStatus(summary) === trackStatusFilter;
      });
    }
    
    return tracks;
  };

  const getTrackStats = () => {
    const tracks = Object.entries(analyticsData.tracks_summary);
    const stats = {
      all: tracks.length,
      excellent: 0,
      good: 0,
      fair: 0,
      poor: 0
    };
    
    tracks.forEach(([trackId, summary]) => {
      const status = getTrackStatus(summary);
      stats[status]++;
    });
    
    return stats;
  };

  const clearSearch = () => {
    setTrackIdSearch("");
    setFrameSearch("");
    setTrackStatusFilter("all");
  };

  const hasActiveFilters = () => {
    return trackIdSearch || frameSearch || trackStatusFilter !== "all";
  };

  const getKeyMetrics = () => {
    const { metrics } = analyticsData;
    return {
      'Total Tracks': metrics.total_tracks,
      'Total Frames': metrics.total_frames,
      'Avg Detections/Frame': metrics.avg_detections_per_frame,
      // 'Track Stability Score': metrics.track_stability_score
    };
  };

  const getPerformanceMetrics = () => {
    const { metrics } = analyticsData;
    return {
      'Avg Track Duration': metrics.avg_track_duration,
      'Max Track Duration': metrics.max_track_duration,
      'Min Track Duration': metrics.min_track_duration,
      'Avg Track Fragmentation': metrics.avg_track_fragmentation,
      // 'Avg Velocity Consistency': metrics.avg_velocity_consistency,
      'Avg Size Consistency': metrics.avg_size_consistency,
      'Avg Confidence Stability': metrics.avg_confidence_stability
    };
  };

  return (
    <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto' }}>
      <h1>Analytics Dashboard</h1>
      
      <div className="outputs-actions">
        <button 
          className="analytics-btn" 
          onClick={loadAnalytics}
          disabled={loading}
        >
          {loading ? 'Loading...' : '📊 View Analytics'}
        </button>
        <DownloadCsvButton />

      </div>

      {error && (
        <div className="analytics-error">
          <h3>❌ Error Loading Analytics</h3>
          <p>{error}</p>
          <p>Please check if your CSV file is uploaded and try again.</p>
        </div>
      )}

      {loading && (
        <div className="analytics-loading">
          <div className="spinner"></div>
          <p>Loading analytics data...</p>
        </div>
      )}

      {showAnalytics && analyticsData && !loading && (
        <div className="analytics-dashboard">
          <div className="analytics-header">
            <h2>📊 Analytics Dashboard</h2>
            <button 
              className="close-analytics-btn"
              onClick={() => setShowAnalytics(false)}
            >
              ✕
            </button>
          </div>

          {/* Frame Range Info */}
          <div className="frame-info">
            <div className="frame-range">
              Frame {analyticsData.start_frame} - {analyticsData.end_frame}
            </div>
            <div className="frame-label">
              Analysis Range • Total: {analyticsData.end_frame - analyticsData.start_frame + 1} frames
            </div>
          </div>

          {/* Key Metrics Section */}
          <AnalyticsSection title="Key Metrics" icon={Info} defaultOpen={true}>
            <div className="metrics-grid">
              {Object.entries(getKeyMetrics()).map(([key, value]) => (
                <MetricItem key={key} label={key} value={value} type="highlight" />
              ))}
            </div>
          </AnalyticsSection>

          {/* Performance Metrics Section */}
          <AnalyticsSection title="Performance Metrics" icon={BarChart3}>
            <div className="metrics-grid">
              {Object.entries(getPerformanceMetrics()).map(([key, value]) => (
                <MetricItem key={key} label={key} value={value} type="default" />
              ))}
            </div>
          </AnalyticsSection>

          {/* Tracks Summary Section */}
          <AnalyticsSection title="Individual Tracks" icon={Target}>
            <div className="tracks-search-container">
              {/* Search Inputs Row */}
              <div className="search-inputs-row">
                {/* Track ID Search */}
                <div className="search-input-container">
                  <label className="search-input-label">Search by Track ID</label>
                  <Search className="search-icon" size={16} />
                  <input
                    type="text"
                    className="search-input"
                    placeholder="Enter track ID (e.g., 1, 2, 3...)"
                    value={trackIdSearch}
                    onChange={(e) => setTrackIdSearch(e.target.value)}
                  />
                  {trackIdSearch && (
                    <button className="clear-search" onClick={() => setTrackIdSearch("")}>
                      <X size={14} />
                    </button>
                  )}
                </div>

                {/* Frame Search */}
                <div className="search-input-container">
                  <label className="search-input-label">Search by Frame Number</label>
                  <Search className="search-icon" size={16} />
                  <input
                    type="number"
                    className="search-input"
                    placeholder="Enter frame number (e.g., 105)"
                    value={frameSearch}
                    onChange={(e) => setFrameSearch(e.target.value)}
                    min="1"
                  />
                  {frameSearch && (
                    <button className="clear-search" onClick={() => setFrameSearch("")}>
                      <X size={14} />
                    </button>
                  )}
                </div>

                {/* Clear All Button */}
                {hasActiveFilters() && (
                  <button className="clear-all-searches" onClick={clearSearch}>
                    Clear All
                  </button>
                )}
              </div>

              {/* Status Filters */}
              <div className="filter-container">
                <span className="filter-label">Filter by Quality:</span>
                <div className="status-filters">
                  {Object.entries(getTrackStats()).map(([status, count]) => (
                    <button
                      key={status}
                      className={`status-filter-btn ${status} ${trackStatusFilter === status ? 'active' : ''}`}
                      onClick={() => setTrackStatusFilter(status)}
                    >
                      {status} ({count})
                    </button>
                  ))}
                </div>
              </div>

              {/* Search Results Info */}
              {hasActiveFilters() && (
                <div className="search-results-info">
                  <span className="results-count">
                    Showing {filteredTracks().length} of {Object.keys(analyticsData.tracks_summary).length} tracks
                    {trackIdSearch && ` • Track ID: "${trackIdSearch}"`}
                    {frameSearch && ` • Frame: ${frameSearch}`}
                    {trackStatusFilter !== "all" && ` • Quality: ${trackStatusFilter}`}
                  </span>
                  <button className="clear-all-btn" onClick={clearSearch}>
                    Clear Filters
                  </button>
                </div>
              )}
            </div>

            {filteredTracks().length > 0 ? (
              <div className="tracks-grid">
                {filteredTracks().map(([trackId, summary]) => (
                  <TrackCard 
                    key={trackId} 
                    trackId={trackId} 
                    summary={summary} 
                    trackStatus={getTrackStatus(summary)}
                  />
                ))}
              </div>
            ) : (
              <div className="no-results">
                <h3>No tracks found</h3>
                <p>
                  {trackIdSearch && `No tracks found with ID containing "${trackIdSearch}"`}
                  {frameSearch && !trackIdSearch && `No tracks found containing frame ${frameSearch}`}
                  {trackIdSearch && frameSearch && ` or containing frame ${frameSearch}`}
                  {!trackIdSearch && !frameSearch && trackStatusFilter !== "all" && `No ${trackStatusFilter} quality tracks found`}
                  {!trackIdSearch && !frameSearch && trackStatusFilter === "all" && "Try adjusting your search criteria"}
                </p>
              </div>
            )}
          </AnalyticsSection>
        </div>
      )}
    </div>
  );
};

export default AnalyticsDashboard;