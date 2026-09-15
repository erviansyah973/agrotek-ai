"""
AGROTEK AI — Analisis Sawah Saya
==================================
Sistem rekomendasi tanaman berbasis RULE-BASED (bukan ML).
Transparansi penuh: input → parameter → bobot → skor → rekomendasi.

Metode: Weighted Overlay sederhana
Skor: 0-100
Kelas: S1 (Sangat Sesuai), S2 (Sesuai), S3 (Cukup Sesuai), N (Tidak Sesuai)
"""

from flask import Blueprint, render_template, current_app, jsonify, request
from app.auth_utils import require_login, current_user

ai_bp = Blueprint("ai", __name__)


# ============================================================
# PARAMETER IDEAL PER KOMODITAS
# ============================================================
KOMODITAS_RULES = {
    "PDI": {
        "name": "Padi",
        "icon": "🌾",
        "curah_hujan": [1500, 2500],
        "elevasi": [0, 600],
        "kemiringan": [0, 8],
        "kebutuhan_air": "tinggi",
    },
    "JAG": {
        "name": "Jagung",
        "icon": "🌽",
        "curah_hujan": [800, 1800],
        "elevasi": [0, 900],
        "kemiringan": [0, 15],
        "kebutuhan_air": "sedang",
    },
    "KED": {
        "name": "Kedelai",
        "icon": "🫘",
        "curah_hujan": [700, 1500],
        "elevasi": [0, 700],
        "kemiringan": [0, 12],
        "kebutuhan_air": "sedang",
    },
    "CBI": {
        "name": "Cabai",
        "icon": "🌶️",
        "curah_hujan": [800, 1800],
        "elevasi": [200, 1200],
        "kemiringan": [0, 20],
        "kebutuhan_air": "sedang",
    },
    "TMK": {
        "name": "Tembakau",
        "icon": "🍂",
        "curah_hujan": [600, 1500],
        "elevasi": [100, 900],
        "kemiringan": [0, 15],
        "kebutuhan_air": "rendah",
    },
    "KOP": {
        "name": "Kopi",
        "icon": "☕",
        "curah_hujan": [1500, 2500],
        "elevasi": [600, 1500],
        "kemiringan": [5, 30],
        "kebutuhan_air": "sedang",
    },
}

