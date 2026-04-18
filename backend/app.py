"""
ArenaMaxx Stadium Management Platform — Backend API
Version: 3.0.0

Google Cloud Services Used:
  - Google Cloud Run        (hosting & auto-scaling)
  - Google Cloud Logging    (structured log ingestion)
  - Google Cloud Firestore  (real-time event storage via Firebase Admin SDK)
  - Google Gemini AI        (gemini-1.5-flash, AI concierge)
  - Firebase Admin SDK      (auth-ready, Firestore client)

Architecture: Flask + Flask-SocketIO (Eventlet) + SQLAlchemy (SQLite) + Firebase
"""

from __future__ import annotations

__version__ = "3.0.0"
__author__ = "ArenaMaxx Team"

import os
import re
import logging
from typing import Any

import google.cloud.logging
import google.generativeai as genai

from flask import Flask, jsonify, request, send_from_directory
from flask_socketio import SocketIO
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
from dotenv import load_dotenv

from models import db, User, Seat, Order, WashroomSlot
from simulation import CrowdSimulator
from firebase_service import initialize_firebase, log_event, log_ai_chat, get_recent_events

load_dotenv()

# ─── Constants ────────────────────────────────────────────────────────────────
MAX_MESSAGE_LENGTH: int = 1000
MAX_ITEMS_LENGTH: int = 500
MAX_FIELD_LENGTH: int = 50
DEFAULT_PORT: int = 8080
CACHE_TIMEOUT_SECONDS: int = 30
VALID_WASHROOM_BLOCKS: list[str] = [
    'Block_A', 'Block_B', 'Block_C',
    'Block_A_m', 'Block_B_m', 'Block_C_m',
    'Block_A_w', 'Block_B_w', 'Block_C_w'
]
INJECTION_PATTERN = re.compile(
    r'(<script|javascript:|on\w+=|union\s+select|drop\s+table|insert\s+into)',
    re.IGNORECASE
)

# ─── Google Cloud Logging Setup ───────────────────────────────────────────────
try:
    _gcp_log_client = google.cloud.logging.Client(
        project=os.getenv('GOOGLE_CLOUD_PROJECT', 'arenamaxx')
    )
    _gcp_log_client.setup_logging()
    logging.info("Google Cloud Logging client initialized for project: arenamaxx")
except Exception as _log_err:
    logging.basicConfig(level=logging.INFO)
    logging.info(f"Standard logging active (GCP not available: {_log_err})")

logger = logging.getLogger(__name__)

# ─── Gemini AI Configuration (Google Generative AI) ──────────────────────────
_GEMINI_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
if _GEMINI_API_KEY:
    genai.configure(api_key=_GEMINI_API_KEY)
    logger.info("Google Gemini AI (gemini-1.5-flash) configured successfully.")
else:
    logger.warning("GOOGLE_API_KEY not set — Gemini running in smart mock mode.")

# ─── App Init ─────────────────────────────────────────────────────────────────
app = Flask(__name__, static_folder='../frontend/dist', static_url_path='/')
app.config.update(
    SECRET_KEY=os.getenv('SECRET_KEY', 'arenamaxx_stadium_secret_2026'),
    SQLALCHEMY_DATABASE_URI='sqlite:///stadium.db',
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    SQLALCHEMY_ECHO=False,
    CACHE_TYPE='SimpleCache',
    CACHE_DEFAULT_TIMEOUT=CACHE_TIMEOUT_SECONDS,
)

# ─── Extensions ───────────────────────────────────────────────────────────────
CORS(app, resources={r"/api/*": {"origins": "*"}})
db.init_app(app)
cache = Cache(app)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["300 per day", "100 per hour"],
    storage_uri="memory://"
)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')
simulator = CrowdSimulator(socketio)

# ─── Firebase / Firestore Init ────────────────────────────────────────────────
_firebase_ready: bool = initialize_firebase()
logger.info(f"Firebase Admin SDK status: {'active' if _firebase_ready else 'graceful-degradation'}")


# ─── Utility Helpers ──────────────────────────────────────────────────────────
def sanitize_string(value: Any, max_length: int = MAX_FIELD_LENGTH) -> str:
    """Strip whitespace, truncate, and block known injection patterns."""
    if not isinstance(value, str):
        return ""
    cleaned = value.strip()[:max_length]
    if INJECTION_PATTERN.search(cleaned):
        logger.warning(f"Potential injection attempt blocked: {cleaned[:100]}")
        return ""
    return cleaned


