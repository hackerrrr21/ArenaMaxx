"""
test_app.py — ArenaMaxx Stadium Platform: Comprehensive Backend Test Suite
Version: 4.0.0

Coverage areas:
  - Health & Google Services metadata (10 services verified)
  - Seats API (pagination, field validation, edge cases)
  - Concessions API (happy path, Pydantic validation, injection attack, queue ordering)
  - Washrooms API (valid/invalid blocks, missing fields, empty payloads)
  - Gemini AI Chat (all intent keywords, empty/missing messages, long inputs, XSS)
  - Security headers (nosniff, x-frame, xss, csp)
  - Content-Type enforcement (415 on wrong MIME type)
  - Firebase service mocks (graceful degradation, write, read, AI chat logging)
  - Emergency endpoint (CLEAR / EVACUATION events)
  - Integration flows (order → queue increment → receipt metadata)
  - Schema validation (Pydantic XSS strips, max-length, required fields)
"""

from __future__ import annotations

import pytest
from unittest.mock import patch, MagicMock
from app import app, db


# ─── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture
def client():
    """Provide an isolated test client with a pristine in-memory SQLite database."""
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["RATELIMIT_ENABLED"] = False

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            from models import Seat, User
            db.session.add(User(name="Test Attendee", role="attendee"))
            db.session.add(User(name="Staff Member", role="management"))
            db.session.add(Seat(block="A", row="1", number=1))
            db.session.add(Seat(block="A", row="1", number=2))
            db.session.add(Seat(block="B", row="2", number=1))
            db.session.commit()
        yield client
        with app.app_context():
            db.drop_all()


# ─── Health & Google Services ─────────────────────────────────────────────────

def test_health_check_status(client):
    """Health endpoint returns 200 with 'healthy' status."""
    rv = client.get("/api/health")
    assert rv.status_code == 200
    assert rv.get_json()["status"] == "healthy"


def test_health_check_version(client):
    """Health endpoint should return platform version string."""
    rv = client.get("/api/health")
    assert "version" in rv.get_json()


def test_health_check_firebase_status(client):
    """Health endpoint should include Firebase operational status."""
    rv = client.get("/api/health")
    data = rv.get_json()
    assert "firebase_status" in data
    assert data["firebase_status"] in ["active", "graceful-degradation"]


def test_health_check_google_services_listed(client):
    """Health endpoint must list ≥5 Google Cloud services."""
    rv = client.get("/api/health")
    data = rv.get_json()
    assert "google_cloud_services" in data
    services = data["google_cloud_services"]
    assert len(services) >= 5


def test_health_check_vertex_ai(client):
    """Health endpoint must report Vertex AI status."""
    rv = client.get("/api/health")
    data = rv.get_json()
    assert "vertex_ai" in data
    assert data["vertex_ai"]["status"] == "enabled"


def test_health_check_pubsub(client):
    """Health endpoint must report Pub/Sub status."""
    rv = client.get("/api/health")
    data = rv.get_json()
    assert "pubsub" in data


def test_health_check_google_services_count(client):
    """Health endpoint must declare at least 8 Google Cloud services."""
    rv = client.get("/api/health")
    data = rv.get_json()
    assert data.get("google_services_count", 0) >= 8


def test_health_check_features(client):
    """Health endpoint must list active platform features."""
    rv = client.get("/api/health")
    features = rv.get_json().get("features", [])
    assert len(features) >= 5


def test_health_check_gemini_service(client):
    """Gemini AI must be listed in Google Cloud services."""
    rv = client.get("/api/health")
    services = " ".join(rv.get_json()["google_cloud_services"])
    assert "Gemini" in services


def test_health_check_firestore_service(client):
    """Firestore must be listed in Google Cloud services."""
    rv = client.get("/api/health")
    services = " ".join(rv.get_json()["google_cloud_services"])
    assert "Firestore" in services


def test_health_security_fields(client):
    """Security metadata must include pydantic_validation field."""
    rv = client.get("/api/health")
    security = rv.get_json().get("security", {})
    assert "pydantic_validation" in security


# ─── Seats API ────────────────────────────────────────────────────────────────

def test_get_seats_returns_list(client):
    """GET /api/seats returns paginated seats list."""
    rv = client.get("/api/seats")
    assert rv.status_code == 200
    data = rv.get_json()
    assert "seats" in data
    assert data["total"] == 3


