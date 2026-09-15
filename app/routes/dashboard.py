"""
AGROTEK AI — Dashboard Route (FASE 3)
=====================================
Halaman /dashboard dengan KPI + chart + tabel monitoring.

CATATAN:
Semua data di sini = DEMO (belum dari DB).
Akan diubah ke PostGIS pada fase berikutnya.
"""

from flask import Blueprint, render_template, current_app, jsonify

dashboard_bp = Blueprint("dashboard", __name__)


# ============================================================
# DATA DEMO — nanti dipindah ke service layer
# ============================================================
KPI = [
    {"key": "production",   "label": "Produksi Padi (demo)",      "value": "1.24",
     "unit": "juta ton",    "trend": "+4.2%",  "trend_dir": "up"},
    {"key": "productivity", "label": "Produktivitas Padi (demo)", "value": "6.12",
     "unit": "ton/ha",      "trend": "+1.8%",  "trend_dir": "up"},
    {"key": "irrigated",    "label": "Lahan Teririgasi (demo)",   "value": "64.8",
     "unit": "ribu ha",     "trend": "-0.5%",  "trend_dir": "down"},
    {"key": "risk",         "label": "Kecamatan Waspada (demo)",  "value": "5",
     "unit": "kecamatan",   "trend": "0",      "trend_dir": "flat"},
]

RISK_DATA = [
    {"district": "Tempurejo",   "flood": "Tinggi", "drought": "Sedang", "score": 82},
    {"district": "Wuluhan",     "flood": "Sedang", "drought": "Rendah", "score": 68},
    {"district": "Puger",       "flood": "Sedang", "drought": "Sedang", "score": 65},
    {"district": "Ambulu",      "flood": "Rendah", "drought": "Sedang", "score": 58},
    {"district": "Silo",        "flood": "Rendah", "drought": "Tinggi", "score": 74},
    {"district": "Sumberjambe", "flood": "Rendah", "drought": "Tinggi", "score": 76},
]

MONITORING_TABLE = [
    {"time": "08:00", "sensor": "AWLR Bedadung",    "param": "TMA",        "value": "182 cm",  "status": "normal"},
    {"time": "08:05", "sensor": "AWLR Wuluhan",     "param": "TMA",        "value": "215 cm",  "status": "warning"},
    {"time": "08:10", "sensor": "Weather Jenggawah","param": "Curah Hujan","value": "12 mm",   "status": "normal"},
    {"time": "08:15", "sensor": "Sensor Tanah A1",  "param": "Kelembapan", "value": "38%",     "status": "warning"},
    {"time": "08:20", "sensor": "Debit Bedadung",   "param": "Debit",      "value": "4.8 m³/s", "status": "normal"},
    {"time": "08:25", "sensor": "Early Warning",    "param": "Status",     "value": "Siaga",   "status": "alert"},
]

RAINFALL = {
    "labels": ["Jan","Feb","Mar","Apr","Mei","Jun","Jul","Agu","Sep","Okt","Nov","Des"],
    "data":   [280, 265, 240, 150, 95,  60,  45,  30,  55,  120, 200, 270],
    "unit": "mm",
}

WATER_LEVEL = {
    "labels": [f"{d:02d}" for d in range(1, 31)],
    "data":   [180,182,185,190,188,192,198,205,210,208,
               215,220,218,222,225,228,224,220,215,210,
               208,205,200,198,195,192,190,188,185,182],
    "unit": "cm",
}

DISCHARGE = {
    "labels": [f"{d:02d}" for d in range(1, 31)],
    "data":   [3.8,3.9,4.0,4.2,4.1,4.3,4.5,4.8,5.0,4.9,
               5.2,5.4,5.3,5.5,5.6,5.7,5.5,5.3,5.1,4.9,
               4.8,4.7,4.5,4.4,4.3,4.2,4.1,4.0,3.9,3.8],
    "unit": "m³/s",
}

CROP_PRODUCTION = {
    "labels": ["Padi", "Jagung", "Kedelai", "Cabai", "Tembakau", "Lainnya"],
    "data":   [620, 245, 42, 28, 35, 88],
    "unit": "ribu ton",
}

LAND_USE = {
    "labels": ["Sawah", "Tegalan", "Perkebunan", "Hutan", "Permukiman", "Lainnya"],
    "data":   [96, 58, 82, 145, 42, 25],
    "unit": "ribu ha",
}


# ============================================================
# ROUTES
# ============================================================
@dashboard_bp.route("/dashboard")
def index():
    return render_template(
        "dashboard.html",
        app_name=current_app.config["APP_NAME"],
        app_subtitle=current_app.config["APP_SUBTITLE"],
        app_region=current_app.config["APP_REGION"],
        kpi=KPI,
        risk=RISK_DATA,
        monitoring_table=MONITORING_TABLE,
        is_demo=True,
    )


# ------------------------------------------------------------
# Endpoint JSON untuk chart
# ------------------------------------------------------------
@dashboard_bp.route("/dashboard/data/rainfall")
def data_rainfall():
    return jsonify(RAINFALL)


@dashboard_bp.route("/dashboard/data/water-level")
def data_water_level():
    return jsonify(WATER_LEVEL)


@dashboard_bp.route("/dashboard/data/discharge")
def data_discharge():
    return jsonify(DISCHARGE)


@dashboard_bp.route("/dashboard/data/crops")
def data_crops():
    return jsonify(CROP_PRODUCTION)


@dashboard_bp.route("/dashboard/data/land-use")
def data_land_use():
    return jsonify(LAND_USE)