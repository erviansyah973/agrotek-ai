"""
AGROTEK AI — Main Routes
========================
"""

import csv
import io
import os
import zipfile
from flask import (
    Blueprint,
    current_app,
    abort,
    jsonify,
    render_template,
    request,
    Response,
    send_file,
)
from app.auth_utils import require_login, require_role, current_user
from app import data_catalog as catalog

main_bp = Blueprint("main", __name__)

EPAKSI_LAYERS = {
    "bangunan": "irigasi_epaksi_bangunan.geojson",
    "jaringan": "irigasi_epaksi_jaringan.geojson",
    "petak": "irigasi_epaksi_petak.geojson",
}
JEMBER_RIVERS_FILE = "sungai_line_25k_jember.geojson"
JEMBER_BOUNDARIES = {
    "kabupaten": "batas_jember_kabupaten.geojson",
    "kecamatan": "batas_jember_kecamatan.geojson",
    "desa": "batas_jember_desa.geojson",
}


def _gis_data_dir():
    configured_path = os.environ.get("GIS_DATA_DIR") or os.environ.get("EPAKSI_DATA_DIR")
    if configured_path:
        return os.path.abspath(configured_path)
    return os.path.abspath(
        os.path.join(current_app.root_path, "..", "private_data", "irigasi_epaksi")
    )


def _epaksi_data_dir():
    return _gis_data_dir()


# ============================================================
# DATA DEMO
# ============================================================
STATS = [
    {"value": 31,    "unit": "",        "label": "Kecamatan",        "icon": "1"},
    {"value": 248,   "unit": "",        "label": "Desa / Kelurahan", "icon": "2"},
    {"value": 178.4, "unit": "ribu ha", "label": "Luas Pertanian",   "icon": "3"},
    {"value": 1240,  "unit": "km",      "label": "Jaringan Irigasi", "icon": "4"},
]

MONITORING = [
    {"title": "Smart Irrigation", "metric": "Debit rata-rata 4.2 m³/s", "status": "normal",  "label": "Normal"},
    {"title": "Hydrology",        "metric": "TMA +18 cm / 24 jam",      "status": "warning", "label": "Waspada"},
    {"title": "Agriculture",      "metric": "NDVI rata-rata 0.62",       "status": "normal",  "label": "Normal"},
    {"title": "Early Warning",    "metric": "2 kecamatan rawan banjir",  "status": "alert",   "label": "Siaga"},
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
    {"time": "08:00", "sensor": "AWLR Bedadung",     "param": "TMA",         "value": "182 cm",   "status": "normal"},
    {"time": "08:05", "sensor": "AWLR Wuluhan",      "param": "TMA",         "value": "215 cm",   "status": "warning"},
    {"time": "08:10", "sensor": "Weather Jenggawah", "param": "Curah Hujan", "value": "12 mm",    "status": "normal"},
    {"time": "08:15", "sensor": "Sensor Tanah A1",   "param": "Kelembapan",  "value": "38%",      "status": "warning"},
    {"time": "08:20", "sensor": "Debit Bedadung",    "param": "Debit",       "value": "4.8 m³/s", "status": "normal"},
    {"time": "08:25", "sensor": "Early Warning",     "param": "Status",      "value": "Siaga",    "status": "alert"},
]

MODULES_DEMO = [
    {"icon": "🌱", "color": "emerald", "title": "Pertanian",         "desc": "Komoditas, produksi, produktivitas, dan kalender tanam."},
    {"icon": "💧", "color": "sky",     "title": "Smart Irrigation",  "desc": "Jaringan irigasi, bendung, saluran, dan neraca air."},
    {"icon": "🌊", "color": "cyan",    "title": "Hydrology",         "desc": "Curah hujan, debit, tinggi muka air, dan DAS."},
    {"icon": "⚠️", "color": "red",     "title": "Early Warning",     "desc": "Risiko banjir & kekeringan dengan status real-time."},
    {"icon": "🗺️", "color": "amber",   "title": "Analisis Lahan",    "desc": "Kesesuaian lahan dengan metode weighted overlay."},
    {"icon": "🤖", "color": "purple",  "title": "AGROTEK AI",        "desc": "Rekomendasi berbasis parameter spasial dengan transparansi penuh."},
]