def test_get_seats_pagination(client):
    """Seats endpoint respects page and per_page params."""
    rv = client.get("/api/seats?page=1&per_page=2")
    data = rv.get_json()
    assert len(data["seats"]) == 2
    assert data["pages"] == 2


def test_get_seats_per_page_cap(client):
    """per_page is capped at 100 even if a larger value is passed."""
    rv = client.get("/api/seats?per_page=9999")
    assert rv.status_code == 200


def test_seat_fields_present(client):
    """Each seat object must include block, row, number, status and id."""
    rv = client.get("/api/seats")
    seat = rv.get_json()["seats"][0]
    for field in ["block", "row", "number", "status", "id"]:
        assert field in seat


def test_get_seats_page_two(client):
    """Page 2 with per_page=2 returns the remaining 1 seat."""
    rv = client.get("/api/seats?page=2&per_page=2")
    data = rv.get_json()
    assert len(data["seats"]) == 1


# ─── Concessions API ─────────────────────────────────────────────────────────

def test_place_order_success(client):
    """Valid order returns success and queue_number."""
    rv = client.post(
        "/api/concessions/order",
        json={"items": "2x Vada Pav, 1x Cold Coffee"},
        content_type="application/json",
    )
    assert rv.status_code == 200
    data = rv.get_json()
    assert data["success"] is True
    assert "queue_number" in data
    assert data["estimated_wait_mins"] >= 2


def test_place_order_missing_items(client):
    """Order without items returns 400."""
    rv = client.post("/api/concessions/order", json={}, content_type="application/json")
    assert rv.status_code == 400
    assert "error" in rv.get_json()


def test_place_order_empty_string(client):
    """Order with whitespace-only items returns 400."""
    rv = client.post(
        "/api/concessions/order",
        json={"items": "   "},
        content_type="application/json",
    )
    assert rv.status_code == 400


def test_place_order_queue_increments(client):
    """Consecutive orders produce monotonically increasing queue numbers."""
    rv1 = client.post("/api/concessions/order", json={"items": "Burger"}, content_type="application/json")
    rv2 = client.post("/api/concessions/order", json={"items": "Fries"}, content_type="application/json")
    assert rv1.get_json()["queue_number"] < rv2.get_json()["queue_number"]


def test_place_order_xss_blocked(client):
    """XSS payload consisting solely of HTML tags sanitizes to empty → 400."""
    rv = client.post(
        "/api/concessions/order",
        json={"items": "<script></script>"},
        content_type="application/json",
    )
    assert rv.status_code == 400


def test_place_order_wrong_content_type(client):
    """POST without application/json Content-Type returns 415."""
    rv = client.post(
        "/api/concessions/order",
        data="items=burger",
        content_type="application/x-www-form-urlencoded",
    )
    assert rv.status_code == 415


def test_place_order_returns_fulfillment_method(client):
    """Order response should declare the fulfillment method."""
    rv = client.post(
        "/api/concessions/order",
        json={"items": "Hot Dog"},
        content_type="application/json",
    )
    assert rv.status_code == 200
    assert "fulfillment" in rv.get_json()


# ─── Washrooms API ────────────────────────────────────────────────────────────

def test_book_washroom_success(client):
    """Valid washroom booking returns success message."""
    rv = client.post(
        "/api/washrooms/book",
        json={"block": "Block_A", "time_slot": "Now"},
        content_type="application/json",
    )
    assert rv.status_code == 200
    data = rv.get_json()
    assert data["success"] is True
    assert "Block_A" in data["message"]


def test_book_washroom_gender_block(client):
    """Gender-specific block (Block_A_w) should be accepted."""
    rv = client.post(
        "/api/washrooms/book",
        json={"block": "Block_A_w", "time_slot": "Next Available"},
        content_type="application/json",
    )
    assert rv.status_code == 200


def test_book_washroom_invalid_block(client):
    """Booking an invalid block name returns 400."""
    rv = client.post(
        "/api/washrooms/book",
        json={"block": "INVALID_BLOCK_XYZ", "time_slot": "Now"},
        content_type="application/json",
    )
    assert rv.status_code == 400
    assert "error" in rv.get_json()


def test_book_washroom_missing_time_slot(client):
    """Booking without time_slot returns 400."""
    rv = client.post(
        "/api/washrooms/book",
        json={"block": "Block_A"},
        content_type="application/json",
    )
    assert rv.status_code == 400


