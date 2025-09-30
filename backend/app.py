from flask import Flask
from flask_cors import CORS
import os
import logging
import atexit

from routes.upload_routes import upload_bp
from routes.update_routes import update_bp

from routes.frameroutes import frame_bp 
from routes.download_routes import download_bp
from routes.analytics_routes import analytics_bp 
from routes.display_filter_routes import display_filter_bp

from services.stream_service import cleanup_stream_processor

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
CORS(app)

os.makedirs('temp', exist_ok=True)

app.register_blueprint(upload_bp)
app.register_blueprint(update_bp)
app.register_blueprint(frame_bp)
app.register_blueprint(download_bp)
app.register_blueprint(analytics_bp)
app.register_blueprint(display_filter_bp)

def cleanup():
    cleanup_stream_processor()

atexit.register(cleanup)

@app.route('/')
def home():
    return "Video Processing Server with MJPEG Streaming"

@app.route('/health')
def health():
    return {"status": "healthy"}

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000, threaded=True)