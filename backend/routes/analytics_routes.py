from flask import Blueprint, jsonify
import os
from services.assessment_service import run_full_assessment
from services.csv_service import get_uploaded_csv_path

analytics_bp = Blueprint("analytics", __name__)


@analytics_bp.route("/analytics", methods=["GET"])
def analytics():
    csv_path = get_uploaded_csv_path()
    if not csv_path or not os.path.exists(csv_path):
        return jsonify({"error": "CSV file not found"}), 400

    results = run_full_assessment(csv_path)
    return jsonify(results)