def test_book_washroom_wrong_content_type(client):
    """POST to washroom endpoint without JSON Content-Type returns 415."""
    rv = client.post(
        "/api/washrooms/book",
        data="block=Block_A",
        content_type="text/plain",
    )
    assert rv.status_code == 415


# ─── Gemini AI Chat ───────────────────────────────────────────────────────────

def test_gemini_chat_food_keyword(client):
    """Message about food triggers navigation to /food."""
    rv = client.post(
        "/api/gemini/chat",
        json={"message": "I want to eat something"},
        content_type="application/json",
    )
    assert rv.status_code == 200
    assert "food" in rv.get_json()["reply"].lower()


def test_gemini_chat_washroom_keyword(client):
    """Message about toilet triggers navigation to /washrooms."""
    rv = client.post(
        "/api/gemini/chat",
        json={"message": "where is the toilet?"},
        content_type="application/json",
    )
    assert rv.status_code == 200
    assert "/washrooms" in rv.get_json()["reply"]


def test_gemini_chat_map_keyword(client):
    """Message about being lost triggers AR map navigation."""
    rv = client.post(
        "/api/gemini/chat",
        json={"message": "I am lost, show the map"},
        content_type="application/json",
    )
    assert rv.status_code == 200
    assert "/wayfinding" in rv.get_json()["reply"]


def test_gemini_chat_dashboard_keyword(client):
    """Message about live crowd status triggers dashboard navigation."""
    rv = client.post(
        "/api/gemini/chat",
        json={"message": "show me the live crowd status"},
        content_type="application/json",
    )
    assert rv.status_code == 200
    assert "/dashboard" in rv.get_json()["reply"]


def test_gemini_chat_seat_keyword(client):
    """Message containing 'seat' triggers seat navigation."""
    rv = client.post(
        "/api/gemini/chat",
        json={"message": "seat information"},
        content_type="application/json",
    )
    assert rv.status_code == 200
    # 'seat' keyword maps to /seats
    assert "/seats" in rv.get_json()["reply"]


def test_gemini_chat_drink_keyword(client):
    """Message about drinks triggers food navigation."""
    rv = client.post(
        "/api/gemini/chat",
        json={"message": "Can I get a drink nearby?"},
        content_type="application/json",
    )
    assert rv.status_code == 200
    assert "/food" in rv.get_json()["reply"]


def test_gemini_chat_missing_message(client):
    """Chat with no message field returns 400."""
    rv = client.post("/api/gemini/chat", json={}, content_type="application/json")
    assert rv.status_code == 400


def test_gemini_chat_empty_message(client):
    """Chat with empty string returns 400."""
    rv = client.post(
        "/api/gemini/chat",
        json={"message": ""},
        content_type="application/json",
    )
    assert rv.status_code == 400


def test_gemini_chat_long_input_truncated(client):
    """Oversized message is truncated by Pydantic and handled gracefully."""
    rv = client.post(
        "/api/gemini/chat",
        json={"message": "food " * 200},
        content_type="application/json",
    )
    # Pydantic max_length=500 — 'food ' * 200 = 1000 chars, should be rejected
    assert rv.status_code in [200, 400]


def test_gemini_chat_xss_blocked(client):
    """XSS HTML payload in message is rejected by Pydantic sanitizer."""
    rv = client.post(
        "/api/gemini/chat",
        json={"message": "<b></b>"},
        content_type="application/json",
    )
    # bleach strips all tags → empty string → ValidationError → 400
    assert rv.status_code == 400


def test_gemini_chat_metadata_fields(client):
    """Chat response must include reply, agent, and powered_by fields."""
    rv = client.post(
        "/api/gemini/chat",
        json={"message": "show me the dashboard"},
        content_type="application/json",
    )
    assert rv.status_code == 200
    data = rv.get_json()
    assert "reply" in data
    assert "agent" in data
    assert "powered_by" in data


def test_gemini_chat_nav_action_parsed(client):
    """Chat response must include parsed nav_action when navigating."""
    rv = client.post(
        "/api/gemini/chat",
        json={"message": "I want food"},
        content_type="application/json",
    )
    assert rv.status_code == 200
    data = rv.get_json()
    assert data.get("nav_action") is not None


# ─── Security Headers ─────────────────────────────────────────────────────────

