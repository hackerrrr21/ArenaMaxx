from __future__ import annotations
import logging
from flask import Blueprint, jsonify, request
from models import Order, db
from firebase_service import log_event, archive_receipt_to_gcs

logger = logging.getLogger(__name__)
concessions_bp = Blueprint('concessions', __name__)

MAX_ITEMS_LENGTH = 500

@concessions_bp.route('/api/concessions/order', methods=['POST'])
def place_order():
    """Place a food/beverage order and assign a virtual queue number."""
    from app import sanitize_string, validate_required
    
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

    # Firestore & GCS
    log_event("concession_orders", {
        "user_id": user_id,
        "items": items,
        "queue_number": q_num,
        "status": "Preparing",
    })
    archive_receipt_to_gcs(str(q_num), {
        "id": q_num,
        "user_id": user_id,
        "items": items,
        "timestamp": str(new_order.created_at)
    })
    
    logger.info(f"Order placed: Queue #{q_num}")

    return jsonify({
        "success": True,
        "queue_number": q_num,
        "status": "Preparing",
        "estimated_wait_mins": max(2, (q_num % 100) * 2),
    }), 200
