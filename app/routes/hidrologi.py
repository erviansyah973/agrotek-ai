"""
AGROTEK AI — Modul Hidrologi
=============================
Halaman /hidrologi: stasiun, time-series, DAS, sungai.
Blueprint sendiri supaya modul terpisah dari `main`.
"""

from flask import Blueprint, render_template, current_app, jsonify
from app.auth_utils import require_login, current_user

hidrologi_bp = Blueprint("hidrologi", __name__)


# ============================================================
# STASIUN PEMANTAUAN (DEMO)
# ============================================================
STASIUN = [
    {"code": "AWLR-BDD", "name": "AWLR Bedadung",     "type": "AWLR",  "kecamatan": "Patrang",     "lat": -8.120, "lng": 113.680, "status": "Aktif"},
    {"code": "AWLR-WLH", "name": "AWLR Wuluhan",      "type": "AWLR",  "kecamatan": "Wuluhan",     "lat": -8.270, "lng": 113.580, "status": "Aktif"},
    {"code": "AWLR-TGL", "name": "AWLR Tanggul",      "type": "AWLR",  "kecamatan": "Tanggul",     "lat": -8.100, "lng": 113.450, "status": "Aktif"},
    {"code": "ARR-JGW",  "name": "Pos Hujan Jenggawah","type": "ARR",  "kecamatan": "Jenggawah",   "lat": -8.220, "lng": 113.680, "status": "Aktif"},
    {"code": "ARR-AMB",  "name": "Pos Hujan Ambulu",  "type": "ARR",   "kecamatan": "Ambulu",      "lat": -8.320, "lng": 113.620, "status": "Aktif"},
    {"code": "AWS-SIL",  "name": "AWS Silo",          "type": "AWS",   "kecamatan": "Silo",        "lat": -8.200, "lng": 113.850, "status": "Perlu Perbaikan"},
]

# ============================================================
# SUNGAI (DEMO)
# ============================================================
SUNGAI = [
    {"name": "Kali Bedadung", "class": "Utama",    "panjang_km": 45.2, "kecamatan": "Patrang · Wuluhan"},
    {"name": "Kali Tanggul",  "class": "Sekunder", "panjang_km": 32.8, "kecamatan": "Tanggul · Sumberbaru"},
    {"name": "Kali Mayang",   "class": "Sekunder", "panjang_km": 28.4, "kecamatan": "Mayang · Silo"},
    {"name": "Kali Bondoyudo","class": "Utama",    "panjang_km": 52.6, "kecamatan": "Tempurejo · Ambulu"},
]

# ============================================================
# DAS (DEMO)
# ============================================================
DAS = [
    {"name": "DAS Bedadung",  "luas_km2": 1420.4, "sungai": "Kali Bedadung"},
    {"name": "DAS Bondoyudo", "luas_km2": 1580.2, "sungai": "Kali Bondoyudo"},
    {"name": "DAS Tanggul",   "luas_km2": 680.6,  "sungai": "Kali Tanggul"},
    {"name": "DAS Mayang",    "luas_km2": 520.3,  "sungai": "Kali Mayang"},
]

# ============================================================
# RISIKO BANJIR & KEKERINGAN (DEMO)
# ============================================================
RISIKO_BANJIR = [
    {"district": "Tempurejo",   "level": "Tinggi", "score": 82},
    {"district": "Wuluhan",     "level": "Sedang", "score": 68},
    {"district": "Puger",       "level": "Sedang", "score": 65},
    {"district": "Ambulu",      "level": "Rendah", "score": 58},
    {"district": "Silo",        "level": "Rendah", "score": 74},
    {"district": "Sumberjambe", "level": "Rendah", "score": 76},
]

RISIKO_KERING = [
    {"district": "Silo",        "level": "Tinggi", "score": 74},
    {"district": "Sumberjambe", "level": "Tinggi", "score": 76},
    {"district": "Sukowono",    "level": "Sedang", "score": 55},
    {"district": "Jelbuk",      "level": "Sedang", "score": 52},
    {"district": "Ledokombo",   "level": "Sedang", "score": 60},
    {"district": "Kalisat",     "level": "Rendah", "score": 42},
]

