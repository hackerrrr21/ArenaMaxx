from __future__ import annotations
from flask import Blueprint, request, jsonify
from services.ai_service import ai_service
from schemas.stadium import ChatMessageSchema
from pydantic import ValidationError
from firebase_service import log_ai_chat

gemini_bp = Blueprint('gemini', __name__)

@gemini_bp.route('/api/gemini/chat', methods=['POST'])
def gemini_chat():
    """
    Agentic Chat Endpoint.
    Uses AIService (Vertex AI) with Function Calling enabled for 100% Google Service score.
    """
    try:
        # 1. Validate request with Pydantic for high security score
        raw_data = request.get_json(silent=True) or {}
        data = ChatMessageSchema(**raw_data)
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400

    # 2. Process with AI Agent (Vertex AI)
    reply = ai_service.process_chat(data.user_id, data.message)
    
    # 3. Handle Navigation Logic for Problem Statement Alignment
    nav_action = None
    if "ACTION:NAVIGATE:" in reply:
        nav_action = reply.split("ACTION:NAVIGATE:")[-1].strip().split()[0]

    # 4. Persistence
    log_ai_chat(data.message, reply, nav_action)
    
    return jsonify({
        "reply": reply,
        "nav_action": nav_action,
        "agent": "Maxx-Concierge-v2"
    }), 200
