import os
from flask import Flask, jsonify, request, send_from_directory
from flask_socketio import SocketIO
from flask_cors import CORS
from models import db, User, Seat, Ticket, Order, WashroomSlot
from simulation import CrowdSimulator
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

app = Flask(__name__, static_folder='../frontend/dist', static_url_path='/')
# Configurations
app.config['SECRET_KEY'] = 'living_stadium_secret_2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stadium.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Init extensions
CORS(app)
db.init_app(app)
socketio = SocketIO(app, cors_allowed_origins="*")

simulator = CrowdSimulator(socketio)

def initialize_database():
    with app.app_context():
        db.create_all()
        # Seed mock data if empty
        if Seat.query.count() == 0:
            # Create a mock user
            if User.query.count() == 0:
                mock_user = User(name="Test Attendee", role="attendee")
                db.session.add(mock_user)
                
            # Create mock seats
            for i in range(1, 51):
                db.session.add(Seat(block='A', row='1', number=i))
                db.session.add(Seat(block='B', row='1', number=i))
            db.session.commit()
            print("Database initialized with mock seats.")
 
# Serve React Frontend
@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')
 
@app.errorhandler(404)
def not_found(e):
    # This ensures that deep links in React routing work correctly
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/api/seats', methods=['GET'])
def get_seats():
    seats = Seat.query.all()
    res = []
    for s in seats:
        res.append({
            "id": s.id, "block": s.block, "row": s.row, "number": s.number, "status": s.status
        })
    return jsonify(res)

@app.route('/api/concessions/order', methods=['POST'])
def place_order():
    data = request.json
    user_id = data.get('user_id', 1) # Mock User default
    items = str(data.get('items', 'Standard Meal'))
    
    last_order = Order.query.order_by(Order.queue_number.desc()).first()
    q_num = (last_order.queue_number + 1) if last_order else 100
    
    new_order = Order(user_id=user_id, items=items, queue_number=q_num, status='Preparing')
    db.session.add(new_order)
    db.session.commit()
    
    return jsonify({"success": True, "queue_number": q_num, "status": "Preparing", "estimated_wait_mins": max(2, (q_num % 100) * 2)})

@app.route('/api/washrooms/book', methods=['POST'])
def book_washroom():
    data = request.json
    block = data.get('block', 'Block_A')
    time_slot = data.get('time_slot', 'Now')
    user_id = data.get('user_id', 1)
    
    ws = WashroomSlot(user_id=user_id, block=block, time_slot=time_slot, status='Booked')
    db.session.add(ws)
    db.session.commit()
    return jsonify({"success": True, "message": f"Washroom at {block} booked for {time_slot}."})

@app.route('/api/gemini/chat', methods=['POST'])
def gemini_chat():
    data = request.json
    user_msg = data.get('message', '')
    
    api_key = os.getenv("GOOGLE_API_KEY")
    
    # SYSTEM CONTEXT
    system_prompt = (
        "You are the ArenaMaxx Stadium Assistant. Helping users with navigation and stadium info. "
        "Pages available: /dashboard (Overview), /food (Order Food), /washrooms (Restrooms), /wayfinding (AR Map). "
        "If a user wants to go to a page, include 'ACTION:NAVIGATE:/page_name' at the end of your response."
    )

    if not api_key or "your_gemini_api_key_here" in api_key:
        # SMART MOCK MODE
        msg_lower = user_msg.lower()
        if "food" in msg_lower or "eat" in msg_lower:
            return jsonify({"reply": "I can help with that! Heading to the Food court now. ACTION:NAVIGATE:/food"})
        if "washroom" in msg_lower or "toilet" in msg_lower:
            return jsonify({"reply": "Sure thing. Navigating to the Washroom booking page. ACTION:NAVIGATE:/washrooms"})
        if "map" in msg_lower or "where" in msg_lower:
            return jsonify({"reply": "Opening the AR Wayfinding map for you. ACTION:NAVIGATE:/wayfinding"})
        return jsonify({"reply": "I'm the ArenaMaxx Concierge! How can I assist you today? (Note: Gemini API key not configured, running in Mock Mode)"})

    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(f"{system_prompt}\n\nUser: {user_msg}")
        return jsonify({"reply": response.text})
    except Exception as e:
        return jsonify({"reply": f"Error connecting to Gemini: {str(e)}", "error": True})

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    initialize_database()
    simulator.start()
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, debug=False, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)
