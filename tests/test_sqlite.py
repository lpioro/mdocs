from app import create_app, db
from app.models import Client

def test_sqlite_persistence(tmp_path):
    uri = "sqlite:///" + str(tmp_path / "data.sqlite")
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": uri, "WTF_CSRF_ENABLED": False})
    with app.app_context():
        db.create_all()
        db.session.add(Client(name="ARM64 demo"))
        db.session.commit()
        db.session.remove()
    app2 = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": uri, "WTF_CSRF_ENABLED": False})
    with app2.app_context():
        assert db.session.query(Client).count() == 1
