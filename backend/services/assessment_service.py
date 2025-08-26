from assesment import load_tracking_results_from_csv, StoredResultsAssessment

def get_track_end_frames_with_ids(csv_path):
    results = load_tracking_results_from_csv(csv_path)
    if not results:
        return []
    assessment = StoredResultsAssessment()
    assessment.process_stored_results(results)
    tracks_summary = assessment.get_tracks_summary()
    return [(max(summary['end_frame'] - 20, 0), track_id) for track_id, summary in tracks_summary.items()]