# ============================================================
# PARAMETER PER KECAMATAN (DEMO)
# ============================================================
KECAMATAN_PARAMS = {
    "Kencong":       {"curah_hujan": 1400, "elevasi": 15,  "kemiringan": 2,  "ketersediaan_air": "sedang", "risiko_banjir": "rendah", "risiko_kekeringan": "rendah"},
    "Gumukmas":      {"curah_hujan": 1450, "elevasi": 20,  "kemiringan": 3,  "ketersediaan_air": "sedang", "risiko_banjir": "rendah", "risiko_kekeringan": "rendah"},
    "Puger":         {"curah_hujan": 1550, "elevasi": 10,  "kemiringan": 2,  "ketersediaan_air": "tinggi", "risiko_banjir": "sedang", "risiko_kekeringan": "sedang"},
    "Wuluhan":       {"curah_hujan": 1600, "elevasi": 25,  "kemiringan": 3,  "ketersediaan_air": "tinggi", "risiko_banjir": "sedang", "risiko_kekeringan": "rendah"},
    "Ambulu":        {"curah_hujan": 1650, "elevasi": 30,  "kemiringan": 4,  "ketersediaan_air": "tinggi", "risiko_banjir": "rendah", "risiko_kekeringan": "sedang"},
    "Tempurejo":     {"curah_hujan": 1800, "elevasi": 50,  "kemiringan": 6,  "ketersediaan_air": "tinggi", "risiko_banjir": "tinggi", "risiko_kekeringan": "sedang"},
    "Silo":          {"curah_hujan": 1200, "elevasi": 250, "kemiringan": 15, "ketersediaan_air": "rendah", "risiko_banjir": "rendah", "risiko_kekeringan": "tinggi"},
    "Mayang":        {"curah_hujan": 1500, "elevasi": 150, "kemiringan": 8,  "ketersediaan_air": "sedang", "risiko_banjir": "rendah", "risiko_kekeringan": "sedang"},
    "Mumbulsari":    {"curah_hujan": 1450, "elevasi": 180, "kemiringan": 10, "ketersediaan_air": "sedang", "risiko_banjir": "rendah", "risiko_kekeringan": "sedang"},
    "Jenggawah":     {"curah_hujan": 1500, "elevasi": 100, "kemiringan": 6,  "ketersediaan_air": "sedang", "risiko_banjir": "rendah", "risiko_kekeringan": "sedang"},
    "Ajung":         {"curah_hujan": 1500, "elevasi": 80,  "kemiringan": 4,  "ketersediaan_air": "sedang", "risiko_banjir": "rendah", "risiko_kekeringan": "sedang"},
    "Rambipuji":     {"curah_hujan": 1550, "elevasi": 60,  "kemiringan": 3,  "ketersediaan_air": "tinggi", "risiko_banjir": "rendah", "risiko_kekeringan": "sedang"},
    "Balung":        {"curah_hujan": 1500, "elevasi": 40,  "kemiringan": 3,  "ketersediaan_air": "sedang", "risiko_banjir": "rendah", "risiko_kekeringan": "sedang"},
    "Umbulsari":     {"curah_hujan": 1400, "elevasi": 30,  "kemiringan": 2,  "ketersediaan_air": "sedang", "risiko_banjir": "rendah", "risiko_kekeringan": "rendah"},
    "Semboro":       {"curah_hujan": 1350, "elevasi": 25,  "kemiringan": 2,  "ketersediaan_air": "sedang", "risiko_banjir": "rendah", "risiko_kekeringan": "rendah"},
    "Jombang":       {"curah_hujan": 1350, "elevasi": 30,  "kemiringan": 2,  "ketersediaan_air": "sedang", "risiko_banjir": "rendah", "risiko_kekeringan": "rendah"},
    "Sumberbaru":    {"curah_hujan": 1500, "elevasi": 120, "kemiringan": 8,  "ketersediaan_air": "sedang", "risiko_banjir": "rendah", "risiko_kekeringan": "sedang"},
    "Tanggul":       {"curah_hujan": 1600, "elevasi": 200, "kemiringan": 12, "ketersediaan_air": "sedang", "risiko_banjir": "sedang", "risiko_kekeringan": "sedang"},
    "Bangsalsari":   {"curah_hujan": 1700, "elevasi": 150, "kemiringan": 10, "ketersediaan_air": "tinggi", "risiko_banjir": "sedang", "risiko_kekeringan": "sedang"},
    "Panti":         {"curah_hujan": 1800, "elevasi": 250, "kemiringan": 14, "ketersediaan_air": "sedang", "risiko_banjir": "sedang", "risiko_kekeringan": "sedang"},
    "Sukorambi":     {"curah_hujan": 1600, "elevasi": 200, "kemiringan": 10, "ketersediaan_air": "sedang", "risiko_banjir": "rendah", "risiko_kekeringan": "sedang"},
    "Arjasa":        {"curah_hujan": 1500, "elevasi": 300, "kemiringan": 18, "ketersediaan_air": "sedang", "risiko_banjir": "rendah", "risiko_kekeringan": "tinggi"},
    "Pakusari":      {"curah_hujan": 1500, "elevasi": 200, "kemiringan": 10, "ketersediaan_air": "sedang", "risiko_banjir": "rendah", "risiko_kekeringan": "sedang"},
    "Kalisat":       {"curah_hujan": 1300, "elevasi": 350, "kemiringan": 20, "ketersediaan_air": "rendah", "risiko_banjir": "rendah", "risiko_kekeringan": "sedang"},
    "Ledokombo":     {"curah_hujan": 1250, "elevasi": 400, "kemiringan": 22, "ketersediaan_air": "rendah", "risiko_banjir": "rendah", "risiko_kekeringan": "sedang"},
    "Sumberjambe":   {"curah_hujan": 1150, "elevasi": 500, "kemiringan": 25, "ketersediaan_air": "rendah", "risiko_banjir": "rendah", "risiko_kekeringan": "tinggi"},
    "Sukowono":      {"curah_hujan": 1200, "elevasi": 450, "kemiringan": 24, "ketersediaan_air": "rendah", "risiko_banjir": "rendah", "risiko_kekeringan": "sedang"},
    "Jelbuk":        {"curah_hujan": 1350, "elevasi": 380, "kemiringan": 18, "ketersediaan_air": "sedang", "risiko_banjir": "rendah", "risiko_kekeringan": "sedang"},
    "Kaliwates":     {"curah_hujan": 1550, "elevasi": 90,  "kemiringan": 4,  "ketersediaan_air": "sedang", "risiko_banjir": "rendah", "risiko_kekeringan": "rendah"},
    "Sumbersari":    {"curah_hujan": 1550, "elevasi": 100, "kemiringan": 5,  "ketersediaan_air": "sedang", "risiko_banjir": "rendah", "risiko_kekeringan": "rendah"},
    "Patrang":       {"curah_hujan": 1600, "elevasi": 130, "kemiringan": 8,  "ketersediaan_air": "tinggi", "risiko_banjir": "rendah", "risiko_kekeringan": "rendah"},
}

