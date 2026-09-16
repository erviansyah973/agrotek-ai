"""
AGROTEK AI — Hub Route
======================
"""

from flask import Blueprint, render_template, current_app
from app.auth_utils import require_login, current_user, PERMISSIONS

hub_bp = Blueprint("hub", __name__)


MODULES = [
    {"id": "statistik", "title": "Statistik Wilayah", "desc": "Data spasial & statistik Kabupaten Jember.",
     "icon": "📊", "color": "emerald", "endpoint": "main.statistik", "perm": "view_statistik"},
    {"id": "pertanian", "title": "Pertanian", "desc": "Komoditas, produksi, dan kalender tanam.",
     "icon": "🌱", "color": "emerald", "endpoint": "pertanian.index", "perm": "view_statistik"},
    {"id": "irigasi", "title": "Smart Irrigation", "desc": "Jaringan irigasi, bangunan air, dan neraca air.",
     "icon": "💧", "color": "sky", "endpoint": "irigasi.index", "perm": "view_hidrologi"},
    {"id": "hidrologi", "title": "Hidrologi", "desc": "Curah hujan, debit, tinggi muka air, DAS.",
     "icon": "🌊", "color": "cyan", "endpoint": "hidrologi.index", "perm": "view_hidrologi"},
    {"id": "risiko", "title": "Early Warning", "desc": "Risiko banjir & kekeringan real-time.",
     "icon": "⚠️", "color": "red", "endpoint": "risiko.index", "perm": "view_hidrologi"},
    {"id": "ndvi", "title": "NDVI Monitoring", "desc": "Kesehatan vegetasi via Sentinel-2 (remote sensing).",
     "icon": "🛰️", "color": "emerald", "endpoint": "ndvi.index", "perm": "view_statistik"},
    {"id": "lahan", "title": "Kesesuaian Lahan", "desc": "Analisis S1-S3-N per kecamatan (weighted overlay).",
     "icon": "🗺️", "color": "cyan", "endpoint": "lahan.index", "perm": "view_statistik"},
    {"id": "iot", "title": "IoT Monitoring", "desc": "Sensor real-time: water level, hujan, tanah.",
     "icon": "📡", "color": "purple", "endpoint": "iot.index", "perm": "view_hidrologi"},
    {"id": "peta", "title": "Peta GIS", "desc": "Peta interaktif Kabupaten Jember (2D).",
     "icon": "🌐", "color": "cyan", "endpoint": "main.peta", "perm": "view_peta"},
    {"id": "peta3d", "title": "Peta 3D", "desc": "3D WebGIS Google-Earth style + SHP asli.",
     "icon": "🏔️", "color": "cyan", "endpoint": "main.peta3d", "perm": "view_peta"},
    {"id": "ai", "title": "Analisis Sawah Saya", "desc": "Rekomendasi tanaman untuk lokasi Anda.",
     "icon": "🌾", "color": "amber", "endpoint": "ai.index", "perm": "analyze_limited"},
    {"id": "data", "title": "Data Center", "desc": "Katalog & unduh dataset.",
     "icon": "📁", "color": "purple", "endpoint": "main.data_center", "perm": "view_statistik"},
    {"id": "laporan", "title": "Laporan", "desc": "Ekspor laporan analitik.",
     "icon": "📄", "color": "red", "endpoint": "main.laporan", "perm": "view_statistik"},
    {"id": "admin", "title": "Admin Panel", "desc": "Kelola data request, user, dan log sistem.",
     "icon": "🛡️", "color": "red", "endpoint": "admin.index", "perm": "view_admin_panel"},
]


@hub_bp.route("/hub")
@require_login
def index():
    user = current_user()
    role = user.get("role", "umum")
    user_perms = PERMISSIONS.get(role, set())

    if role == "admin":
        allowed_modules = MODULES
    else:
        allowed_modules = [m for m in MODULES if m["perm"] in user_perms]

    return render_template(
        "hub.html",
        app_name=current_app.config["APP_NAME"],
        app_subtitle=current_app.config["APP_SUBTITLE"],
        app_region=current_app.config["APP_REGION"],
        user=user,
        role=role,
        modules=allowed_modules,
    )