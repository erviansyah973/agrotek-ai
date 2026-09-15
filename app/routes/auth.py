"""
AGROTEK AI — Auth Routes (Login / Logout)
=========================================
- GET  /login  → tampil form
- POST /login  → proses login
- GET  /logout → keluar
"""

from flask import (
    Blueprint, render_template, request,
    redirect, url_for, flash, current_app,
)
from app.auth_utils import authenticate, login_user, logout_user, current_user

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    # Kalau sudah login → langsung ke hub
    if current_user():
        return redirect(url_for("hub.index"))

    error = None

    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = (request.form.get("password") or "").strip()

        if not username or not password:
            error = "Username dan password wajib diisi."
        else:
            user = authenticate(username, password)
            if user:
                login_user(user)
                next_url = request.args.get("next") or url_for("hub.index")
                return redirect(next_url)
            else:
                error = "Username atau password salah."

    return render_template(
        "login.html",
        app_name=current_app.config["APP_NAME"],
        app_subtitle=current_app.config["APP_SUBTITLE"],
        error=error,
    )


@auth_bp.route("/logout")
def logout():
    logout_user()
    flash("Anda telah keluar.", "info")
    return redirect(url_for("main.landing"))