# ============================================================
# BOBOT PARAMETER (WAJIB TOTAL = 1.0)
# ============================================================
BOBOT = {
    "curah_hujan":        0.30,
    "elevasi":            0.15,
    "kemiringan":         0.20,
    "ketersediaan_air":   0.20,
    "risiko":             0.15,
}

# Konversi kategorik ke skor
AIR_SCORE     = {"tinggi": 100, "sedang": 70, "rendah": 40}
RISIKO_SCORE  = {"rendah": 100, "sedang": 70, "tinggi": 35}


# ============================================================
# FUNGSI SKORING
# ============================================================
def score_range(value, min_val, max_val):
    """Skor 0-100: 100 kalau dalam range, turun linear di luar range."""
    if min_val <= value <= max_val:
        return 100.0
    if value < min_val:
        distance = min_val - value
        span = max(max_val - min_val, 1)
        return max(0.0, 100.0 - (distance / span * 100))
    # value > max_val
    distance = value - max_val
    span = max(max_val - min_val, 1)
    return max(0.0, 100.0 - (distance / span * 100))


def score_risiko(banjir, kekeringan):
    """Rata-rata skor dari risiko banjir + kekeringan."""
    return (RISIKO_SCORE[banjir] + RISIKO_SCORE[kekeringan]) / 2


def class_from_score(score):
    if score >= 80:
        return "S1", "Sangat Sesuai"
    if score >= 65:
        return "S2", "Sesuai"
    if score >= 45:
        return "S3", "Cukup Sesuai"
    return "N", "Tidak Sesuai"


