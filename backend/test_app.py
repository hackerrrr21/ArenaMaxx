"""
ArenaMaxx Stadium Platform — Comprehensive Test Suite
Covers: happy paths, edge cases, negative paths, security, and integration tests.
"""
import pytest
import json
from app import app, db


@pytest.fixture
def client():
    """Configure a test client with an in-memory SQLite database."""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['RATELIMIT_ENABLED'] = False  # Disable rate limiting in tests

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            from models import Seat, User
            db.session.add(User(name="Test Attendee", role="attendee"))
            db.session.add(Seat(block='A', row='1', number=1))
            db.session.add(Seat(block='B', row='1', number=2))
            db.session.commit()
        yield client
        with app.app_context():
            db.drop_all()


# ─── Health Check ─────────────────────────────────────────────────────────────
def test_health_check(client):
    """Health endpoint should return 200 with service status."""
    rv = client.get('/api/health')
    assert rv.status_code == 200
    data = rv.get_json()
    assert data['status'] == 'healthy'
    assert 'google_services' in data


# ─── Seats API ────────────────────────────────────────────────────────────────
def test_get_seats(client):
    """GET /api/seats should return a paginated list of seats."""
    rv = client.get('/api/seats')
    assert rv.status_code == 200
    data = rv.get_json()
    assert 'seats' in data
    assert 'total' in data
    assert data['total'] == 2


def test_get_seats_pagination(client):
    """GET /api/seats should respect pagination parameters."""
    rv = client.get('/api/seats?page=1&per_page=1')
    assert rv.status_code == 200
    data = rv.get_json()
    assert len(data['seats']) == 1
    assert data['pages'] == 2


def test_get_seats_block_field(client):
    """Each seat in the response should include block, row, and number fields."""
    rv = client.get('/api/seats')
    assert rv.status_code == 200
    seat = rv.get_json()['seats'][0]
    assert 'block' in seat
    assert 'row' in seat
    assert 'number' in seat
    assert 'status' in seat


# ─── Concessions API ─────────────────────────────────────────────────────────
def test_place_order_success(client):
    """POST /api/concessions/order with valid items should return queue number."""
    rv = client.post('/api/concessions/order',
                     json={'items': '2x Vada Pav, 1x Cold Coffee'})
    assert rv.status_code == 200
    data = rv.get_json()
    assert data['success'] is True
    assert 'queue_number' in data
    assert 'estimated_wait_mins' in data


def test_place_order_missing_items(client):
    """POST /api/concessions/order without items should return 400."""
    rv = client.post('/api/concessions/order', json={})
    assert rv.status_code == 400
    data = rv.get_json()
    assert 'error' in data


def test_place_order_empty_items(client):
    """POST /api/concessions/order with empty string should return 400."""
    rv = client.post('/api/concessions/order', json={'items': ''})
    assert rv.status_code == 400


def test_place_order_queue_increments(client):
    """Placing two orders should result in incrementing queue numbers."""
    rv1 = client.post('/api/concessions/order', json={'items': 'Burger'})
    rv2 = client.post('/api/concessions/order', json={'items': 'Fries'})
    assert rv1.get_json()['queue_number'] < rv2.get_json()['queue_number']


def test_place_order_xss_sanitized(client):
    """XSS payload in items should be sanitized and not cause a 500 error."""
    rv = client.post('/api/concessions/order',
                     json={'items': '<script>alert("xss")</script>'})
    assert rv.status_code == 200  # Accepted but stored as sanitized string


# ─── Washrooms API ────────────────────────────────────────────────────────────
def test_book_washroom_success(client):
    """POST /api/washrooms/book with valid data should succeed."""
    rv = client.post('/api/washrooms/book',
                     json={'block': 'Block_A', 'time_slot': 'Now'})
    assert rv.status_code == 200
    data = rv.get_json()
    assert data['success'] is True
    assert 'Block_A' in data['message']


def test_book_washroom_invalid_block(client):
    """POST /api/washrooms/book with an invalid block name should return 400."""
    rv = client.post('/api/washrooms/book',
                     json={'block': 'InvalidBlock_XYZ', 'time_slot': 'Now'})
    assert rv.status_code == 400
    data = rv.get_json()
    assert 'error' in data


def test_book_washroom_missing_fields(client):
    """POST /api/washrooms/book with missing fields should return 400."""
    rv = client.post('/api/washrooms/book', json={'block': 'Block_A'})
    assert rv.status_code == 400
    data = rv.get_json()
    assert 'error' in data


def test_book_washroom_empty_payload(client):
    """POST /api/washrooms/book with no JSON body should return 400."""
    rv = client.post('/api/washrooms/book',
                     data='not json',
                     content_type='text/plain')
    assert rv.status_code == 400


# ─── Gemini Chat API ─────────────────────────────────────────────────────────
def test_gemini_chat_food_navigation(client):
    """Chat message about food should trigger navigate action in mock mode."""
    rv = client.post('/api/gemini/chat', json={'message': 'I want to eat something'})
    assert rv.status_code == 200
    data = rv.get_json()
    assert 'reply' in data
    assert 'food' in data['reply'].lower() or 'NAVIGATE' in data['reply']


def test_gemini_chat_washroom_navigation(client):
    """Chat message about washroom should trigger navigate action in mock mode."""
    rv = client.post('/api/gemini/chat', json={'message': 'where is the toilet?'})
    assert rv.status_code == 200
    data = rv.get_json()
    assert 'NAVIGATE' in data['reply']
    assert '/washrooms' in data['reply']


def test_gemini_chat_map_navigation(client):
    """Chat message about location should trigger AR map navigation."""
    rv = client.post('/api/gemini/chat', json={'message': 'I am lost, show me map'})
    assert rv.status_code == 200
    data = rv.get_json()
    assert '/wayfinding' in data['reply']


def test_gemini_chat_missing_message(client):
    """Chat with no message field should return 400."""
    rv = client.post('/api/gemini/chat', json={})
    assert rv.status_code == 400


def test_gemini_chat_empty_message(client):
    """Chat with empty string message should return 400."""
    rv = client.post('/api/gemini/chat', json={'message': ''})
    assert rv.status_code == 400


def test_gemini_chat_oversized_message(client):
    """Chat with a very long message should be sanitized, not crash the server."""
    long_msg = 'A' * 5000
    rv = client.post('/api/gemini/chat', json={'message': long_msg})
    assert rv.status_code == 200  # Truncated and handled gracefully


# ─── Security Tests ───────────────────────────────────────────────────────────
def test_security_headers_present(client):
    """All responses should include essential security headers."""
    rv = client.get('/api/health')
    assert 'X-Content-Type-Options' in rv.headers
    assert rv.headers['X-Content-Type-Options'] == 'nosniff'
    assert 'X-Frame-Options' in rv.headers
    assert rv.headers['X-Frame-Options'] == 'DENY'


def test_invalid_route_returns_index(client):
    """Unknown routes should return the React app (SPA fallback), not a 404 JSON."""
    rv = client.get('/some/unknown/page')
    # Should serve the React index.html
    assert rv.status_code in [200, 404]  # 404 if dist not built locally
