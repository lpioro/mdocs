from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, jsonify
from flask_login import login_user, logout_user
from werkzeug.security import check_password_hash
from sqlalchemy import func
from . import db
from .models import User, Client, Sender, EmailMessage, Document, Reminder

bp = Blueprint("main", __name__)

@bp.get("/health")
def health():
    return jsonify(status="ok")

@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = db.session.execute(db.select(User).filter_by(username=request.form.get("username", ""))).scalar_one_or_none()
        if user and check_password_hash(user.password_hash, request.form.get("password", "")):
            login_user(user)
            return redirect(url_for("main.dashboard"))
        flash("Nieprawidłowe dane logowania", "danger")
    return render_template("login.html")

@bp.post("/logout")
def logout():
    logout_user()
    return redirect(url_for("main.login"))

@bp.get("/")
def dashboard():
    clients = db.session.execute(db.select(Client).order_by(Client.name)).scalars().all()
    emails = db.session.execute(db.select(EmailMessage).order_by(EmailMessage.id.desc()).limit(10)).scalars().all()
    unknown = db.session.scalar(db.select(func.count()).select_from(EmailMessage).where(EmailMessage.client_id.is_(None)))
    document_count = db.session.scalar(db.select(func.count()).select_from(Document))
    return render_template("dashboard.html", clients=clients, emails=emails, unknown=unknown, document_count=document_count)

@bp.route("/clients", methods=["GET","POST"])
def clients():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            abort(400)
        db.session.add(Client(name=name, nip=request.form.get("nip") or None, email=request.form.get("email") or None))
        db.session.commit()
        return redirect(url_for("main.clients"))
    clients = db.session.execute(db.select(Client).order_by(Client.name)).scalars().all()
    return render_template("clients.html", clients=clients)

@bp.get("/clients/<int:client_id>")
def client(client_id):
    item = db.get_or_404(Client, client_id)
    docs = db.session.execute(db.select(Document).where(Document.client_id == item.id).order_by(Document.id.desc())).scalars().all()
    return render_template("client.html", client=item, docs=docs)

@bp.post("/clients/<int:client_id>/documents")
def add_document(client_id):
    db.get_or_404(Client, client_id)
    period = request.form.get("period", "")
    try:
        datetime.strptime(period, "%Y-%m")
    except ValueError:
        abort(400)
    name = request.form.get("name", "").strip()
    if not name:
        abort(400)
    db.session.add(Document(client_id=client_id, name=name, period=period, kind=request.form.get("kind", "Inny")))
    db.session.commit()
    return redirect(url_for("main.client", client_id=client_id))

@bp.post("/clients/<int:client_id>/senders")
def add_sender(client_id):
    db.get_or_404(Client, client_id)
    email = request.form.get("email", "").strip().lower()
    if "@" not in email:
        abort(400)
    sender = db.session.execute(db.select(Sender).filter_by(email=email)).scalar_one_or_none()
    if sender and sender.client_id != client_id:
        flash("Adres jest przypisany do innego klienta", "danger")
    elif not sender:
        db.session.add(Sender(email=email, client_id=client_id))
        db.session.commit()
    return redirect(url_for("main.client", client_id=client_id))

@bp.post("/emails")
def add_email():
    email = request.form.get("sender", "").strip().lower()
    subject = request.form.get("subject", "").strip()
    if "@" not in email or not subject:
        abort(400)
    sender = db.session.execute(db.select(Sender).filter_by(email=email)).scalar_one_or_none()
    db.session.add(EmailMessage(sender=email, subject=subject, client_id=sender.client_id if sender else None))
    db.session.commit()
    return redirect(url_for("main.dashboard"))

@bp.post("/clients/<int:client_id>/reminders")
def add_reminder(client_id):
    c = db.get_or_404(Client, client_id)
    period = request.form.get("period", "").strip()
    try:
        datetime.strptime(period, "%Y-%m")
    except ValueError:
        abort(400)
    msg = f"Dzień dobry, prosimy o przekazanie dokumentów za okres {period}."
    db.session.add(Reminder(client_id=c.id, period=period, message=msg))
    db.session.commit()
    flash("Utworzono szkic przypomnienia (bez wysyłki)", "success")
    return redirect(url_for("main.client", client_id=client_id))
