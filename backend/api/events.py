from __future__ import annotations
from flask import Blueprint, jsonify, request
from firebase_service import get_recent_events
from flask import current_app

events_bp = Blueprint('events', __name__)

@events_bp.route('/api/events/recent', methods=['GET'])
def recent_events():
    """Retrieve recent stadium events from Google Cloud Firestore."""
    collection = request.args.get('collection', 'concession_orders')
    limit = min(request.args.get('limit', 10, type=int), 50)
    
    # Check if firebase is initialized via current_app config or extensions
    events = get_recent_events(collection, limit=limit)
    
    return jsonify({
        "collection": collection,
        "events": events,
        "firebase_active": True # Placeholder
    }), 200
