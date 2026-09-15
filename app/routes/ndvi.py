"""
AGROTEK AI — Sentinel-2 NDVI Monitoring
========================================
Halaman /ndvi: monitoring kesehatan vegetasi via NDVI time-series.
Arsitektur siap menerima citra Sentinel-2 real.

NDVI = (NIR - Red) / (NIR + Red)
Range: -1.0 s/d +1.0
Interpretasi:
  < 0.2   : Non-vegetasi (air, awan, tanah terbuka)
  0.2-0.4 : Vegetasi jarang
  0.4-0.6 : Vegetasi sedang
  0.6-0.8 : Vegetasi lebat
  > 0.8   : Vegetasi sangat lebat
"""

from flask import Blueprint, render_template, current_app, jsonify
from app.auth_utils import require_login, current_user

ndvi_bp = Blueprint("ndvi", __name__)


# ============================================================
# TIME-SERIES NDVI (DEMO — per bulan, rata-rata Kab. Jember)
# ============================================================
NDVI_MONTHLY = {
    "labels": ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun",
               "Jul", "Agu", "Sep", "Okt", "Nov", "Des"],
    "data":   [0.72, 0.78, 0.75, 0.68, 0.55, 0.42,
               0.35, 0.38, 0.45, 0.58, 0.68, 0.74],
    "unit": "NDVI",
}

# ============================================================
# NDVI PER KECAMATAN (DEMO — 10 kecamatan contoh)
# ============================================================
NDVI_BY_DISTRICT = [
    {"district": "Wuluhan",     "ndvi": 0.78, "kategori": "Lebat",       "trend": "up",   "luas_vegetasi_ha": 8240},
    {"district": "Patrang",     "ndvi": 0.74, "kategori": "Lebat",       "trend": "up",   "luas_vegetasi_ha": 6180},
    {"district": "Ambulu",      "ndvi": 0.72, "kategori": "Lebat",       "trend": "flat", "luas_vegetasi_ha": 7260},
    {"district": "Jenggawah",   "ndvi": 0.68, "kategori": "Lebat",       "trend": "up",   "luas_vegetasi_ha": 4380},
    {"district": "Rambipuji",   "ndvi": 0.62, "kategori": "Sedang",      "trend": "down", "luas_vegetasi_ha": 5120},
    {"district": "Bangsalsari", "ndvi": 0.58, "kategori": "Sedang",      "trend": "flat", "luas_vegetasi_ha": 6840},
    {"district": "Puger",       "ndvi": 0.52, "kategori": "Sedang",      "trend": "down", "luas_vegetasi_ha": 3260},
    {"district": "Balung",      "ndvi": 0.45, "kategori": "Sedang",      "trend": "down", "luas_vegetasi_ha": 2840},
    {"district": "Silo",        "ndvi": 0.38, "kategori": "Jarang",      "trend": "down", "luas_vegetasi_ha": 1200},
    {"district": "Sumberjambe", "ndvi": 0.32, "kategori": "Jarang",      "trend": "down", "luas_vegetasi_ha": 800},
]

# Kategori warna NDVI
KATEGORI = [
    {"range": "< 0.2",    "label": "Non-Vegetasi",      "warna": "#dc2626"},
    {"range": "0.2-0.4",  "label": "Vegetasi Jarang",   "warna": "#f59e0b"},
    {"range": "0.4-0.6",  "label": "Vegetasi Sedang",   "warna": "#eab308"},
    {"range": "0.6-0.8",  "label": "Vegetasi Lebat",    "warna": "#10b981"},
    {"range": "> 0.8",    "label": "Vegetasi Sangat Lebat","warna": "#059669"},
]

# Info satellite
SATELLITE = {
    "name": "Sentinel-2",
    "operator": "ESA Copernicus",
    "resolusi": "10 m / pixel",
    "revisit": "5 hari",
    "band_ndvi": "Band 4 (Red) + Band 8 (NIR)",
    "lisensi": "CC-BY-SA 3.0 IGO (Gratis)",
    "terakhir_scan": "15 September 2026",
    "cloud_cover": "8%",
}


# ============================================================
# ROUTES
# ============================================================
@ndvi_bp.route("/ndvi")
@require_login
def index():
    # Statistik ringkas
    ndvi_avg = sum(NDVI_MONTHLY["data"]) / len(NDVI_MONTHLY["data"])
    ndvi_max = max(NDVI_MONTHLY["data"])
    ndvi_min = min(NDVI_MONTHLY["data"])

    stats = {
        "ndvi_avg": round(ndvi_avg, 3),
        "ndvi_max": ndvi_max,
        "ndvi_min": ndvi_min,
        "total_district": len(NDVI_BY_DISTRICT),
        "vegetasi_lebat": sum(1 for d in NDVI_BY_DISTRICT if d["kategori"] == "Lebat"),
        "vegetasi_jarang": sum(1 for d in NDVI_BY_DISTRICT if d["kategori"] == "Jarang"),
    }

    return render_template(
        "ndvi.html",
        app_name=current_app.config["APP_NAME"],
        app_subtitle=current_app.config["APP_SUBTITLE"],
        app_region=current_app.config["APP_REGION"],
        user=current_user(),
        ndvi_monthly=NDVI_MONTHLY,
        ndvi_districts=NDVI_BY_DISTRICT,
        kategori=KATEGORI,
        satellite=SATELLITE,
        stats=stats,
    )


@ndvi_bp.route("/ndvi/data/timeseries")
def data_timeseries():
    """Endpoint JSON: time-series NDVI."""
    return jsonify(NDVI_MONTHLY)


@ndvi_bp.route("/ndvi/data/districts")
def data_districts():
    """Endpoint JSON: NDVI per kecamatan (untuk chart bar)."""
    return jsonify({
        "labels": [d["district"] for d in NDVI_BY_DISTRICT],
        "data":   [d["ndvi"] for d in NDVI_BY_DISTRICT],
        "kategori": [d["kategori"] for d in NDVI_BY_DISTRICT],
        "unit": "NDVI",
    })


@ndvi_bp.route("/ndvi/data/satellite")
def data_satellite():
    """Endpoint JSON: info satellite."""
    return jsonify(SATELLITE)


@ndvi_bp.route("/ndvi/data/stats")
def data_stats():
    """Endpoint JSON: statistik ringkas."""
    ndvi_avg = sum(NDVI_MONTHLY["data"]) / len(NDVI_MONTHLY["data"])
    return jsonify({
        "ndvi_avg": round(ndvi_avg, 3),
        "ndvi_max": max(NDVI_MONTHLY["data"]),
        "ndvi_min": min(NDVI_MONTHLY["data"]),
        "satellite": SATELLITE["name"],
    })