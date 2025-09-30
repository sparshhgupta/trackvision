from assesment import load_tracking_results_from_csv, StoredResultsAssessment, get_overall_edge_frames
import logging
import numpy as np
import pandas as pd

def convert_to_serializable(obj):
    """Convert numpy/pandas types to JSON serializable Python types."""
    if isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, pd.Series):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_to_serializable(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_serializable(item) for item in obj]
    else:
        return obj

def run_full_assessment(csv_path: str):
    """Run assessment on tracking CSV and return analytics results."""
    try:
        results = load_tracking_results_from_csv(csv_path)
        if not results:
            return {"error": "No results found in CSV"}

        assessment = StoredResultsAssessment()
        assessment.process_stored_results(results)

        # Collect analytics
        tracks_summary = assessment.get_tracks_summary()
        metrics = assessment.compute_metrics()
        start_frame, end_frame = get_overall_edge_frames(csv_path)

        # Convert all data to JSON serializable format
        serializable_data = {
            "tracks_summary": convert_to_serializable(tracks_summary),
            "metrics": convert_to_serializable(metrics),
            "start_frame": convert_to_serializable(start_frame),
            "end_frame": convert_to_serializable(end_frame)
        }

        return serializable_data

    except Exception as e:
        logging.error(f"Error running assessment: {e}")
        return {"error": str(e)}

def getTrackSummaries(csv_path):
    results = load_tracking_results_from_csv(csv_path)
    if not results:
        return {}
    assessment = StoredResultsAssessment()
    assessment.process_stored_results(results)
    tracks_summary = assessment.get_tracks_summary()
    return convert_to_serializable(tracks_summary)

def getTrackMetrics(csv_path):
    results = load_tracking_results_from_csv(csv_path)
    if not results:
        return {}
    assessment = StoredResultsAssessment()
    assessment.process_stored_results(results)
    metrics = assessment.compute_metrics()
    return convert_to_serializable(metrics)

def get_track_end_frames_with_ids(csv_path):
    results = load_tracking_results_from_csv(csv_path)
    if not results:
        return []
    assessment = StoredResultsAssessment()
    assessment.process_stored_results(results)
    tracks_summary = assessment.get_tracks_summary()
    
    # Convert to serializable format
    track_frames = [(max(summary['end_frame'] - 20, 0), track_id) 
                   for track_id, summary in tracks_summary.items()]
    return convert_to_serializable(track_frames)