"""
AGROTEK AI — Auth & Authorization (DB-based)
============================================
Login pakai SQLAlchemy model User.
Fallback ke hardcode kalau DB error (untuk dev).
"""

from functools import wraps
from flask import session, redirect, url_for, flash, abort


# ============================================================
# ROLE PERMISSIONS
# ============================================================
PERMISSIONS = {
    "umum": {
        "view_landing",
        "view_statistik",
        "view_hidrologi",
        "view_peta",
        "analyze_limited",
    },
    "mahasiswa": {
        "view_landing",
        "view_statistik",
        "view_hidrologi",
        "view_peta",
        "analyze_medium",
        "download_csv",
    },
    "admin": {
        "view_landing",
        "view_statistik",
        "view_hidrologi",
        "view_peta",
        "analyze_unlimited",
        "download_csv",
        "download_all",
        "manage_data",
        "manage_user",
        "view_admin_panel",
    },
}


# ============================================================
# CORE FUNCTIONS
# ============================================================
def authenticate(username: str, password: str):
    """Cek user dari database. Return dict user atau None."""
    from app.models import User, Log
    from app.extensions import db

    try:
        user = User.query.filter_by(username=username, active=True).first()
        if not user:
            _log_attempt(username, "user tidak ditemukan")
            return None

        if not user.check_password(password):
            _log_attempt(username, "password salah")
            return None

        # Log sukses
        log = Log(level="info", source="auth", message=f"Login sukses: {username}")
        db.session.add(log)
        db.session.commit()

        return {
            "id": user.id,
            "username": user.username,
            "name": user.name,
            "role": user.role,
        }
    except Exception as e:
        print(f"[AGROTEK] Auth error: {e}")
        return None


def _log_attempt(username, reason):
    """Log percobaan login gagal."""
    from app.models import Log
    from app.extensions import db
    try:
        log = Log(level="warn", source="auth", message=f"Login gagal: {username} ({reason})")
        db.session.add(log)
        db.session.commit()
    except Exception:
        pass


def login_user(user: dict):
    session["user"] = user
    session.permanent = False


def logout_user():
    session.pop("user", None)


def current_user():
    return session.get("user")


def is_logged_in() -> bool:
    return "user" in session


def has_permission(permission: str) -> bool:
    user = current_user()
    if not user:
        return False
    role = user.get("role", "umum")
    return permission in PERMISSIONS.get(role, set())


# ============================================================
# DECORATORS
# ============================================================
def require_login(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not is_logged_in():
            flash("Silakan login terlebih dahulu.", "warning")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return wrapper


def require_permission(permission: str):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not is_logged_in():
                flash("Silakan login terlebih dahulu.", "warning")
                return redirect(url_for("auth.login"))
            if not has_permission(permission):
                abort(403)
            return f(*args, **kwargs)
        return wrapper
    return decorator


def require_role(*roles):
    """Cek user punya role tertentu (multiple)."""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            user = current_user()
            if not user or user.get("role") not in roles:
                abort(403)
            return f(*args, **kwargs)
        return wrapper
    return decorator