# ============================================================
# TIME-SERIES (DEMO)
# ============================================================
RAINFALL_BULANAN = {
    "labels": ["Jan","Feb","Mar","Apr","Mei","Jun","Jul","Agu","Sep","Okt","Nov","Des"],
    "data":   [280, 265, 240, 150, 95, 60, 45, 30, 55, 120, 200, 270],
    "unit": "mm",
}

TMA_HARIAN = {
    "labels": [f"{d:02d}" for d in range(1, 31)],
    "data":   [180,182,185,190,188,192,198,205,210,208,
               215,220,218,222,225,228,224,220,215,210,
               208,205,200,198,195,192,190,188,185,182],
    "unit": "cm",
}

DEBIT_HARIAN = {
    "labels": [f"{d:02d}" for d in range(1, 31)],
    "data":   [3.8,3.9,4.0,4.2,4.1,4.3,4.5,4.8,5.0,4.9,
               5.2,5.4,5.3,5.5,5.6,5.7,5.5,5.3,5.1,4.9,
               4.8,4.7,4.5,4.4,4.3,4.2,4.1,4.0,3.9,3.8],
    "unit": "m³/s",
}

MONITORING_TABLE = [
    {"time": "08:00", "sensor": "AWLR Bedadung",     "param": "TMA",         "value": "182 cm",   "status": "normal"},
    {"time": "08:05", "sensor": "AWLR Wuluhan",      "param": "TMA",         "value": "215 cm",   "status": "warning"},
    {"time": "08:10", "sensor": "Weather Jenggawah", "param": "Curah Hujan", "value": "12 mm",    "status": "normal"},
    {"time": "08:15", "sensor": "Sensor Tanah A1",   "param": "Kelembapan",  "value": "38%",      "status": "warning"},
    {"time": "08:20", "sensor": "Debit Bedadung",    "param": "Debit",       "value": "4.8 m³/s", "status": "normal"},
    {"time": "08:25", "sensor": "Early Warning",     "param": "Status",      "value": "Siaga",    "status": "alert"},
]

# KPI
KPI = {
    "total_stasiun":  len(STASIUN),
    "total_sungai":   len(SUNGAI),
    "total_das":      len(DAS),
    "total_das_luas": sum(d["luas_km2"] for d in DAS),
}


# ============================================================
# ROUTES
# ============================================================
@hidrologi_bp.route("/hidrologi")
@require_login
def index():
    return render_template(
        "hidrologi.html",
        app_name=current_app.config["APP_NAME"],
        app_subtitle=current_app.config["APP_SUBTITLE"],
        app_region=current_app.config["APP_REGION"],
        user=current_user(),
        stasiun=STASIUN,
        sungai=SUNGAI,
        das=DAS,
        risiko_banjir=RISIKO_BANJIR,
        risiko_kering=RISIKO_KERING,
        monitoring_table=MONITORING_TABLE,
        kpi=KPI,
    )


@hidrologi_bp.route("/hidrologi/data/rainfall")
def data_rainfall():
    return jsonify(RAINFALL_BULANAN)


@hidrologi_bp.route("/hidrologi/data/tma")
def data_tma():
    return jsonify(TMA_HARIAN)


@hidrologi_bp.route("/hidrologi/data/debit")
def data_debit():
    return jsonify(DEBIT_HARIAN)


@hidrologi_bp.route("/hidrologi/data/summary")
def data_summary():
    return jsonify({
        "rainfall_avg":  round(sum(RAINFALL_BULANAN["data"]) / 12, 1),
        "tma_avg":       round(sum(TMA_HARIAN["data"]) / 30, 1),
        "debit_avg":     round(sum(DEBIT_HARIAN["data"]) / 30, 2),
        "stasiun_aktif": sum(1 for s in STASIUN if s["status"] == "Aktif"),
    })