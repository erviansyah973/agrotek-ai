"""
AGROTEK AI — Early Warning System
==================================
Halaman /risiko: monitoring risiko banjir & kekeringan.
Auto-focus peta + status real-time.
"""

from flask import Blueprint, render_template, current_app, jsonify
from app.auth_utils import require_login, current_user

risiko_bp = Blueprint("risiko", __name__)


# ============================================================
# STATUS GLOBAL (dihitung dari skor tertinggi)
# ============================================================
def compute_status(scores):
    if not scores:
        return "NORMAL"
    m = max(scores)
    if m >= 80: return "KRITIS"
    if m >= 65: return "SIAGA"
    if m >= 45: return "WASPADA"
    return "NORMAL"


# ============================================================
# DATA RISIKO BANJIR (DEMO)
# ============================================================
RISIKO_BANJIR = [
    {"district": "Tempurejo",   "level": "tinggi", "score": 82, "lat": -8.350, "lng": 113.720,
     "curah_hujan": 1800, "elevasi": 50, "catatan": "Dekat DAS Bondoyudo"},
    {"district": "Wuluhan",     "level": "sedang", "score": 68, "lat": -8.300, "lng": 113.550,
     "curah_hujan": 1600, "elevasi": 25, "catatan": "Dataran rendah"},
    {"district": "Puger",       "level": "sedang", "score": 65, "lat": -8.300, "lng": 113.480,
     "curah_hujan": 1550, "elevasi": 10, "catatan": "Pesisir selatan"},
    {"district": "Ambulu",      "level": "rendah", "score": 45, "lat": -8.320, "lng": 113.620,
     "curah_hujan": 1650, "elevasi": 30, "catatan": "Drainase baik"},
    {"district": "Bangsalsari", "level": "sedang", "score": 62, "lat": -8.100, "lng": 113.500,
     "curah_hujan": 1700, "elevasi": 150, "catatan": "Dekat sungai"},
    {"district": "Tanggul",     "level": "sedang", "score": 60, "lat": -8.050, "lng": 113.420,
     "curah_hujan": 1600, "elevasi": 200, "catatan": "Hulu sungai"},
    {"district": "Panti",       "level": "sedang", "score": 58, "lat": -8.080, "lng": 113.600,
     "curah_hujan": 1800, "elevasi": 250, "catatan": "Curah hujan tinggi"},
]

# ============================================================
# DATA RISIKO KEKERINGAN (DEMO)
# ============================================================
RISIKO_KERING = [
    {"district": "Sumberjambe", "level": "tinggi", "score": 76, "lat": -8.020, "lng": 113.850,
     "curah_hujan": 1150, "elevasi": 500, "catatan": "Curah hujan rendah"},
    {"district": "Silo",        "level": "tinggi", "score": 74, "lat": -8.200, "lng": 113.850,
     "curah_hujan": 1200, "elevasi": 250, "catatan": "Ketersediaan air rendah"},
    {"district": "Ledokombo",   "level": "sedang", "score": 60, "lat": -8.080, "lng": 113.850,
     "curah_hujan": 1250, "elevasi": 400, "catatan": "Topografi tinggi"},
    {"district": "Sukowono",    "level": "sedang", "score": 58, "lat": -8.050, "lng": 113.780,
     "curah_hujan": 1200, "elevasi": 450, "catatan": "Hulu DAS"},
    {"district": "Kalisat",     "level": "sedang", "score": 52, "lat": -8.100, "lng": 113.800,
     "curah_hujan": 1300, "elevasi": 350, "catatan": "Perlu irigasi"},
    {"district": "Jelbuk",      "level": "sedang", "score": 50, "lat": -8.050, "lng": 113.720,
     "curah_hujan": 1350, "elevasi": 380, "catatan": "Air tanah dalam"},
    {"district": "Arjasa",      "level": "sedang", "score": 48, "lat": -8.080, "lng": 113.720,
     "curah_hujan": 1500, "elevasi": 300, "catatan": "Kemiringan tinggi"},
]

