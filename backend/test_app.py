import pytest
from app import app, db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            from models import Seat, User
            db.session.add(User(name="Test Attendee", role="attendee"))
            db.session.add(Seat(block='A', row='1', number=1))
            db.session.commit()
        yield client
        with app.app_context():
            db.drop_all()

def test_get_seats(client):
    rv = client.get('/api/seats')
    assert rv.status_code == 200
    assert len(rv.json) == 1
    assert rv.json[0]['block'] == 'A'

def test_place_order(client):
    rv = client.post('/api/concessions/order', json={'items': 'Test Burger'})
    assert rv.status_code == 200
    assert rv.json['success'] == True
    assert 'queue_number' in rv.json

def test_book_washroom(client):
    rv = client.post('/api/washrooms/book', json={'block': 'Block_B', 'time_slot': '12:00'})
    assert rv.status_code == 200
    assert rv.json['success'] == True
