from __future__ import annotations
import os
import logging
import google.generativeai as genai
from flask import Blueprint, jsonify, request
from firebase_service import log_ai_chat

logger = logging.getLogger(__name__)
gemini_bp = Blueprint('gemini', __name__)

MAX_MESSAGE_LENGTH = 1000

@gemini_bp.route('/api/gemini/chat', methods=['POST'])
def gemini_chat():
    """Process a user message through Google Gemini AI with Stadium Context."""
    from app import get_secret, sanitize_string, validate_required
    
    data = request.get_json(silent=True) or {}
    ok, err = validate_required(data, ['message'])
    if not ok:
        return jsonify({"error": err}), 400

    user_msg = sanitize_string(data.get('message', ''), max_length=MAX_MESSAGE_LENGTH)
    if not user_msg:
        return jsonify({"error": "Invalid message content."}), 400

    # ── Intelligent Alignment: Injecting Live Stadium Context ──────────────
    # In a real app, we'd fetch live density/wait times from simulation state
    system_prompt = (
        "You are the ArenaMaxx AI Concierge. "
        "Context: North Gate is currently CONGESTED (Wait time: 15m). "
        "Food Court load is MEDIUM. "
        "Emergency services are active near Block B. "
        "Help attendees navigate. Use ACTION:NAVIGATE:/page if needed."
    )

    _GEMINI_API_KEY = get_secret("GEMINI_API_KEY", os.getenv("GOOGLE_API_KEY", ""))
    
    if not _GEMINI_API_KEY or "your_gemini" in _GEMINI_API_KEY:
        # Smart Mock Logic for testing
        msg_l = user_msg.lower()
        if 'food' in msg_l or 'eat' in msg_l:
            reply = "Our Food Court has great Vada Pav! ACTION:NAVIGATE:/food"
        elif 'toilet' in msg_l or 'washroom' in msg_l:
            reply = "Clean facilities are available at Block A. ACTION:NAVIGATE:/washrooms"
        elif 'map' in msg_l or 'lost' in msg_l or 'where' in msg_l:
            reply = "I've opened the AR Wayfinding map for you. ACTION:NAVIGATE:/wayfinding"
        else:
            reply = "I'm ArenaMaxx AI. Gate A is busy, try Gate C! ACTION:NAVIGATE:/dashboard"
    else:
        try:
            model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=system_prompt)
            response = model.generate_content(user_msg)
            reply = response.text
        except Exception as e:
            logger.error(f"Gemini error: {e}")
            return jsonify({"reply": "AI Concierge is busy.", "error": True}), 503

    nav_action = None
    if "ACTION:NAVIGATE:" in reply:
        nav_action = reply.split("ACTION:NAVIGATE:")[-1].strip().split()[0]

    log_ai_chat(user_msg, reply, nav_action)
    return jsonify({"reply": reply}), 200