# ============================================================
# PUBLIC
# ============================================================
@main_bp.route("/")
def landing():
    return render_template("landing.html",
        app_name=current_app.config["APP_NAME"],
        app_subtitle=current_app.config["APP_SUBTITLE"],
        app_region=current_app.config["APP_REGION"],
        is_logged_in=current_user() is not None)


@main_bp.route("/demo")
def demo():
    return render_template("demo.html",
        app_name=current_app.config["APP_NAME"],
        app_subtitle=current_app.config["APP_SUBTITLE"],
        app_region=current_app.config["APP_REGION"],
        stats=STATS, monitoring=MONITORING,
        risk=RISK_DATA, monitoring_table=MONITORING_TABLE,
        modules=MODULES_DEMO)


# ============================================================
# PETA 3D (BARU!)
# ============================================================
@main_bp.route("/peta3d")
def peta3d():
    """3D WebGIS Google-Earth style dengan SHP asli Jember."""
    return render_template(
        "peta3d.html",
        app_name=current_app.config["APP_NAME"],
        app_subtitle=current_app.config["APP_SUBTITLE"],
        app_region=current_app.config["APP_REGION"],
        user=current_user(),
        is_logged_in=current_user() is not None,
    )


# ============================================================
# PETA 2D
# ============================================================
@main_bp.route("/peta")
def peta():
    data_dir = _epaksi_data_dir()
    epaksi_available = all(
        os.path.isfile(os.path.join(data_dir, filename))
        for filename in EPAKSI_LAYERS.values()
    )
    jember_rivers_available = os.path.isfile(
        os.path.join(_gis_data_dir(), JEMBER_RIVERS_FILE)
    )
    jember_boundaries_available = {
        layer: os.path.isfile(os.path.join(_gis_data_dir(), filename))
        for layer, filename in JEMBER_BOUNDARIES.items()
    }
    return render_template("peta.html",
        app_name=current_app.config["APP_NAME"],
        app_subtitle=current_app.config["APP_SUBTITLE"],
        app_region=current_app.config["APP_REGION"],
        user=current_user(),
        epaksi_available=epaksi_available,
        jember_rivers_available=jember_rivers_available,
        jember_boundaries_available=jember_boundaries_available,
        is_logged_in=current_user() is not None)