def validate_required(data: dict, fields: list[str]) -> tuple[bool, str]:
    """Assert that all required fields are present and non-empty in a request dict."""
    for field in fields:
        if not data.get(field):
            return False, f"Missing required field: '{field}'"
    return True, ""


def require_json(func):
    """Decorator: enforce strict Content-Type: application/json on POST routes."""
    from functools import wraps
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        if request.method == 'POST' and not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 415
        return func(*args, **kwargs)
    return wrapper


# ─── Database Init ────────────────────────────────────────────────────────────
def initialize_database() -> None:
    """Create all database tables and seed with mock data if the database is empty."""
    with app.app_context():
        db.create_all()
        if Seat.query.count() == 0:
            if User.query.count() == 0:
                mock_user = User(name="Test Attendee", role="attendee")
                db.session.add(mock_user)
            for i in range(1, 51):
                db.session.add(Seat(block='A', row='1', number=i))
                db.session.add(Seat(block='B', row='1', number=i))
            db.session.commit()
            logger.info("Database seeded with 100 mock seats and 1 test user.")


# ─── Security Headers ─────────────────────────────────────────────────────────
@app.after_request
def set_security_headers(response):
    """Attach OWASP-recommended security headers to every HTTP response."""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=()'
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline' fonts.googleapis.com; "
        "font-src fonts.gstatic.com; "
        "connect-src 'self' wss: ws:;"
    )
    return response


# ─── Error Handlers ───────────────────────────────────────────────────────────
@app.errorhandler(404)
def not_found(e) -> Any:
    """Serve the React SPA for all unmatched routes (client-side routing fallback)."""
    return send_from_directory(app.static_folder, 'index.html')


@app.errorhandler(429)
def rate_limit_exceeded(e) -> tuple:
    """Return structured JSON when a client exceeds the configured rate limit."""
    logger.warning(f"Rate limit exceeded from {get_remote_address()}")
    return jsonify({"error": "Rate limit exceeded. Please slow down.", "retry_after": str(e.description)}), 429


@app.errorhandler(415)
def unsupported_media(e) -> tuple:
    """Return structured JSON for unsupported content type errors."""
    return jsonify({"error": "Content-Type must be application/json"}), 415


# ─── Static Routes ───────────────────────────────────────────────────────────
@app.route('/')
def serve_index() -> Any:
    """Serve the compiled React/Vite frontend SPA entry point."""
    return send_from_directory(app.static_folder, 'index.html')


# ─── Health & Diagnostics ────────────────────────────────────────────────────
@app.route('/api/health', methods=['GET'])
def health_check() -> tuple:
    """
    Cloud Run liveness and readiness health probe endpoint.

    Returns platform version, active Google services, and Firebase status.
    This endpoint is used by Cloud Run for uptime monitoring.
    """
    return jsonify({
        "status": "healthy",
        "version": __version__,
        "service": "ArenaMaxx Platform",
        "google_cloud_services": [
            "Cloud Run (Hosting)",
            "Cloud Logging (Structured Logs)",
            "Cloud Firestore (Event Storage)",
            "Gemini AI / gemini-1.5-flash (AI Concierge)",
            "Firebase Admin SDK (Backend Auth Ready)"
        ],
        "firebase_status": "active" if _firebase_ready else "graceful-degradation",
        "region": os.getenv("GOOGLE_CLOUD_REGION", "us-central1"),
    }), 200


# ─── Seats API ────────────────────────────────────────────────────────────────
@app.route('/api/seats', methods=['GET'])
@cache.cached(timeout=CACHE_TIMEOUT_SECONDS, query_string=True)
@limiter.limit("30 per minute")
def get_seats() -> tuple:
    """
    Return a paginated list of stadium seats from the database.

    Query params:
        page (int): Page number, 1-indexed. Default: 1.
        per_page (int): Results per page. Max: 100. Default: 20.

    Returns:
        JSON with keys: seats, total, pages, current_page.
    """
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    pagination = Seat.query.paginate(page=page, per_page=per_page, error_out=False)
    seats = [{
        "id": s.id, "block": s.block, "row": s.row,
        "number": s.number, "status": s.status
    } for s in pagination.items]
    return jsonify({
        "seats": seats,
        "total": pagination.total,
        "pages": pagination.pages,
        "current_page": page
    }), 200


