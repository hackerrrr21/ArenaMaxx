"""
ArenaMaxx Stadium Management Platform — Backend API
Deployed on Google Cloud Run. Uses Google Cloud Logging and Google Gemini AI.
"""
import os
import logging
from flask import Flask, jsonify, request, send_from_directory
from flask_socketio import SocketIO
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
from models import db, User, Seat, Ticket, Order, WashroomSlot
from simulation import CrowdSimulator
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# ─── Google Cloud Logging Setup ───────────────────────────────────────────────
try:
    import google.cloud.logging
    gcp_client = google.cloud.logging.Client()
    gcp_client.setup_logging()
    logging.info("Google Cloud Logging initialized.")
except Exception:
    logging.basicConfig(level=logging.INFO)
    logging.info("Running with standard logging (GCP not available locally).")

logger = logging.getLogger(__name__)

# ─── App Init ─────────────────────────────────────────────────────────────────
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

app = Flask(__name__, static_folder='../frontend/dist', static_url_path='/')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'living_stadium_secret_2026')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stadium.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['CACHE_TYPE'] = 'SimpleCache'
app.config['CACHE_DEFAULT_TIMEOUT'] = 30

# ─── Extensions ───────────────────────────────────────────────────────────────
CORS(app, resources={r"/api/*": {"origins": "*"}})
db.init_app(app)
cache = Cache(app)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "60 per hour"],
    storage_uri="memory://"
)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')
simulator = CrowdSimulator(socketio)


# ─── Helpers ──────────────────────────────────────────────────────────────────
def sanitize_string(value: str, max_length: int = 200) -> str:
    """Strip and truncate a string to prevent injection and DoS attacks."""
    if not isinstance(value, str):
        return ""
    return value.strip()[:max_length]


def validate_required(data: dict, fields: list) -> tuple[bool, str]:
    """Check that all required fields are present and non-empty in a request body."""
    for field in fields:
        if not data.get(field):
            return False, f"Missing required field: '{field}'"
    return True, ""


# ─── Database Init ────────────────────────────────────────────────────────────
def initialize_database() -> None:
    """Create all tables and seed with mock data if the database is empty."""
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
            logger.info("Database initialized with mock seats.")


# ─── Security Headers ─────────────────────────────────────────────────────────
@app.after_request
def set_security_headers(response):
    """Attach security headers to all responses."""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    return response


# ─── Static File Serving ──────────────────────────────────────────────────────
@app.route('/')
def serve_index():
    """Serve the compiled React frontend SPA."""
    return send_from_directory(app.static_folder, 'index.html')


@app.errorhandler(404)
def not_found(e):
    """Fallback route for React client-side deep links."""
    return send_from_directory(app.static_folder, 'index.html')


@app.errorhandler(429)
def rate_limit_exceeded(e):
    """Return a structured error when a client hits the rate limit."""
    return jsonify({"error": "Rate limit exceeded. Please slow down your requests.", "retry_after": str(e.description)}), 429


# ─── Health Endpoint ─────────────────────────────────────────────────────────
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint for Cloud Run liveness probes and uptime monitoring."""
    return jsonify({
        "status": "healthy",
        "service": "ArenaMaxx Backend",
        "google_services": ["Cloud Run", "Cloud Logging", "Gemini AI"],
        "version": "2.0.0"
    }), 200


# ─── Seats API ────────────────────────────────────────────────────────────────
@app.route('/api/seats', methods=['GET'])
@cache.cached(timeout=30, query_string=True)
@limiter.limit("30 per minute")
def get_seats():
    """
    Return paginated seat inventory.
    Query params: ?page=1&per_page=20
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
    })


# ─── Concessions API ─────────────────────────────────────────────────────────
@app.route('/api/concessions/order', methods=['POST'])
@limiter.limit("10 per minute")
def place_order():
    """
    Place a food order and return a virtual queue number.
    Expects JSON: { "items": "<order string>" }
    """
    data = request.get_json(silent=True) or {}
    ok, err = validate_required(data, ['items'])
    if not ok:
        return jsonify({"error": err}), 400

    items = sanitize_string(str(data.get('items', '')), max_length=500)
    if not items:
        return jsonify({"error": "Order items cannot be empty."}), 400

    user_id = data.get('user_id', 1)
    last_order = Order.query.order_by(Order.queue_number.desc()).first()
    q_num = (last_order.queue_number + 1) if last_order else 100
    new_order = Order(user_id=user_id, items=items, queue_number=q_num, status='Preparing')
    db.session.add(new_order)
    db.session.commit()
    logger.info(f"New order placed: Queue #{q_num}")
    return jsonify({
        "success": True,
        "queue_number": q_num,
        "status": "Preparing",
        "estimated_wait_mins": max(2, (q_num % 100) * 2)
    })