# ============================================================
# EARLY WARNING FEED (DEMO)
# ============================================================
ALERTS = [
    {
        "id": 1,
        "type": "banjir",
        "level": "siaga",
        "district": "Tempurejo",
        "message": "Curah hujan tinggi 3 hari berturut. Waspadai luapan DAS Bondoyudo.",
        "waktu": "Hari ini 08:30",
        "lat": -8.350, "lng": 113.720,
    },
    {
        "id": 2,
        "type": "kekeringan",
        "level": "waspada",
        "district": "Silo",
        "message": "Hari tanpa hujan 21 hari. Ketersediaan air irigasi menurun.",
        "waktu": "Hari ini 07:15",
        "lat": -8.200, "lng": 113.850,
    },
    {
        "id": 3,
        "type": "banjir",
        "level": "waspada",
        "district": "Wuluhan",
        "message": "TMA Kali Bedadung naik +45 cm dalam 12 jam.",
        "waktu": "Kemarin 18:45",
        "lat": -8.300, "lng": 113.550,
    },
    {
        "id": 4,
        "type": "kekeringan",
        "level": "siaga",
        "district": "Sumberjambe",
        "message": "Status kekeringan Siaga. Rekomendasi: prioritaskan air untuk tanaman pangan.",
        "waktu": "Kemarin 14:20",
        "lat": -8.020, "lng": 113.850,
    },
]


# ============================================================
# ROUTES
# ============================================================
@risiko_bp.route("/risiko")
@require_login
def index():
    # Hitung status global
    banjir_status = compute_status([r["score"] for r in RISIKO_BANJIR])
    kering_status = compute_status([r["score"] for r in RISIKO_KERING])

    # Hitung statistik
    statistik = {
        "banjir_tinggi":  sum(1 for r in RISIKO_BANJIR if r["level"] == "tinggi"),
        "banjir_sedang":  sum(1 for r in RISIKO_BANJIR if r["level"] == "sedang"),
        "banjir_rendah":  sum(1 for r in RISIKO_BANJIR if r["level"] == "rendah"),
        "kering_tinggi":  sum(1 for r in RISIKO_KERING if r["level"] == "tinggi"),
        "kering_sedang":  sum(1 for r in RISIKO_KERING if r["level"] == "sedang"),
        "kering_rendah":  sum(1 for r in RISIKO_KERING if r["level"] == "rendah"),
        "total_alert":    len(ALERTS),
    }

    return render_template(
        "risiko.html",
        app_name=current_app.config["APP_NAME"],
        app_subtitle=current_app.config["APP_SUBTITLE"],
        app_region=current_app.config["APP_REGION"],
        user=current_user(),
        banjir=RISIKO_BANJIR,
        kering=RISIKO_KERING,
        alerts=ALERTS,
        banjir_status=banjir_status,
        kering_status=kering_status,
        statistik=statistik,
    )


@risiko_bp.route("/risiko/data/banjir")
def data_banjir():
    return jsonify({"type": "FeatureCollection", "features": [
        {
            "type": "Feature",
            "properties": {
                "district": r["district"],
                "level": r["level"],
                "score": r["score"],
                "catatan": r["catatan"],
            },
            "geometry": {"type": "Point", "coordinates": [r["lng"], r["lat"]]},
        } for r in RISIKO_BANJIR
    ]})


@risiko_bp.route("/risiko/data/kering")
def data_kering():
    return jsonify({"type": "FeatureCollection", "features": [
        {
            "type": "Feature",
            "properties": {
                "district": r["district"],
                "level": r["level"],
                "score": r["score"],
                "catatan": r["catatan"],
            },
            "geometry": {"type": "Point", "coordinates": [r["lng"], r["lat"]]},
        } for r in RISIKO_KERING
    ]})