def analyze(kecamatan, kode_komoditas):
    """Fungsi utama analisis. Return dict dengan semua info."""
    rule = KOMODITAS_RULES.get(kode_komoditas)
    params = KECAMATAN_PARAMS.get(kecamatan)

    if not rule or not params:
        return None

    # Hitung skor per parameter
    s_hujan = score_range(params["curah_hujan"], *rule["curah_hujan"])
    s_elev  = score_range(params["elevasi"],    *rule["elevasi"])
    s_slope = score_range(params["kemiringan"], *rule["kemiringan"])
    s_air   = AIR_SCORE[params["ketersediaan_air"]]
    s_risk  = score_risiko(params["risiko_banjir"], params["risiko_kekeringan"])

    scores = {
        "curah_hujan":      round(s_hujan, 1),
        "elevasi":          round(s_elev, 1),
        "kemiringan":       round(s_slope, 1),
        "ketersediaan_air": round(s_air, 1),
        "risiko":           round(s_risk, 1),
    }

    # Skor total (weighted sum)
    total = sum(scores[k] * BOBOT[k] for k in BOBOT)
    total = round(total, 1)

    kelas, kelas_label = class_from_score(total)

    # Generate rekomendasi
    rekomendasi = []

    if s_hujan < 60:
        rekomendasi.append(
            f"Curah hujan {params['curah_hujan']} mm di luar rentang optimal "
            f"({rule['curah_hujan'][0]}-{rule['curah_hujan'][1]} mm) untuk {rule['name']}."
        )

    if s_elev < 60:
        rekomendasi.append(
            f"Elevasi {params['elevasi']} m kurang ideal "
            f"({rule['elevasi'][0]}-{rule['elevasi'][1]} m)."
        )

    if s_slope < 60:
        rekomendasi.append(
            f"Kemiringan lahan {params['kemiringan']}% berpotensi erosi. "
            "Pertimbangkan terasering atau tanaman penutup tanah."
        )

    if s_air < 60:
        rekomendasi.append(
            "Ketersediaan air rendah. Siapkan irigasi tambahan atau "
            "pilih komoditas yang lebih hemat air."
        )

    if params["risiko_banjir"] == "tinggi":
        rekomendasi.append(
            "Risiko banjir tinggi. Hindari penanaman di musim hujan puncak."
        )

    if params["risiko_kekeringan"] == "tinggi":
        rekomendasi.append(
            "Risiko kekeringan tinggi. Siapkan panen air hujan atau mulsa."
        )

    if not rekomendasi:
        rekomendasi.append(
            f"Parameter lingkungan sangat mendukung budidaya {rule['name']} "
            f"di {kecamatan}."
        )

    return {
        "kecamatan":         kecamatan,
        "komoditas":         rule["name"],
        "komoditas_kode":    kode_komoditas,
        "komoditas_icon":    rule["icon"],
        "kelas":             kelas,
        "kelas_label":       kelas_label,
        "skor_total":        total,
        "scores":            scores,
        "bobot":             BOBOT,
        "params":            params,
        "rule":              rule,
        "rekomendasi":       rekomendasi,
    }


# ============================================================
# ROUTES
# ============================================================
@ai_bp.route("/ai")
@require_login
def index():
    # Daftar kecamatan (sorted alphabetically)
    kecamatan_list = sorted(KECAMATAN_PARAMS.keys())

    # Daftar komoditas
    komoditas_list = [
        {"kode": k, "name": v["name"], "icon": v["icon"]}
        for k, v in KOMODITAS_RULES.items()
    ]

    return render_template(
        "ai.html",
        app_name=current_app.config["APP_NAME"],
        app_subtitle=current_app.config["APP_SUBTITLE"],
        app_region=current_app.config["APP_REGION"],
        user=current_user(),
        kecamatan_list=kecamatan_list,
        komoditas_list=komoditas_list,
    )


@ai_bp.route("/ai/analyze", methods=["POST"])
def analyze_endpoint():
    """Endpoint JSON: terima (kecamatan, komoditas) → return hasil analisis."""
    data = request.get_json(silent=True) or {}

    kecamatan = (data.get("kecamatan") or "").strip()
    komoditas = (data.get("komoditas") or "").strip().upper()

    if not kecamatan or not komoditas:
        return jsonify({"ok": False, "error": "Kecamatan dan komoditas wajib dipilih."}), 400

    if kecamatan not in KECAMATAN_PARAMS:
        return jsonify({"ok": False, "error": f"Kecamatan '{kecamatan}' tidak ditemukan."}), 404

    if komoditas not in KOMODITAS_RULES:
        return jsonify({"ok": False, "error": f"Komoditas '{komoditas}' tidak dikenal."}), 404

    result = analyze(kecamatan, komoditas)

    if not result:
        return jsonify({"ok": False, "error": "Analisis gagal."}), 500

    return jsonify({"ok": True, "result": result})