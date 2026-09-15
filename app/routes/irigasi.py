"""
AGROTEK AI — Modul Irigasi (Smart Irrigation)
==============================================
Halaman /irigasi: jaringan irigasi, neraca air, daerah irigasi.
Data DEMO — akan diganti dengan hasil SID 3 kabupaten.
"""

from flask import Blueprint, render_template, current_app, jsonify
from app.auth_utils import require_login, current_user

irigasi_bp = Blueprint("irigasi", __name__)


# ============================================================
# BANGUNAN IRIGASI (DEMO)
# ============================================================
BANGUNAN = [
    {"id": 1, "name": "Bendung Bedadung",       "type": "Bendung",      "kecamatan": "Patrang",     "kapasitas_m3s": 12.4, "tahun": 2015, "status": "Aktif"},
    {"id": 2, "name": "Bendung Wuluhan",        "type": "Bendung",      "kecamatan": "Wuluhan",     "kapasitas_m3s": 8.6,  "tahun": 2018, "status": "Aktif"},
    {"id": 3, "name": "Pintu Air Bedadung 01",  "type": "Pintu Air",    "kecamatan": "Patrang",     "kapasitas_m3s": 4.2,  "tahun": 2015, "status": "Aktif"},
    {"id": 4, "name": "Pintu Air Wuluhan 02",   "type": "Pintu Air",    "kecamatan": "Wuluhan",     "kapasitas_m3s": 3.8,  "tahun": 2018, "status": "Aktif"},
    {"id": 5, "name": "Pompa Ambulu",           "type": "Pompa",        "kecamatan": "Ambulu",      "kapasitas_m3s": 2.4,  "tahun": 2020, "status": "Aktif"},
    {"id": 6, "name": "Pintu Air Rambipuji 01", "type": "Pintu Air",    "kecamatan": "Rambipuji",   "kapasitas_m3s": 3.2,  "tahun": 2019, "status": "Perlu Perbaikan"},
]

# ============================================================
# JARINGAN SALURAN (DEMO)
# ============================================================
SALURAN = [
    {"id": 1, "name": "Saluran Primer Bedadung",   "type": "Primer",   "kecamatan": "Patrang",     "panjang_km": 8.4, "layanan_ha": 2400, "kondisi": "Baik"},
    {"id": 2, "name": "Saluran Sekunder Wuluhan",  "type": "Sekunder", "kecamatan": "Wuluhan",     "panjang_km": 5.2, "layanan_ha": 1200, "kondisi": "Baik"},
    {"id": 3, "name": "Saluran Tersier Ambulu 01", "type": "Tersier",  "kecamatan": "Ambulu",      "panjang_km": 3.1, "layanan_ha": 480,  "kondisi": "Baik"},
    {"id": 4, "name": "Saluran Tersier Rambipuji","type": "Tersier",  "kecamatan": "Rambipuji",   "panjang_km": 2.8, "layanan_ha": 420,  "kondisi": "Sedang"},
    {"id": 5, "name": "Saluran Pembuang Bedadung","type": "Pembuang", "kecamatan": "Patrang",     "panjang_km": 6.2, "layanan_ha": 0,    "kondisi": "Baik"},
]

# ============================================================
# NERACA AIR (DEMO) — per kecamatan
# ============================================================
NERACA_AIR = [
    {"kecamatan": "Wuluhan",     "ketersediaan": 28.4, "kebutuhan": 24.2, "neraca": 4.2,  "status": "Surplus"},
    {"kecamatan": "Ambulu",      "ketersediaan": 22.6, "kebutuhan": 20.8, "neraca": 1.8,  "status": "Surplus"},
    {"kecamatan": "Patrang",     "ketersediaan": 32.8, "kebutuhan": 28.4, "neraca": 4.4,  "status": "Surplus"},
    {"kecamatan": "Rambipuji",   "ketersediaan": 18.4, "kebutuhan": 19.2, "neraca": -0.8, "status": "Defisit"},
    {"kecamatan": "Balung",      "ketersediaan": 12.2, "kebutuhan": 14.8, "neraca": -2.6, "status": "Defisit"},
    {"kecamatan": "Puger",       "ketersediaan": 16.4, "kebutuhan": 15.6, "neraca": 0.8,  "status": "Surplus"},
    {"kecamatan": "Jenggawah",   "ketersediaan": 14.2, "kebutuhan": 13.8, "neraca": 0.4,  "status": "Surplus"},
    {"kecamatan": "Tempurejo",   "ketersediaan": 20.8, "kebutuhan": 18.4, "neraca": 2.4,  "status": "Surplus"},
]

# KPI total
KPI = {
    "total_saluran":      sum(s["panjang_km"] for s in SALURAN),
    "total_layanan_ha":   sum(s["layanan_ha"] for s in SALURAN),
    "total_bangunan":     len(BANGUNAN),
    "total_ketersediaan": sum(n["ketersediaan"] for n in NERACA_AIR),
    "total_kebutuhan":    sum(n["kebutuhan"] for n in NERACA_AIR),
    "total_neraca":       sum(n["neraca"] for n in NERACA_AIR),
}


# ============================================================
# ROUTES
# ============================================================
@irigasi_bp.route("/irigasi")
@require_login
def index():
    return render_template(
        "irigasi.html",
        app_name=current_app.config["APP_NAME"],
        app_subtitle=current_app.config["APP_SUBTITLE"],
        app_region=current_app.config["APP_REGION"],
        user=current_user(),
        bangunan=BANGUNAN,
        saluran=SALURAN,
        neraca=NERACA_AIR,
        kpi=KPI,
    )


@irigasi_bp.route("/irigasi/data/neraca")
def data_neraca():
    """Endpoint JSON untuk chart neraca air."""
    return jsonify({
        "labels":          [n["kecamatan"] for n in NERACA_AIR],
        "ketersediaan":    [n["ketersediaan"] for n in NERACA_AIR],
        "kebutuhan":       [n["kebutuhan"] for n in NERACA_AIR],
        "neraca":          [n["neraca"] for n in NERACA_AIR],
        "unit":            "juta m³",
    })


@irigasi_bp.route("/irigasi/data/saluran")
def data_saluran():
    """Endpoint JSON untuk chart distribusi saluran."""
    types = {}
    for s in SALURAN:
        types[s["type"]] = types.get(s["type"], 0) + s["panjang_km"]
    return jsonify({
        "labels": list(types.keys()),
        "data":   [round(v, 2) for v in types.values()],
        "unit":   "km",
    })