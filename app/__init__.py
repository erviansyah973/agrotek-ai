"""
AGROTEK AI — Application Factory
=================================
Registrasi blueprint + init DB + error handler.
"""

import os
from flask import Flask, render_template
from config import config
from app.extensions import db


def create_app(config_name="default"):
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static",
    )
    app.config.from_object(config[config_name])

    # ---------- Database: SQLite ----------
    # Gunakan /data kalau tersedia (untuk Railway), fallback ke root (untuk lokal)
    if os.path.exists("/data") or os.path.exists("/app/data"):
        base_dir = "/data"
    else:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(base_dir, 'agrotek.db')}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    # ---------- Blueprints ----------
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.hub import hub_bp
    from app.routes.admin import admin_bp
    from app.routes.pertanian import pertanian_bp
    from app.routes.irigasi import irigasi_bp
    from app.routes.hidrologi import hidrologi_bp
    from app.routes.ai import ai_bp
    from app.routes.risiko import risiko_bp
    from app.routes.iot import iot_bp
    from app.routes.lahan import lahan_bp
    from app.routes.ndvi import ndvi_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(hub_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(pertanian_bp)
    app.register_blueprint(irigasi_bp)
    app.register_blueprint(hidrologi_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(risiko_bp)
    app.register_blueprint(iot_bp)
    app.register_blueprint(lahan_bp)
    app.register_blueprint(ndvi_bp)

    # ---------- Error Handlers ----------
    @app.errorhandler(404)
    def not_found(e):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template("500.html"), 500

    @app.errorhandler(403)
    def forbidden(e):
        return render_template("404.html"), 403

    # ---------- Init DB + Seed ----------
    with app.app_context():
        from app.models import User, DataRequest, Log
        db.create_all()
        _seed_users()

    return app


def _seed_users():
    """Buat user default kalau belum ada."""
    from app.models import User

    default_users = [
        {"username": "admin",     "password": "admin123", "name": "Administrator",  "role": "admin",     "email": "admin@agrotek.local"},
        {"username": "mahasiswa", "password": "mhs123",   "name": "Mahasiswa",      "role": "mahasiswa", "email": "mhs@agrotek.local"},
        {"username": "umum",      "password": "umum123",  "name": "Pengguna Umum",  "role": "umum",      "email": "umum@agrotek.local"},
    ]

    for u in default_users:
        existing = User.query.filter_by(username=u["username"]).first()
        if not existing:
            user = User(
                username=u["username"],
                name=u["name"],
                email=u["email"],
                role=u["role"],
            )
            user.set_password(u["password"])
            db.session.add(user)

    db.session.commit()