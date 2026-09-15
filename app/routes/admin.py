"""
AGROTEK AI — Admin Panel Routes (Enhanced)
==========================================
Manage data request, user, log, dan statistik platform.
"""

from flask import (
    Blueprint, render_template, current_app,
    redirect, url_for, request, flash, jsonify,
)
from app.auth_utils import require_role, current_user
from app.extensions import db

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


# ============================================================
# DASHBOARD
# ============================================================
@admin_bp.route("/")
@require_role("admin")
def index():
    from app.models import DataRequest, Log, User

    # ---- Stats ----
    stats = {
        "requests":       DataRequest.query.count(),
        "pending":        DataRequest.query.filter_by(status="pending").count(),
        "approved":       DataRequest.query.filter_by(status="approved").count(),
        "rejected":       DataRequest.query.filter_by(status="rejected").count(),
        "users":          User.query.count(),
        "users_active":   User.query.filter_by(active=True).count(),
        "logs":           Log.query.count(),
    }

    # ---- Data ----
    requests = DataRequest.query.order_by(DataRequest.created_at.desc()).limit(20).all()
    logs = Log.query.order_by(Log.created_at.desc()).limit(30).all()
    users = User.query.order_by(User.created_at.desc()).all()

    # ---- Stats breakdown user by role ----
    role_stats = {}
    for u in users:
        role_stats[u.role] = role_stats.get(u.role, 0) + 1

    # ---- Stats request by status ----
    status_stats = {
        "pending":   stats["pending"],
        "approved":  stats["approved"],
        "rejected":  stats["rejected"],
        "delivered": DataRequest.query.filter_by(status="delivered").count(),
    }

    return render_template(
        "admin.html",
        app_name=current_app.config["APP_NAME"],
        app_subtitle=current_app.config["APP_SUBTITLE"],
        user=current_user(),
        stats=stats,
        requests=[r.to_dict() for r in requests],
        logs=[l.to_dict() for l in logs],
        users=[u.to_dict() for u in users],
        role_stats=role_stats,
        status_stats=status_stats,
    )


# ============================================================
# DATA REQUEST MANAGEMENT
# ============================================================
@admin_bp.route("/request/<int:req_id>/<action>", methods=["POST"])
@require_role("admin")
def update_request(req_id, action):
    from app.models import DataRequest, Log

    if action not in ("approved", "rejected", "delivered", "pending"):
        flash("Aksi tidak valid.", "error")
        return redirect(url_for("admin.index"))

    req = DataRequest.query.get(req_id)
    if not req:
        flash("Request tidak ditemukan.", "error")
        return redirect(url_for("admin.index"))

    old_status = req.status
    req.status = action

    db.session.add(Log(
        level="info",
        source="admin",
        message=f"Request #{req_id} status: {old_status} → {action}",
    ))
    db.session.commit()

    flash(f"Request #{req_id} diubah menjadi {action}.", "success")
    return redirect(url_for("admin.index"))


# ============================================================
# USER MANAGEMENT
# ============================================================
@admin_bp.route("/user/<int:user_id>/toggle", methods=["POST"])
@require_role("admin")
def toggle_user(user_id):
    from app.models import User, Log

    u = User.query.get(user_id)
    if not u:
        flash("User tidak ditemukan.", "error")
        return redirect(url_for("admin.index"))

    # Proteksi: tidak bisa nonaktifkan diri sendiri
    me = current_user()
    if me and me.get("id") == user_id:
        flash("Anda tidak bisa menonaktifkan akun sendiri.", "error")
        return redirect(url_for("admin.index"))

    u.active = not u.active

    db.session.add(Log(
        level="info",
        source="admin",
        message=f"User '{u.username}' diubah status → {'aktif' if u.active else 'nonaktif'}",
    ))
    db.session.commit()

    flash(f"User '{u.username}' sekarang {'aktif' if u.active else 'nonaktif'}.", "success")
    return redirect(url_for("admin.index"))


@admin_bp.route("/user/<int:user_id>/role", methods=["POST"])
@require_role("admin")
def update_user_role(user_id):
    from app.models import User, Log

    new_role = (request.form.get("role") or "").strip()
    if new_role not in ("umum", "mahasiswa", "admin"):
        flash("Role tidak valid.", "error")
        return redirect(url_for("admin.index"))

    u = User.query.get(user_id)
    if not u:
        flash("User tidak ditemukan.", "error")
        return redirect(url_for("admin.index"))

    # Proteksi: tidak bisa ubah role sendiri
    me = current_user()
    if me and me.get("id") == user_id:
        flash("Anda tidak bisa mengubah role akun sendiri.", "error")
        return redirect(url_for("admin.index"))

    old_role = u.role
    u.role = new_role

    db.session.add(Log(
        level="info",
        source="admin",
        message=f"User '{u.username}' role: {old_role} → {new_role}",
    ))
    db.session.commit()

    flash(f"Role user '{u.username}' diubah ke {new_role}.", "success")
    return redirect(url_for("admin.index"))


# ============================================================
# API: system stats (JSON)
# ============================================================
@admin_bp.route("/api/stats")
@require_role("admin")
def api_stats():
    from app.models import DataRequest, Log, User

    return jsonify({
        "ok": True,
        "users": {
            "total": User.query.count(),
            "active": User.query.filter_by(active=True).count(),
            "by_role": {
                "admin": User.query.filter_by(role="admin").count(),
                "mahasiswa": User.query.filter_by(role="mahasiswa").count(),
                "umum": User.query.filter_by(role="umum").count(),
            },
        },
        "requests": {
            "total": DataRequest.query.count(),
            "pending": DataRequest.query.filter_by(status="pending").count(),
            "approved": DataRequest.query.filter_by(status="approved").count(),
            "rejected": DataRequest.query.filter_by(status="rejected").count(),
            "delivered": DataRequest.query.filter_by(status="delivered").count(),
        },
        "logs": {
            "total": Log.query.count(),
        },
    })