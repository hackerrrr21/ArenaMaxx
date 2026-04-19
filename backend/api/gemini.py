"""
gemini.py — Gemini AI Chat Blueprint for ArenaMaxx.

Exposes the /api/gemini/chat endpoint which drives the Maxx Concierge.
Uses AIService (Google Generative AI + Vertex AI Function Calling) and
Pydantic validation for enterprise-grade input handling.

Google Cloud Services used:
  - Google Generative AI (Gemini 1.5 Flash)
  - Firebase Firestore (chat log persistence)
"""
from __future__ import annotations

import logging
from flask import Blueprint, request, jsonify
from pydantic import ValidationError

from services.ai_service import ai_service
from schemas.stadium import ChatMessageSchema
from firebase_service import log_ai_chat

logger = logging.getLogger(__name__)
gemini_bp = Blueprint("gemini", __name__)


@gemini_bp.route("/api/gemini/chat", methods=["POST"])
def gemini_chat():
    """
    Agentic Chat endpoint powered by Google Generative AI (Gemini).

    Flow:
      1. Validate request payload using Pydantic (security + quality).
      2. Run the message through the AIService (Gemini + smart routing).
      3. Parse any navigation action from the AI reply.
      4. Persist the conversation to Firestore for analytics.
      5. Return structured JSON with the reply and navigation action.

    Returns:
        JSON with keys: reply, nav_action, agent
        HTTP 200 on success, 400 on validation failure.
    """
    try:
        raw_data = request.get_json(silent=True) or {}
        data = ChatMessageSchema(**raw_data)
    except ValidationError as exc:
        return jsonify({"error": str(exc)}), 400

    # Process with Google AI concierge
    reply = ai_service.process_chat(data.user_id, data.message)

    # Parse navigation action from reply
    nav_action = None
    if "ACTION:NAVIGATE:" in reply:
        nav_action = reply.split("ACTION:NAVIGATE:")[-1].strip().split()[0]

    # Persist to Firestore
    log_ai_chat(data.message, reply, nav_action)

    return jsonify({
        "reply": reply,
        "nav_action": nav_action,
        "agent": "Maxx-Concierge-v2",
        "powered_by": "Google Generative AI — Gemini 1.5 Flash",
    }), 200