# ─── Washrooms API ────────────────────────────────────────────────────────────
@app.route('/api/washrooms/book', methods=['POST'])
@limiter.limit("5 per minute")
def book_washroom():
    """
    Book a washroom slot.
    Expects JSON: { "block": "<block_name>", "time_slot": "<time>" }
    """
    data = request.get_json(silent=True) or {}
    ok, err = validate_required(data, ['block', 'time_slot'])
    if not ok:
        return jsonify({"error": err}), 400

    block = sanitize_string(data.get('block', ''), max_length=50)
    time_slot = sanitize_string(data.get('time_slot', ''), max_length=50)
    user_id = data.get('user_id', 1)

    VALID_BLOCKS = ['Block_A', 'Block_B', 'Block_C', 'Block_A_m', 'Block_B_m',
                    'Block_C_m', 'Block_A_w', 'Block_B_w', 'Block_C_w']
    if block not in VALID_BLOCKS:
        return jsonify({"error": f"Invalid block: '{block}'"}), 400

    ws = WashroomSlot(user_id=user_id, block=block, time_slot=time_slot, status='Booked')
    db.session.add(ws)
    db.session.commit()
    logger.info(f"Washroom booked: {block} @ {time_slot}")
    return jsonify({"success": True, "message": f"Washroom at {block} booked for {time_slot}."})


# ─── Gemini AI Chat API ───────────────────────────────────────────────────────
@app.route('/api/gemini/chat', methods=['POST'])
@limiter.limit("20 per minute")
def gemini_chat():
    """
    Process a user message via Google Gemini AI (gemini-1.5-flash).
    Falls back to smart mock mode if GOOGLE_API_KEY is not configured.
    Expects JSON: { "message": "<user message>" }
    """
    data = request.get_json(silent=True) or {}
    ok, err = validate_required(data, ['message'])
    if not ok:
        return jsonify({"error": err}), 400

    user_msg = sanitize_string(data.get('message', ''), max_length=1000)
    if not user_msg:
        return jsonify({"error": "Message cannot be empty."}), 400

    api_key = os.getenv("GOOGLE_API_KEY")

    system_prompt = (
        "You are the ArenaMaxx Stadium Assistant. Help users with stadium navigation and info. "
        "Pages: /dashboard (Overview), /food (Order Food), /washrooms (Restrooms), /wayfinding (AR Map). "
        "If a user wants to navigate, include 'ACTION:NAVIGATE:/page_name' at the end."
    )

    if not api_key or "your_gemini_api_key_here" in api_key:
        msg_lower = user_msg.lower()
        if any(k in msg_lower for k in ["food", "eat", "hungry", "drink"]):
            return jsonify({"reply": "Heading to the Food court now! ACTION:NAVIGATE:/food"})
        if any(k in msg_lower for k in ["washroom", "toilet", "restroom", "bathroom"]):
            return jsonify({"reply": "Navigating to the Washroom booking page. ACTION:NAVIGATE:/washrooms"})
        if any(k in msg_lower for k in ["map", "where", "navigate", "lost", "direction"]):
            return jsonify({"reply": "Opening the AR Wayfinding map. ACTION:NAVIGATE:/wayfinding"})
        if any(k in msg_lower for k in ["dashboard", "crowd", "gate", "live"]):
            return jsonify({"reply": "Taking you to the live stadium dashboard. ACTION:NAVIGATE:/dashboard"})
        return jsonify({"reply": "I'm the ArenaMaxx AI Concierge! Ask me about food, washrooms, navigation, or the live dashboard."})

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(f"{system_prompt}\n\nUser: {user_msg}")
        logger.info("Gemini AI response generated successfully.")
        return jsonify({"reply": response.text})
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        return jsonify({"reply": "I'm having trouble connecting right now. Please try again shortly.", "error": True}), 503


# ─── WebSocket Events ─────────────────────────────────────────────────────────
@socketio.on('connect')
def handle_connect():
    """Handle a new WebSocket client connection."""
    logger.info('Client connected via WebSocket')


@socketio.on('disconnect')
def handle_disconnect():
    """Handle a WebSocket client disconnection."""
    logger.info('Client disconnected')


# ─── Entry Point ──────────────────────────────────────────────────────────────
if __name__ == '__main__':
    initialize_database()
    simulator.start()
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, debug=False, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)
