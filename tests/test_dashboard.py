from app import create_app, db
from app.models import User, Client, Document, EmailMessage
from werkzeug.security import generate_password_hash

def test_dashboard_statuses():
    app = create_app({
        "TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
    })
    with app.app_context():
        db.create_all()
        db.session.add(User(username="admin", password_hash=generate_password_hash("temporary-password")))
        db.session.add(Client(name="Alpha"))
        db.session.add(Client(name="Beta"))
        db.session.commit()
        alpha = db.session.execute(db.select(Client).where(Client.name == "Alpha")).scalar_one()
        db.session.add(Document(client_id=alpha.id, name="Faktura nr 1", period="2026-10", kind="Faktura"))
        db.session.add(EmailMessage(sender="unknown@example.com", subject="Dokumenty"))
        db.session.commit()
    c = app.test_client()
    assert c.post("/login", data={"username": "admin", "password": "temporary-password"}).status_code == 302
    res = c.get("/?period=2026-10")
    assert res.status_code == 200
    for txt in (b"Alpha", b"Beta", b"2026-10", b"unknown@example.com", b"Faktura nr 1"):
        assert txt in res.data
    assert c.get("/?period=garbage").status_code == 400
