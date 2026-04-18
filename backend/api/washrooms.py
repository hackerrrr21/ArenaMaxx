from __future__ import annotations
import logging
from flask import Blueprint, jsonify, request
from models import WashroomSlot, db
from firebase_service import log_event

logger = logging.getLogger(__name__)
washrooms_bp = Blueprint('washrooms', __name__)

VALID_WASHROOM_BLOCKS = [
    'Block_A', 'Block_B', 'Block_C',
    'Block_A_m', 'Block_B_m', 'Block_C_m',
    'Block_A_w', 'Block_B_w', 'Block_C_w'
]

@washrooms_bp.route('/api/washrooms/book', methods=['POST'])
def book_washroom():
    """Reserve a washroom time slot."""
    from app import sanitize_string, validate_required, MAX_FIELD_LENGTH
    
    data = request.get_json(silent=True) or {}
    ok, err = validate_required(data, ['block', 'time_slot'])
    if not ok:
        return jsonify({"error": err}), 400

    block = sanitize_string(data.get('block', ''), max_length=MAX_FIELD_LENGTH)
    time_slot = sanitize_string(data.get('time_slot', ''), max_length=MAX_FIELD_LENGTH)

    if block not in VALID_WASHROOM_BLOCKS:
        return jsonify({"error": f"Invalid block '{block}'."}), 400

    user_id = int(data.get('user_id', 1))
    ws = WashroomSlot(user_id=user_id, block=block, time_slot=time_slot, status='Booked')
    db.session.add(ws)
    db.session.commit()

    log_event("washroom_bookings", {
        "user_id": user_id,
        "block": block,
        "time_slot": time_slot,
        "status": "Booked",
    })
    
    return jsonify({"success": True, "message": f"Washroom at {block} booked for {time_slot}."}), 200