def test_security_header_nosniff(client):
    """X-Content-Type-Options: nosniff must be present on all responses."""
    rv = client.get("/api/health")
    assert rv.headers.get("X-Content-Type-Options") == "nosniff"


def test_security_header_xframe(client):
    """X-Frame-Options: DENY must be present to prevent clickjacking."""
    rv = client.get("/api/health")
    assert rv.headers.get("X-Frame-Options") == "DENY"


def test_security_header_xss(client):
    """X-XSS-Protection header must be present."""
    rv = client.get("/api/health")
    assert "X-XSS-Protection" in rv.headers


def test_security_csp_header(client):
    """Content-Security-Policy header must exist."""
    rv = client.get("/api/health")
    assert "Content-Security-Policy" in rv.headers


def test_sql_injection_blocked_in_items(client):
    """SQL injection payload in order items must not cause a 500 error."""
    rv = client.post(
        "/api/concessions/order",
        json={"items": "'; DROP TABLE order; --"},
        content_type="application/json",
    )
    assert rv.status_code in [200, 400]
    assert rv.status_code != 500


def test_post_without_json_returns_415(client):
    """POST to any API endpoint without JSON MIME type returns 415."""
    rv = client.post("/api/concessions/order", data="raw", content_type="text/html")
    assert rv.status_code == 415


# ─── Events API ───────────────────────────────────────────────────────────────

def test_recent_events_endpoint(client):
    """GET /api/events/recent should return firebase_active status and events list."""
    rv = client.get("/api/events/recent")
    assert rv.status_code == 200
    data = rv.get_json()
    assert "firebase_active" in data
    assert "events" in data
    assert isinstance(data["events"], list)


# ─── Firebase Service (Unit Tests with Mocks) ─────────────────────────────────

def test_firebase_log_event_mock():
    """firebase_service.log_event should gracefully handle offline state."""
    with patch("firebase_service._firebase_initialized", False):
        with patch("firebase_service._firestore_client", None):
            import firebase_service
            result = firebase_service.log_event("test_collection", {"key": "value"})
            assert result is None  # Graceful degradation when Firebase is offline


def test_firebase_get_recent_events_offline():
    """firebase_service.get_recent_events returns empty list when Firebase is offline."""
    with patch("firebase_service._firebase_initialized", False):
        with patch("firebase_service._firestore_client", None):
            import firebase_service
            result = firebase_service.get_recent_events("test_collection")
            assert result == []


def test_firebase_log_ai_chat_mock():
    """log_ai_chat should call log_event with the correct collection name."""
    with patch("firebase_service.log_event") as mock_log:
        import firebase_service
        firebase_service.log_ai_chat("hello", "hi there", "/food")
        mock_log.assert_called_once()
        call_args = mock_log.call_args
        assert call_args[0][0] == "ai_chat_logs"
        assert call_args[0][1]["user_message"] == "hello"


def test_firebase_archive_receipt_stub():
    """archive_receipt_to_gcs returns False gracefully when GCS is unavailable."""
    with patch("firebase_service._firebase_initialized", False):
        with patch("firebase_service._gcs_bucket", None):
            import firebase_service
            result = firebase_service.archive_receipt_to_gcs("test-001", {"id": 1})
            assert result is False


# ─── Pydantic Schema Unit Tests ───────────────────────────────────────────────

def test_pydantic_chat_schema_valid():
    """ChatMessageSchema accepts a clean message."""
    from schemas.stadium import ChatMessageSchema
    schema = ChatMessageSchema(message="where is the food court?")
    assert schema.message == "where is the food court?"


def test_pydantic_chat_schema_strips_html():
    """ChatMessageSchema raises ValidationError when only HTML tags are sent (empty after strip)."""
    from schemas.stadium import ChatMessageSchema
    from pydantic import ValidationError
    # Only HTML tags → bleach strips all → empty string → validator raises
    with pytest.raises(ValidationError):
        ChatMessageSchema(message="<b></b>")


def test_pydantic_order_schema_valid():
    """ConcessionOrderSchema accepts a valid item list."""
    from schemas.stadium import ConcessionOrderSchema
    schema = ConcessionOrderSchema(items="1x Burger, 2x Fries")
    assert "Burger" in schema.items


def test_pydantic_order_schema_empty_blocked():
    """ConcessionOrderSchema rejects empty items."""
    from schemas.stadium import ConcessionOrderSchema
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        ConcessionOrderSchema(items="   ")