@main_bp.route("/peta/unduh/epaksi")
def download_epaksi():
    data_dir = _epaksi_data_dir()
    if not all(os.path.isfile(os.path.join(data_dir, filename)) for filename in EPAKSI_LAYERS.values()):
        abort(404)

    archive_buffer = io.BytesIO()

    with zipfile.ZipFile(archive_buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for filename in EPAKSI_LAYERS.values():
            archive.write(os.path.join(data_dir, filename), arcname=filename)

    archive_buffer.seek(0)
    response = send_file(
        archive_buffer,
        mimetype="application/zip",
        as_attachment=True,
        download_name="agrotek-shp-epaksi-geojson.zip",
        max_age=0,
    )
    response.headers["Cache-Control"] = "public, max-age=3600"
    return response


@main_bp.route("/peta/data/epaksi/<layer_name>")
def data_epaksi(layer_name):
    filename = EPAKSI_LAYERS.get(layer_name)
    if filename is None:
        abort(404)

    data_dir = _epaksi_data_dir()
    file_path = os.path.join(data_dir, filename)
    if not os.path.isfile(file_path):
        abort(404)

    response = send_file(
        file_path,
        mimetype="application/geo+json",
        max_age=3600,
    )
    response.headers["Cache-Control"] = "public, max-age=3600"
    return response


# ------------------------------------------------------------
# JSON endpoints peta
# ------------------------------------------------------------
@main_bp.route("/peta/data/rivers/jember")
def data_jember_rivers():
    file_path = os.path.join(_gis_data_dir(), JEMBER_RIVERS_FILE)
    if not os.path.isfile(file_path):
        abort(404)

    response = send_file(
        file_path,
        mimetype="application/geo+json",
        max_age=3600,
    )
    response.headers["Cache-Control"] = "public, max-age=3600"
    return response


@main_bp.route("/peta/data/boundaries/jember/<layer_name>")
def data_jember_boundary(layer_name):
    filename = JEMBER_BOUNDARIES.get(layer_name)
    if filename is None:
        abort(404)

    file_path = os.path.join(_gis_data_dir(), filename)
    if not os.path.isfile(file_path):
        abort(404)

    response = send_file(
        file_path,
        mimetype="application/geo+json",
        max_age=3600,
    )
    response.headers["Cache-Control"] = "public, max-age=3600"
    return response


# ============================================================
# DATA CENTER
# ============================================================
@main_bp.route("/data")
@require_login
def data_center():
    all_datasets = catalog.all_datasets()
    categories = catalog.all_categories()
    for category in categories:
        category["count"] = sum(1 for dataset in all_datasets if dataset["category"] == category["key"])
    status_counts = {
        status: sum(1 for dataset in all_datasets if dataset["status"] == status)
        for status in ("PUBLIC", "RESTRICTED", "INTERNAL")
    }
    category_keys = {category["key"] for category in categories}
    current_category = request.args.get("category", "all").strip().lower()
    if current_category != "all" and current_category not in category_keys:
        current_category = "all"
    current_status = request.args.get("status", "all").strip().upper()
    if current_status not in ("all", "PUBLIC", "RESTRICTED", "INTERNAL"):
        current_status = "all"
    current_q = request.args.get("q", "").strip()[:100]

    datasets = all_datasets
    if current_category != "all":
        datasets = [dataset for dataset in datasets if dataset["category"] == current_category]
    if current_status != "all":
        datasets = [dataset for dataset in datasets if dataset["status"] == current_status]
    if current_q:
        query = current_q.casefold()
        datasets = [
            dataset for dataset in datasets
            if query in " ".join((
                dataset["name"],
                dataset["desc"],
                dataset["source"],
                dataset["category_label"],
                " ".join(dataset["keywords"]),
            )).casefold()
        ]

    return render_template("data.html",
        app_name=current_app.config["APP_NAME"],
        app_subtitle=current_app.config["APP_SUBTITLE"],
        app_region=current_app.config["APP_REGION"],
        user=current_user(),
        datasets=datasets,
        categories=categories,
        current_category=current_category,
        current_status=current_status,
        current_q=current_q,
        status_counts=status_counts)


@main_bp.route("/data/<slug>")
@require_login
def data_detail(slug):
    ds = catalog.get_dataset(slug)
    if not ds:
        return render_template("404.html",
            app_name=current_app.config["APP_NAME"],
            app_subtitle=current_app.config["APP_SUBTITLE"],
            app_region=current_app.config["APP_REGION"]), 404
    return render_template("data_detail.html",
        app_name=current_app.config["APP_NAME"],
        app_subtitle=current_app.config["APP_SUBTITLE"],
        app_region=current_app.config["APP_REGION"],
        user=current_user(), ds=ds)


@main_bp.route("/data/<slug>/download")
@require_login
def data_download(slug):
    import json
    ds = catalog.get_dataset(slug)
    if not ds:
        return "Dataset tidak ditemukan", 404
    if ds["status"] != "PUBLIC":
        return "Dataset tidak dapat diunduh.", 403
    payload = {"metadata": ds, "data": []}
    return Response(
        json.dumps(payload, indent=2, ensure_ascii=False),
        mimetype="application/json",
        headers={"Content-Disposition": f'attachment; filename="{slug}.json"'})


# ============================================================
# MODUL (butuh login)
# ============================================================
@main_bp.route("/statistik")
@require_login
def statistik():
    return render_template("statistik.html",
        app_name=current_app.config["APP_NAME"],
        app_subtitle=current_app.config["APP_SUBTITLE"],
        app_region=current_app.config["APP_REGION"],
        user=current_user(), stats=STATS, monitoring=MONITORING)


@main_bp.route("/analisis")
@require_login
def analisis():
    return render_template("analisis.html",
        app_name=current_app.config["APP_NAME"],
        app_subtitle=current_app.config["APP_SUBTITLE"],
        app_region=current_app.config["APP_REGION"],
        user=current_user())


@main_bp.route("/laporan")
@require_login
def laporan():
    return render_template("laporan.html",
        app_name=current_app.config["APP_NAME"],
        app_subtitle=current_app.config["APP_SUBTITLE"],
        app_region=current_app.config["APP_REGION"],
        user=current_user())


# ============================================================
# API: Data Request
# ============================================================
@main_bp.route("/api/data-request", methods=["POST"])
def api_data_request():
    from flask import request
    from app.models import DataRequest, Log
    from app.extensions import db

    name = (request.form.get("name") or "").strip()
    email = (request.form.get("email") or "").strip().lower()
    institution = (request.form.get("institution") or "").strip()
    slug = (request.form.get("dataset_slug") or "").strip()
    fmt = (request.form.get("format") or "").strip()
    purpose = (request.form.get("purpose") or "").strip()

    if not name or len(name) < 3:
        return jsonify({"ok": False, "error": "Nama minimal 3 karakter."}), 400
    if not email or "@" not in email:
        return jsonify({"ok": False, "error": "Email tidak valid."}), 400
    if not slug:
        return jsonify({"ok": False, "error": "Dataset tidak valid."}), 400
    if not purpose or len(purpose) < 10:
        return jsonify({"ok": False, "error": "Tujuan minimal 10 karakter."}), 400

    try:
        req = DataRequest(
            name=name[:160], email=email[:160],
            institution=institution[:200],
            dataset_slug=slug[:120], format=fmt[:40],
            purpose=purpose[:2000], status="pending")
        db.session.add(req)
        db.session.add(Log(level="info", source="data-request",
                           message="Request: " + email))
        db.session.commit()
        return jsonify({"ok": True, "id": req.id, "message": "Permintaan berhasil dikirim."})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


# ============================================================
# EXPORT CSV
# ============================================================
def _csv_response(rows, headers, filename):
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=headers)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    return Response(
        buf.getvalue(),
        mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'})


@main_bp.route("/export/rainfall.csv")
@require_login
def export_rainfall():
    data = [
        {"bulan": "Jan", "curah_hujan_mm": 280}, {"bulan": "Feb", "curah_hujan_mm": 265},
        {"bulan": "Mar", "curah_hujan_mm": 240}, {"bulan": "Apr", "curah_hujan_mm": 150},
        {"bulan": "Mei", "curah_hujan_mm": 95},  {"bulan": "Jun", "curah_hujan_mm": 60},
        {"bulan": "Jul", "curah_hujan_mm": 45},  {"bulan": "Agu", "curah_hujan_mm": 30},
        {"bulan": "Sep", "curah_hujan_mm": 55},  {"bulan": "Okt", "curah_hujan_mm": 120},
        {"bulan": "Nov", "curah_hujan_mm": 200}, {"bulan": "Des", "curah_hujan_mm": 270},
    ]
    return _csv_response(data, ["bulan", "curah_hujan_mm"], "curah_hujan_bulanan.csv")


@main_bp.route("/export/banjir.csv")
@require_login
def export_banjir():
    data = [
        {"kecamatan": "Tempurejo",   "level": "tinggi", "skor": 82, "curah_hujan_mm": 1800, "elevasi_m": 50},
        {"kecamatan": "Wuluhan",     "level": "sedang", "skor": 68, "curah_hujan_mm": 1600, "elevasi_m": 25},
        {"kecamatan": "Puger",       "level": "sedang", "skor": 65, "curah_hujan_mm": 1550, "elevasi_m": 10},
        {"kecamatan": "Ambulu",      "level": "rendah", "skor": 45, "curah_hujan_mm": 1650, "elevasi_m": 30},
        {"kecamatan": "Bangsalsari", "level": "sedang", "skor": 62, "curah_hujan_mm": 1700, "elevasi_m": 150},
        {"kecamatan": "Tanggul",     "level": "sedang", "skor": 60, "curah_hujan_mm": 1600, "elevasi_m": 200},
        {"kecamatan": "Panti",       "level": "sedang", "skor": 58, "curah_hujan_mm": 1800, "elevasi_m": 250},
    ]
    return _csv_response(data,
        ["kecamatan", "level", "skor", "curah_hujan_mm", "elevasi_m"],
        "risiko_banjir.csv")


@main_bp.route("/export/kekeringan.csv")
@require_login
def export_kekeringan():
    data = [
        {"kecamatan": "Sumberjambe", "level": "tinggi", "skor": 76, "curah_hujan_mm": 1150, "elevasi_m": 500},
        {"kecamatan": "Silo",        "level": "tinggi", "skor": 74, "curah_hujan_mm": 1200, "elevasi_m": 250},
        {"kecamatan": "Ledokombo",   "level": "sedang", "skor": 60, "curah_hujan_mm": 1250, "elevasi_m": 400},
        {"kecamatan": "Sukowono",    "level": "sedang", "skor": 58, "curah_hujan_mm": 1200, "elevasi_m": 450},
        {"kecamatan": "Kalisat",     "level": "sedang", "skor": 52, "curah_hujan_mm": 1300, "elevasi_m": 350},
        {"kecamatan": "Jelbuk",      "level": "sedang", "skor": 50, "curah_hujan_mm": 1350, "elevasi_m": 380},
    ]
    return _csv_response(data,
        ["kecamatan", "level", "skor", "curah_hujan_mm", "elevasi_m"],
        "risiko_kekeringan.csv")


@main_bp.route("/export/komoditas.csv")
@require_login
def export_komoditas():
    data = [
        {"komoditas": "Padi",     "kategori": "Pangan",       "luas_tanam_ha": 96400, "produksi_ton": 582700, "produktivitas": 6.12},
        {"komoditas": "Jagung",   "kategori": "Pangan",       "luas_tanam_ha": 52100, "produksi_ton": 245600, "produktivitas": 4.79},
        {"komoditas": "Kedelai",  "kategori": "Pangan",       "luas_tanam_ha": 18700, "produksi_ton": 25800,  "produktivitas": 1.42},
        {"komoditas": "Cabai",    "kategori": "Hortikultura", "luas_tanam_ha": 3400,  "produksi_ton": 28400,  "produktivitas": 8.87},
        {"komoditas": "Tembakau", "kategori": "Perkebunan",   "luas_tanam_ha": 12800, "produksi_ton": 34900,  "produktivitas": 2.79},
        {"komoditas": "Kopi",     "kategori": "Perkebunan",   "luas_tanam_ha": 8200,  "produksi_ton": 4200,   "produktivitas": 0.53},
    ]
    return _csv_response(data,
        ["komoditas", "kategori", "luas_tanam_ha", "produksi_ton", "produktivitas"],
        "komoditas_pertanian.csv")


@main_bp.route("/export/neraca_air.csv")
@require_login
def export_neraca_air():
    data = [
        {"kecamatan": "Wuluhan",   "ketersediaan_juta_m3": 28.4, "kebutuhan_juta_m3": 24.2, "neraca_juta_m3": 4.2,  "status": "Surplus"},
        {"kecamatan": "Ambulu",    "ketersediaan_juta_m3": 22.6, "kebutuhan_juta_m3": 20.8, "neraca_juta_m3": 1.8,  "status": "Surplus"},
        {"kecamatan": "Patrang",   "ketersediaan_juta_m3": 32.8, "kebutuhan_juta_m3": 28.4, "neraca_juta_m3": 4.4,  "status": "Surplus"},
        {"kecamatan": "Rambipuji", "ketersediaan_juta_m3": 18.4, "kebutuhan_juta_m3": 19.2, "neraca_juta_m3": -0.8, "status": "Defisit"},
        {"kecamatan": "Balung",    "ketersediaan_juta_m3": 12.2, "kebutuhan_juta_m3": 14.8, "neraca_juta_m3": -2.6, "status": "Defisit"},
        {"kecamatan": "Puger",     "ketersediaan_juta_m3": 16.4, "kebutuhan_juta_m3": 15.6, "neraca_juta_m3": 0.8,  "status": "Surplus"},
        {"kecamatan": "Jenggawah", "ketersediaan_juta_m3": 14.2, "kebutuhan_juta_m3": 13.8, "neraca_juta_m3": 0.4,  "status": "Surplus"},
        {"kecamatan": "Tempurejo", "ketersediaan_juta_m3": 20.8, "kebutuhan_juta_m3": 18.4, "neraca_juta_m3": 2.4,  "status": "Surplus"},
    ]
    return _csv_response(data,
        ["kecamatan", "ketersediaan_juta_m3", "kebutuhan_juta_m3", "neraca_juta_m3", "status"],
        "neraca_air.csv")