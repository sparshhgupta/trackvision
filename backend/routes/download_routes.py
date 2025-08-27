from flask import Blueprint, request, jsonify
import logging
import os
from services.csv_service import download_updated_csv

download_bp = Blueprint('download', __name__)

@download_bp.route('/download_csv', methods=['GET'])
def download_csv():
    return download_updated_csv()
