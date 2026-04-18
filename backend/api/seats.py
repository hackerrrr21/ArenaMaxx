from __future__ import annotations
from flask import Blueprint, jsonify, request
from models import Seat, db
from flask_caching import Cache

# We'll use a placeholder for cache; will be initialized in app.py
seats_bp = Blueprint('seats', __name__)

@seats_bp.route('/api/seats', methods=['GET'])
def get_seats():
    """Return a paginated list of stadium seats."""
    # Note: Use current_app.extensions['cache'] or similar if needed, 
    # but for simplicity we'll assume global cache is handled or just pass it in.
    from flask import current_app
    cache = current_app.extensions.get('cache')
    
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