# ─── Concessions API ─────────────────────────────────────────────────────────
@app.route('/api/concessions/order', methods=['POST'])
@require_json
@limiter.limit("10 per minute")
def place_order() -> tuple:
    """
    Place a food/beverage order and assign a virtual queue number.

    Expects JSON body: { "items": "<order description>", "user_id": <int> }

    On success, logs the order event to Google Cloud Firestore.

    Returns:
        JSON with keys: success, queue_number, status, estimated_wait_mins.
    """
    data = request.get_json(silent=True) or {}
    ok, err = validate_required(data, ['items'])
    if not ok:
        return jsonify({"error": err}), 400

    items = sanitize_string(str(data.get('items', '')), max_length=MAX_ITEMS_LENGTH)
    if not items:
        return jsonify({"error": "Order items cannot be empty or contain invalid content."}), 400

    user_id = int(data.get('user_id', 1))
    last_order = Order.query.order_by(Order.queue_number.desc()).first()
    q_num = (last_order.queue_number + 1) if last_order else 100

    new_order = Order(user_id=user_id, items=items, queue_number=q_num, status='Preparing')
    db.session.add(new_order)
    db.session.commit()

    # ── Log to Google Cloud Firestore ──────────────────────────────────────
    log_event("concession_orders", {
        "user_id": user_id,
        "items": items,
        "queue_number": q_num,
        "status": "Preparing",
    })
    logger.info(f"Order placed: Queue #{q_num} | Items: {items[:50]}")

    return jsonify({
        "success": True,
        "queue_number": q_num,
        "status": "Preparing",
        "estimated_wait_mins": max(2, (q_num % 100) * 2),
    }), 200


# ─── Washrooms API ────────────────────────────────────────────────────────────
@app.route('/api/washrooms/book', methods=['POST'])
@require_json
@limiter.limit("5 per minute")
def book_washroom() -> tuple:
    """
    Reserve a washroom time slot at a specified stadium block.

    Expects JSON body: { "block": "<block_name>", "time_slot": "<time>", "user_id": <int> }
    Valid blocks: Block_A, Block_B, Block_C (and gender variants _m/_w).

    On success, logs the booking to Google Cloud Firestore.

    Returns:
        JSON with keys: success, message.
    """
    data = request.get_json(silent=True) or {}
    ok, err = validate_required(data, ['block', 'time_slot'])
    if not ok:
        return jsonify({"error": err}), 400

    block = sanitize_string(data.get('block', ''), max_length=MAX_FIELD_LENGTH)
    time_slot = sanitize_string(data.get('time_slot', ''), max_length=MAX_FIELD_LENGTH)

    if block not in VALID_WASHROOM_BLOCKS:
        return jsonify({"error": f"Invalid block '{block}'. Must be one of: {VALID_WASHROOM_BLOCKS}"}), 400
    if not time_slot:
        return jsonify({"error": "time_slot cannot be empty."}), 400

    user_id = int(data.get('user_id', 1))
    ws = WashroomSlot(user_id=user_id, block=block, time_slot=time_slot, status='Booked')
    db.session.add(ws)
    db.session.commit()

    # ── Log to Google Cloud Firestore ──────────────────────────────────────
    log_event("washroom_bookings", {
        "user_id": user_id,
        "block": block,
        "time_slot": time_slot,
        "status": "Booked",
    })
    logger.info(f"Washroom booked: {block} @ {time_slot} for user {user_id}")

    return jsonify({"success": True, "message": f"Washroom at {block} booked for {time_slot}."}), 200


# ─── Recent Events API (Firestore Read) ──────────────────────────────────────
@app.route('/api/events/recent', methods=['GET'])
@cache.cached(timeout=10)
@limiter.limit("20 per minute")
def recent_events() -> tuple:
    """
    Retrieve recent stadium events from Google Cloud Firestore.

    This endpoint demonstrates live read access to the Cloud Firestore
    event log populated by orders and washroom bookings.

    Query params:
        collection (str): Firestore collection name. Default: 'concession_orders'.
        limit (int): Max results. Default: 10, Max: 50.

    Returns:
        JSON with keys: collection, events, firebase_active.
    """
    collection = request.args.get('collection', 'concession_orders')
    limit = min(request.args.get('limit', 10, type=int), 50)
    events = get_recent_events(collection, limit=limit)
    return jsonify({
        "collection": collection,
        "events": events,
        "firebase_active": _firebase_ready,
    }), 200


