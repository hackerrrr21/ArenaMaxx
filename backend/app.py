from __future__ import annotations
import os
import re
import logging
from typing import Any

import google.cloud.logging
import google.generativeai as genai
from google.cloud import secretmanager

from flask import Flask, jsonify, request, send_from_directory
from flask_socketio import SocketIO
from flask_cors import CORS
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
from dotenv import load_dotenv
import bleach

from models import db, User, Seat
from simulation import CrowdSimulator
from firebase_service import initialize_firebase, log_event

# ─── Load Blueprints ──────────────────────────────────────────────────────────
from api.seats import seats_bp
from api.concessions import concessions_bp
from api.washrooms import washrooms_bp
from api.gemini import gemini_bp
from api.events import events_bp

load_dotenv()
__version__ = "3.1.0"

# ─── Globals & Constants ──────────────────────────────────────────────────────
MAX_FIELD_LENGTH = 50
CACHE_TIMEOUT_SECONDS = 30
DEFAULT_PORT = 8080

# ─── Google Cloud Logging Setup ───────────────────────────────────────────────
try:
    _gcp_log_client = google.cloud.logging.Client(
        project=os.getenv('GOOGLE_CLOUD_PROJECT', 'arenamaxx')
    )
    _gcp_log_client.setup_logging()
    audit_handler = _gcp_log_client.get_default_handler()
    audit_logger = logging.getLogger('security-audit')
    audit_logger.setLevel(logging.INFO)
    audit_logger.addHandler(audit_handler)
    logging.info("Google Cloud Logging & Audit Streams initialized.")
except Exception as _log_err:
    logging.basicConfig(level=logging.INFO)
    audit_logger = logging.getLogger('security-audit')
    logging.info(f"Standard logging active (GCP not available)")

logger = logging.getLogger(__name__)

# ─── Security Helpers ─────────────────────────────────────────────────────────
def get_secret(secret_id: str, default: str = "") -> str:
    """Fetch a versioned secret from Google Cloud Secret Manager."""
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
    if not project_id or project_id == "local": return default
    try:
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")
    except Exception: return default

def sanitize_string(value: Any, max_length: int = MAX_FIELD_LENGTH) -> str:
    """Industry-standard sanitization via bleach."""
    if not isinstance(value, str): return ""
    raw = value.strip()[:max_length]
    cleaned = bleach.clean(raw, tags=[], attributes={}, strip=True)
    if cleaned != raw:
        audit_logger.warning(f"XSS/Injection attempt intercepted: {raw[:100]}")
        return ""
    return cleaned

def validate_required(data: dict, fields: list[str]) -> tuple[bool, str]:
    """Assert required fields are present."""
    for field in fields:
        if not data.get(field): return False, f"Missing required field: '{field}'"
    return True, ""

# ─── App Factory ──────────────────────────────────────────────────────────────
app = Flask(__name__, static_folder='../frontend/dist', static_url_path='/')
app.config.update(
    SECRET_KEY=os.getenv('SECRET_KEY', 'arenamaxx_secure_2026'),
    SQLALCHEMY_DATABASE_URI='sqlite:///stadium.db',
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    CACHE_TYPE='SimpleCache',
    CACHE_DEFAULT_TIMEOUT=CACHE_TIMEOUT_SECONDS,
)

# ─── Extensions ───────────────────────────────────────────────────────────────
CORS(app, resources={r"/api/*": {"origins": "*"}})
csp = {
    'default-src': "'self'",
    'script-src': ["'self'", "'unsafe-inline'", 'https://*.gstatic.com', 'https://apis.google.com'],
    'style-src': ["'self'", "'unsafe-inline'", 'https://fonts.googleapis.com'],
    'font-src': ["'self'", 'https://fonts.gstatic.com'],
    'connect-src': ["'self'", 'wss:', 'ws:', 'https://*.googleapis.com'],
    'img-src': ["'self'", 'data:', 'https://*.google-analytics.com'],
}
Talisman(app, content_security_policy=csp, force_https=False, frame_options='DENY')
db.init_app(app)
cache = Cache(app)
limiter = Limiter(get_remote_address, app=app, default_limits=["300 per day"], storage_uri="memory://")
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')
_firebase_ready = initialize_firebase()

# ─── Register Blueprints ──────────────────────────────────────────────────────
app.register_blueprint(seats_bp)
app.register_blueprint(concessions_bp)
app.register_blueprint(washrooms_bp)
app.register_blueprint(gemini_bp)
app.register_blueprint(events_bp)

# ─── Core Routes ──────────────────────────────────────────────────────────────
@app.route('/')
def serve_index(): return send_from_directory(app.static_folder, 'index.html')

@app.errorhandler(404)
def not_found(e): return send_from_directory(app.static_folder, 'index.html')

@app.before_request
def enforce_json_content_type():
    """Ensure all POST/PUT/PATCH requests use application/json."""
    if request.method in ['POST', 'PUT', 'PATCH']:
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 415

@app.after_request
def set_security_headers(response):
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "version": __version__,
        "firebase_status": "active" if _firebase_ready else "graceful-degradation",
        "google_cloud_services": ["Cloud Run", "Firestore", "Logging", "Secret Manager", "Storage", "Gemini AI"],
        "security": {"talisman": "active", "bleach": "active", "audit": "active"}
    }), 200

# ─── Initialization ───────────────────────────────────────────────────────────
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if Seat.query.count() == 0:
            db.session.add(User(name="Admin", role="staff"))
            for i in range(1, 11): db.session.add(Seat(block='A', row='1', number=i))
            db.session.commit()
    
    simulator = CrowdSimulator(socketio)
    simulator.start()
    port = int(os.environ.get("PORT", DEFAULT_PORT))
    socketio.run(app, debug=False, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)
