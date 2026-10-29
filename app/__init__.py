import os
from flask import Flask, redirect, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.getenv("SECRET_KEY", "development-change-me"),
        SQLALCHEMY_DATABASE_URI=os.getenv("DATABASE_URL", "sqlite:///:memory:"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=os.getenv("COOKIE_SECURE", "0") == "1",
    )
    if test_config:
        app.config.update(test_config)
    if os.getenv("APP_ENV") == "production" and app.config["SECRET_KEY"] == "development-change-me":
        raise RuntimeError("Production requires SECRET_KEY")
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    login_manager.login_view = "main.login"

    from .models import User
    @login_manager.user_loader
    def load_user(uid):
        try:
            return db.session.get(User, int(uid))
        except (ValueError, TypeError):
            return None

    from .routes import bp
    app.register_blueprint(bp)

    @app.before_request
    def require_login():
        if request.endpoint in ("main.login", "main.health", "static") or request.endpoint is None:
            return
        if not current_user.is_authenticated:
            return redirect(url_for("main.login", next=request.path))

    @app.cli.command("init-db")
    def init_db():
        db.create_all()
        print("Tables initialized")

    @app.cli.command("create-admin")
    def create_admin():
        from werkzeug.security import generate_password_hash
        username = os.getenv("ADMIN_USERNAME", "").strip()
        password = os.getenv("ADMIN_PASSWORD", "")
        if not username or len(password) < 12:
            raise RuntimeError("Set ADMIN_USERNAME and ADMIN_PASSWORD (min 12 characters)")
        if db.session.execute(db.select(User).filter_by(username=username)).scalar_one_or_none():
            raise RuntimeError("Admin exists")
        db.session.add(User(username=username, password_hash=generate_password_hash(password)))
        db.session.commit()
        print("Administrator created")
    return app
