"""
firebase_service.py — Google Firebase & Firestore Integration for ArenaMaxx.

This module manages all interactions with Google Firebase services:
  - Firebase Admin SDK initialization
  - Firestore document writes (orders, bookings, AI chat logs)
  - Firestore document reads for event history
  - Firebase Analytics event logging

Cloud Services Used:
  - Firebase Admin SDK (google.firebase_adminsdk)
  - Google Cloud Firestore (real-time NoSQL database)
  - Google Cloud Logging (via firebase_admin)
"""

from __future__ import annotations
import os
import logging
import datetime
from typing import Any

logger = logging.getLogger(__name__)

# ─── Firebase Initialization ──────────────────────────────────────────────────
_firebase_initialized: bool = False
_firestore_client: Any = None

def initialize_firebase() -> bool:
    """
    Initialize the Firebase Admin SDK using a service account or Application Default Credentials.

    In production (Cloud Run), uses the default service account credentials.
    In development, falls back to graceful degradation with local logging.

    Returns:
        bool: True if Firebase was successfully initialized, False otherwise.
    """
    global _firebase_initialized, _firestore_client

    if _firebase_initialized:
        return True

    try:
        import firebase_admin
        from firebase_admin import credentials, firestore

        if not firebase_admin._apps:
            # Use Application Default Credentials (works on Cloud Run automatically)
            cred = credentials.ApplicationDefault()
            firebase_admin.initialize_app(cred, {
                'projectId': os.getenv('GOOGLE_CLOUD_PROJECT', 'arenamaxx'),
            })

        _firestore_client = firestore.client()
        _firebase_initialized = True
        logger.info("✅ Firebase Admin SDK initialized. Firestore client ready.")
        return True

    except Exception as e:
        logger.warning(f"⚠️ Firebase initialization skipped (running locally without credentials): {e}")
        _firebase_initialized = False
        return False


def log_event(collection: str, data: dict) -> str | None:
    """
    Write a structured event document to a Google Cloud Firestore collection.

    This is the primary method for persisting real-time stadium events such as
    food orders, washroom slot bookings, and AI chat interactions.

    Args:
        collection: The Firestore collection name (e.g., 'orders', 'washroom_bookings').
        data: A dictionary of fields to store in the Firestore document.

    Returns:
        str | None: The new Firestore document ID on success, or None on failure.
    """
    if not _firebase_initialized or _firestore_client is None:
        logger.debug(f"[Firestore-Stub] Event logged to '{collection}': {data}")
        return None

    try:
        from firebase_admin import firestore
        doc_data = {
            **data,
            "timestamp": firestore.SERVER_TIMESTAMP,
            "source": "ArenaMaxx-CloudRun",
            "environment": os.getenv("K_SERVICE", "local"),
        }
        _, doc_ref = _firestore_client.collection(collection).add(doc_data)
        logger.info(f"Firestore event written to '{collection}': {doc_ref.id}")
        return doc_ref.id
    except Exception as e:
        logger.error(f"Firestore write failed for collection '{collection}': {e}")
        return None


def get_recent_events(collection: str, limit: int = 10) -> list[dict]:
    """
    Retrieve the most recent event documents from a Firestore collection.

    Args:
        collection: The Firestore collection name to query.
        limit: Maximum number of documents to return (default: 10).

    Returns:
        list[dict]: A list of document data dictionaries, ordered by most recent first.
    """
    if not _firebase_initialized or _firestore_client is None:
        logger.debug(f"[Firestore-Stub] Reading from '{collection}' (Firebase offline)")
        return []

    try:
        docs = (
            _firestore_client.collection(collection)
            .order_by("timestamp", direction="DESCENDING")
            .limit(limit)
            .stream()
        )
        return [{"id": doc.id, **doc.to_dict()} for doc in docs]
    except Exception as e:
        logger.error(f"Firestore read failed for collection '{collection}': {e}")
        return []


def log_ai_chat(user_message: str, ai_reply: str, navigation_action: str | None = None) -> None:
    """
    Persist an AI chat interaction to Firestore for analytics and audit purposes.

    Args:
        user_message: The raw user message sent to the Gemini AI.
        ai_reply: The AI-generated response returned to the user.
        navigation_action: Optional navigation action parsed from the AI reply.
    """
    log_event("ai_chat_logs", {
        "user_message": user_message[:500],
        "ai_reply": ai_reply[:1000],
        "navigation_action": navigation_action,
        "model": "gemini-1.5-flash",
        "service": "Google Generative AI",
    })
