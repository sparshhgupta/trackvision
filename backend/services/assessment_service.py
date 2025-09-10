from assesment import load_tracking_results_from_csv, StoredResultsAssessment, get_overall_edge_frames
import logging

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
        problematic_tracks = assessment.get_problematic_tracks()
        start_frame, end_frame = get_overall_edge_frames(csv_path)

        return {
            "tracks_summary": tracks_summary,
            "metrics": metrics,
            "problematic_tracks": problematic_tracks,
            "start_frame": start_frame,
            "end_frame": end_frame
        }

    except Exception as e:
        logging.error(f"Error running assessment: {e}")
        return {"error": str(e)}


def get_track_end_frames_with_ids(csv_path):
    results = load_tracking_results_from_csv(csv_path)
    if not results:
        return []
    assessment = StoredResultsAssessment()
    assessment.process_stored_results(results)
    tracks_summary = assessment.get_tracks_summary()
    return [(max(summary['end_frame'] - 20, 0), track_id) for track_id, summary in tracks_summary.items()]
