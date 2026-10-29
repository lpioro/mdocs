from app import create_app, db
from app.models import Client
import pytest

@pytest.fixture
def client():
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:", "WTF_CSRF_ENABLED": False})
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()

def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json == {"status":"ok"}

def test_login_required(client):
    assert client.get("/").status_code == 302

def test_client_model(client):
    from flask import current_app
    app = client.application
    with app.app_context():
        db.session.add(Client(name="Test"))
        db.session.commit()
        assert db.session.query(Client).count() == 1
