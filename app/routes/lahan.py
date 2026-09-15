"""
AGROTEK AI — Kesesuaian Lahan
==============================
Halaman /lahan: visualisasi kesesuaian lahan per kecamatan
untuk komoditas utama (Padi, Jagung, Tembakau).

Metode: Weighted Overlay (sama dengan AGROTEK AI, tapi agregat).
"""

from flask import Blueprint, render_template, current_app, jsonify, request
from app.auth_utils import require_login, current_user

lahan_bp = Blueprint("lahan", __name__)


# ============================================================
# DATA KESESUAIAN LAHAN (DEMO — hasil perhitungan sudah jadi)
# ============================================================
# Format: (kecamatan, kelas, skor, luas_potensial_ha)
DATA = {
    "PDI": {  # Padi
        "label": "Padi",
        "icon": "🌾",
        "rows": [
            {"kecamatan": "Wuluhan",   "kelas": "S1", "skor": 88, "luas_ha": 8420},
            {"kecamatan": "Patrang",   "kelas": "S1", "skor": 86, "luas_ha": 6180},
            {"kecamatan": "Ambulu",    "kelas": "S1", "skor": 85, "luas_ha": 7260},
            {"kecamatan": "Jenggawah", "kelas": "S2", "skor": 78, "luas_ha": 4380},
            {"kecamatan": "Rambipuji", "kelas": "S2", "skor": 74, "luas_ha": 5120},
            {"kecamatan": "Bangsalsari","kelas":"S2", "skor": 72, "luas_ha": 6840},
            {"kecamatan": "Puger",     "kelas": "S3", "skor": 62, "luas_ha": 3260},
            {"kecamatan": "Balung",    "kelas": "S3", "skor": 58, "luas_ha": 2840},
            {"kecamatan": "Silo",      "kelas": "N",  "skor": 42, "luas_ha": 0},
            {"kecamatan": "Sumberjambe","kelas":"N",  "skor": 38, "luas_ha": 0},
        ],
    },
    "JAG": {  # Jagung
        "label": "Jagung",
        "icon": "🌽",
        "rows": [
            {"kecamatan": "Ambulu",    "kelas": "S1", "skor": 84, "luas_ha": 5240},
            {"kecamatan": "Wuluhan",   "kelas": "S1", "skor": 82, "luas_ha": 4180},
            {"kecamatan": "Bangsalsari","kelas":"S1", "skor": 81, "luas_ha": 6120},
            {"kecamatan": "Silo",      "kelas": "S2", "skor": 72, "luas_ha": 4820},
            {"kecamatan": "Mayang",    "kelas": "S2", "skor": 70, "luas_ha": 3640},
            {"kecamatan": "Tempurejo", "kelas": "S2", "skor": 68, "luas_ha": 5460},
            {"kecamatan": "Kalisat",   "kelas": "S3", "skor": 58, "luas_ha": 2840},
            {"kecamatan": "Sukowono",  "kelas": "S3", "skor": 55, "luas_ha": 2420},
            {"kecamatan": "Puger",     "kelas": "S3", "skor": 52, "luas_ha": 1680},
            {"kecamatan": "Kaliwates", "kelas": "N",  "skor": 40, "luas_ha": 0},
        ],
    },
    "TMK": {  # Tembakau
        "label": "Tembakau",
        "icon": "🍂",
        "rows": [
            {"kecamatan": "Jelbuk",    "kelas": "S1", "skor": 88, "luas_ha": 3240},
            {"kecamatan": "Arjasa",    "kelas": "S1", "skor": 85, "luas_ha": 2860},
            {"kecamatan": "Sukorambi", "kelas": "S1", "skor": 82, "luas_ha": 2240},
            {"kecamatan": "Kalisat",   "kelas": "S2", "skor": 76, "luas_ha": 4620},
            {"kecamatan": "Ledokombo", "kelas": "S2", "skor": 74, "luas_ha": 5840},
            {"kecamatan": "Pakusari",  "kelas": "S2", "skor": 72, "luas_ha": 2180},
            {"kecamatan": "Sukowono",  "kelas": "S3", "skor": 62, "luas_ha": 3420},
            {"kecamatan": "Mayang",    "kelas": "S3", "skor": 58, "luas_ha": 1820},
            {"kecamatan": "Panti",     "kelas": "N",  "skor": 44, "luas_ha": 0},
            {"kecamatan": "Wuluhan",   "kelas": "N",  "skor": 38, "luas_ha": 0},
        ],
    },
}

# Bobot parameter (untuk ditampilkan transparan)
BOBOT = {
    "curah_hujan":    0.30,
    "kemiringan":     0.20,
    "ketersediaan_air":0.20,
    "elevasi":        0.15,
    "risiko":         0.15,
}


def _summary(rows):
    """Hitung ringkasan distribusi kelas."""
    s = {"S1": 0, "S2": 0, "S3": 0, "N": 0}
    luas = {"S1": 0, "S2": 0, "S3": 0, "N": 0}
    for r in rows:
        s[r["kelas"]] += 1
        luas[r["kelas"]] += r["luas_ha"]
    return {
        "count": s,
        "luas": luas,
        "total_luas_sesuai": luas["S1"] + luas["S2"] + luas["S3"],
    }


# ============================================================
# ROUTES
# ============================================================
@lahan_bp.route("/lahan")
@require_login
def index():
    # Ambil komoditas dari query (default Padi)
    crop = request.args.get("crop", "PDI").upper()
    if crop not in DATA:
        crop = "PDI"

    data = DATA[crop]
    summary = _summary(data["rows"])

    # Ringkasan semua komoditas (untuk tab preview)
    all_summary = {}
    for k, v in DATA.items():
        all_summary[k] = {
            "label": v["label"],
            "icon": v["icon"],
            "count": _summary(v["rows"])["count"],
            "total_luas_sesuai": _summary(v["rows"])["total_luas_sesuai"],
        }

    return render_template(
        "lahan.html",
        app_name=current_app.config["APP_NAME"],
        app_subtitle=current_app.config["APP_SUBTITLE"],
        app_region=current_app.config["APP_REGION"],
        user=current_user(),
        crop=crop,
        data=data,
        summary=summary,
        all_summary=all_summary,
        bobot=BOBOT,
    )


@lahan_bp.route("/lahan/data/<crop>")
def data(crop):
    """Endpoint JSON untuk chart."""
    crop = crop.upper()
    if crop not in DATA:
        return jsonify({"ok": False, "error": "Komoditas tidak dikenal"}), 404

    d = DATA[crop]
    s = _summary(d["rows"])

    return jsonify({
        "ok": True,
        "crop": crop,
        "label": d["label"],
        "rows": d["rows"],
        "distribusi": s["count"],
        "luas": s["luas"],
        "total_luas_sesuai": s["total_luas_sesuai"],
    })