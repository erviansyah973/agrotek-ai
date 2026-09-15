"""
AGROTEK AI — Modul Pertanian
=============================
Halaman /pertanian: komoditas, produksi, kalender tanam.
Data DEMO — akan diganti data SID + BPS di fase berikutnya.
"""

from flask import Blueprint, render_template, current_app, jsonify
from app.auth_utils import require_login, current_user

pertanian_bp = Blueprint("pertanian", __name__)


# ============================================================
# DATA DEMO — komoditas utama Jember
# ============================================================
KOMODITAS = [
    {
        "code": "PDI", "name": "Padi", "category": "Pangan",
        "luas_tanam": 96.4, "luas_panen": 95.2, "produksi": 582.7,
        "produktivitas": 6.12, "warna": "emerald",
    },
    {
        "code": "JAG", "name": "Jagung", "category": "Pangan",
        "luas_tanam": 52.1, "luas_panen": 51.3, "produksi": 245.6,
        "produktivitas": 4.79, "warna": "sky",
    },
    {
        "code": "KED", "name": "Kedelai", "category": "Pangan",
        "luas_tanam": 18.7, "luas_panen": 18.2, "produksi": 25.8,
        "produktivitas": 1.42, "warna": "cyan",
    },
    {
        "code": "CBI", "name": "Cabai", "category": "Hortikultura",
        "luas_tanam": 3.4, "luas_panen": 3.2, "produksi": 28.4,
        "produktivitas": 8.87, "warna": "amber",
    },
    {
        "code": "TMK", "name": "Tembakau", "category": "Perkebunan",
        "luas_tanam": 12.8, "luas_panen": 12.5, "produksi": 34.9,
        "produktivitas": 2.79, "warna": "purple",
    },
    {
        "code": "KOP", "name": "Kopi", "category": "Perkebunan",
        "luas_tanam": 8.2, "luas_panen": 7.9, "produksi": 4.2,
        "produktivitas": 0.53, "warna": "red",
    },
]

# Total KPI
KPI = {
    "total_produksi": sum(k["produksi"] for k in KOMODITAS),
    "total_luas_tanam": sum(k["luas_tanam"] for k in KOMODITAS),
    "total_luas_panen": sum(k["luas_panen"] for k in KOMODITAS),
    "komoditas_count": len(KOMODITAS),
}

# Kalender tanam (bulan 1-12)
KALENDER = [
    {
        "komoditas": "Padi",
        "musim": "MT1 (Nov - Feb)",
        "bulan_mulai": 11, "bulan_akhir": 2,
        "catatan": "Musim hujan utama",
    },
    {
        "komoditas": "Padi",
        "musim": "MT2 (Mar - Jun)",
        "bulan_mulai": 3, "bulan_akhir": 6,
        "catatan": "Musim hujan kedua",
    },
    {
        "komoditas": "Jagung",
        "musim": "MT1 (Nov - Feb)",
        "bulan_mulai": 11, "bulan_akhir": 2,
        "catatan": "Lahan kering",
    },
    {
        "komoditas": "Jagung",
        "musim": "MT2 (Mar - Jun)",
        "bulan_mulai": 3, "bulan_akhir": 6,
        "catatan": "Setelah padi",
    },
    {
        "komoditas": "Kedelai",
        "musim": "MT2 (Mar - Jun)",
        "bulan_mulai": 3, "bulan_akhir": 6,
        "catatan": "Rotasi padi-kedelai",
    },
    {
        "komoditas": "Tembakau",
        "musim": "MT2 (Apr - Sep)",
        "bulan_mulai": 4, "bulan_akhir": 9,
        "catatan": "Musim kemarau",
    },
    {
        "komoditas": "Cabai",
        "musim": "Sepanjang tahun",
        "bulan_mulai": 1, "bulan_akhir": 12,
        "catatan": "Dengan irigasi",
    },
    {
        "komoditas": "Kopi",
        "musim": "Tahunan",
        "bulan_mulai": 1, "bulan_akhir": 12,
        "catatan": "Tanaman tahunan",
    },
]


# ============================================================
# ROUTES
# ============================================================
@pertanian_bp.route("/pertanian")
@require_login
def index():
    return render_template(
        "pertanian.html",
        app_name=current_app.config["APP_NAME"],
        app_subtitle=current_app.config["APP_SUBTITLE"],
        app_region=current_app.config["APP_REGION"],
        user=current_user(),
        komoditas=KOMODITAS,
        kpi=KPI,
        kalender=KALENDER,
    )


@pertanian_bp.route("/pertanian/data/production")
def data_production():
    """Endpoint JSON untuk chart produksi."""
    return jsonify({
        "labels": [k["name"] for k in KOMODITAS],
        "data":   [k["produksi"] for k in KOMODITAS],
        "unit":   "ribu ton",
    })


@pertanian_bp.route("/pertanian/data/category")
def data_category():
    """Endpoint JSON untuk doughnut kategori."""
    kategori = {}
    for k in KOMODITAS:
        kategori[k["category"]] = kategori.get(k["category"], 0) + k["produksi"]
    return jsonify({
        "labels": list(kategori.keys()),
        "data":   list(kategori.values()),
        "unit":   "ribu ton",
    })