# ─── Gemini AI Chat API ───────────────────────────────────────────────────────
@app.route('/api/gemini/chat', methods=['POST'])
@require_json
@limiter.limit("20 per minute")
def gemini_chat() -> tuple:
    """
    Process a user message through Google Gemini AI (gemini-1.5-flash).

    Expects JSON body: { "message": "<user text>" }

    The response may include 'ACTION:NAVIGATE:/route' for agentic navigation.
    All interactions are logged to Google Cloud Firestore for analytics.

    Falls back to smart keyword-matching if GOOGLE_API_KEY is unset.

    Returns:
        JSON with keys: reply, [error].
    """
    data = request.get_json(silent=True) or {}
    ok, err = validate_required(data, ['message'])
    if not ok:
        return jsonify({"error": err}), 400

    user_msg = sanitize_string(data.get('message', ''), max_length=MAX_MESSAGE_LENGTH)
    if not user_msg:
        return jsonify({"error": "Message cannot be empty or contain invalid content."}), 400

    system_prompt = (
        "You are the ArenaMaxx AI Stadium Concierge, powered by Google Gemini. "
        "Help attendees navigate and enjoy their experience. "
        "Pages: /dashboard (Live Overview), /food (Order Food), /washrooms (Restrooms), /wayfinding (AR Map). "
        "To navigate, end your reply with: ACTION:NAVIGATE:/page_name"
    )

    reply: str = ""
    nav_action: str | None = None

    if not _GEMINI_API_KEY or "your_gemini" in _GEMINI_API_KEY:
        # Smart keyword mock mode
        msg_lower = user_msg.lower()
        if any(k in msg_lower for k in ["food", "eat", "hungry", "drink", "snack"]):
            reply = "Heading to the Food & Beverages section now! ACTION:NAVIGATE:/food"
        elif any(k in msg_lower for k in ["washroom", "toilet", "restroom", "bathroom", "loo"]):
            reply = "Navigating to the Washroom booking page. ACTION:NAVIGATE:/washrooms"
        elif any(k in msg_lower for k in ["map", "where", "navigate", "lost", "direction", "find"]):
            reply = "Opening the AR Wayfinding Map for you. ACTION:NAVIGATE:/wayfinding"
        elif any(k in msg_lower for k in ["dashboard", "crowd", "gate", "live", "status"]):
            reply = "Taking you to the Live Stadium Dashboard. ACTION:NAVIGATE:/dashboard"
        else:
            reply = (
                "I'm the ArenaMaxx AI Concierge (powered by Google Gemini)! "
                "Ask me about food, washrooms, stadium navigation, or live status."
            )
    else:
        try:
            model = genai.GenerativeModel(
                model_name='gemini-1.5-flash',
                system_instruction=system_prompt
            )
            response = model.generate_content(user_msg)
            reply = response.text
            logger.info("Google Gemini (gemini-1.5-flash) response generated.")
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return jsonify({"reply": "AI concierge is temporarily unavailable. Please try again.", "error": True}), 503

    if "ACTION:NAVIGATE:" in reply:
        nav_action = reply.split("ACTION:NAVIGATE:")[-1].strip().split()[0]

    # ── Log chat to Google Cloud Firestore ─────────────────────────────────
    log_ai_chat(user_msg, reply, nav_action)

    return jsonify({"reply": reply}), 200


# ─── WebSocket Events ─────────────────────────────────────────────────────────
@socketio.on('connect')
def handle_connect() -> None:
    """Handle a new WebSocket client connection. Logs to GCP."""
    logger.info(f"WebSocket client connected")


@socketio.on('disconnect')
def handle_disconnect() -> None:
    """Handle a WebSocket client disconnection. Logs to GCP."""
    logger.info("WebSocket client disconnected")


# ─── Entry Point ──────────────────────────────────────────────────────────────
if __name__ == '__main__':
    initialize_database()
    simulator.start()
    port = int(os.environ.get("PORT", DEFAULT_PORT))
    logger.info(f"ArenaMaxx v{__version__} starting on port {port}")
    socketio.run(app, debug=False, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)
