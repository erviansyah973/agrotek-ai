"""
AGROTEK AI — Main Routes
========================
Landing, demo, peta, data center, modul, dan endpoint export CSV.
"""

import csv
import io
from flask import Blueprint, render_template, current_app, jsonify, Response
from app.auth_utils import require_login, current_user
from app import data_catalog as catalog

main_bp = Blueprint("main", __name__)


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

DISTRICTS = [
    {"id": 1,  "name": "Kencong",       "lat": -8.280, "lng": 113.380, "area_km2": 62.4,  "village_count": 5},
    {"id": 2,  "name": "Gumukmas",      "lat": -8.320, "lng": 113.420, "area_km2": 93.2,  "village_count": 8},
    {"id": 3,  "name": "Puger",         "lat": -8.300, "lng": 113.480, "area_km2": 142.6, "village_count": 12},
    {"id": 4,  "name": "Wuluhan",       "lat": -8.300, "lng": 113.550, "area_km2": 105.2, "village_count": 7},
    {"id": 5,  "name": "Ambulu",        "lat": -8.320, "lng": 113.620, "area_km2": 103.5, "village_count": 7},
    {"id": 6,  "name": "Tempurejo",     "lat": -8.350, "lng": 113.720, "area_km2": 210.4, "village_count": 8},
    {"id": 7,  "name": "Silo",          "lat": -8.200, "lng": 113.850, "area_km2": 206.3, "village_count": 9},
    {"id": 8,  "name": "Mayang",        "lat": -8.120, "lng": 113.800, "area_km2": 60.3,  "village_count": 7},
    {"id": 9,  "name": "Mumbulsari",    "lat": -8.150, "lng": 113.750, "area_km2": 56.8,  "village_count": 7},
    {"id": 10, "name": "Jenggawah",     "lat": -8.220, "lng": 113.680, "area_km2": 48.7,  "village_count": 8},
    {"id": 11, "name": "Ajung",         "lat": -8.200, "lng": 113.650, "area_km2": 40.2,  "village_count": 7},
    {"id": 12, "name": "Rambipuji",     "lat": -8.200, "lng": 113.600, "area_km2": 54.9,  "village_count": 8},
    {"id": 13, "name": "Balung",        "lat": -8.250, "lng": 113.550, "area_km2": 46.1,  "village_count": 8},
    {"id": 14, "name": "Umbulsari",     "lat": -8.200, "lng": 113.420, "area_km2": 65.4,  "village_count": 10},
    {"id": 15, "name": "Semboro",       "lat": -8.200, "lng": 113.380, "area_km2": 41.8,  "village_count": 6},
    {"id": 16, "name": "Jombang",       "lat": -8.180, "lng": 113.350, "area_km2": 45.9,  "village_count": 6},
    {"id": 17, "name": "Sumberbaru",    "lat": -8.100, "lng": 113.350, "area_km2": 132.7, "village_count": 10},
    {"id": 18, "name": "Tanggul",       "lat": -8.050, "lng": 113.420, "area_km2": 100.5, "village_count": 8},
    {"id": 19, "name": "Bangsalsari",   "lat": -8.100, "lng": 113.500, "area_km2": 88.3,  "village_count": 11},
    {"id": 20, "name": "Panti",         "lat": -8.080, "lng": 113.600, "area_km2": 96.4,  "village_count": 7},
    {"id": 21, "name": "Sukorambi",     "lat": -8.120, "lng": 113.680, "area_km2": 42.7,  "village_count": 5},
    {"id": 22, "name": "Arjasa",        "lat": -8.080, "lng": 113.720, "area_km2": 60.5,  "village_count": 6},
    {"id": 23, "name": "Pakusari",      "lat": -8.120, "lng": 113.750, "area_km2": 34.8,  "village_count": 7},
    {"id": 24, "name": "Kalisat",       "lat": -8.100, "lng": 113.800, "area_km2": 89.6,  "village_count": 12},
    {"id": 25, "name": "Ledokombo",     "lat": -8.080, "lng": 113.850, "area_km2": 105.8, "village_count": 10},
    {"id": 26, "name": "Sumberjambe",   "lat": -8.020, "lng": 113.850, "area_km2": 96.2,  "village_count": 9},
    {"id": 27, "name": "Sukowono",      "lat": -8.050, "lng": 113.780, "area_km2": 60.4,  "village_count": 12},
    {"id": 28, "name": "Jelbuk",        "lat": -8.050, "lng": 113.720, "area_km2": 51.6,  "village_count": 6},
    {"id": 29, "name": "Kaliwates",     "lat": -8.170, "lng": 113.700, "area_km2": 24.7,  "village_count": 7},
    {"id": 30, "name": "Sumbersari",    "lat": -8.170, "lng": 113.720, "area_km2": 32.5,  "village_count": 7},
    {"id": 31, "name": "Patrang",       "lat": -8.130, "lng": 113.700, "area_km2": 45.3,  "village_count": 8},
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


@main_bp.route("/peta")
def peta():
    return render_template("peta.html",
        app_name=current_app.config["APP_NAME"],
        app_subtitle=current_app.config["APP_SUBTITLE"],
        app_region=current_app.config["APP_REGION"],
        user=current_user(),
        is_logged_in=current_user() is not None)


# ------------------------------------------------------------
# JSON endpoints peta
# ------------------------------------------------------------
@main_bp.route("/peta/data/districts")
def data_districts():
    features = [{
        "type": "Feature",
        "properties": {"id": d["id"], "name": d["name"],
                       "area_km2": d["area_km2"], "village_count": d["village_count"]},
        "geometry": {"type": "Point", "coordinates": [d["lng"], d["lat"]]},
    } for d in DISTRICTS]
    return jsonify({"type": "FeatureCollection", "features": features})


@main_bp.route("/peta/data/rivers")
def data_rivers():
    return jsonify({"type": "FeatureCollection", "features": [
        {"type": "Feature", "properties": {"name": "Kali Bedadung", "class": "utama"},
         "geometry": {"type": "LineString", "coordinates": [
             [113.640, -8.050], [113.660, -8.120], [113.680, -8.170],
             [113.700, -8.230], [113.720, -8.280], [113.700, -8.350]]}},
        {"type": "Feature", "properties": {"name": "Kali Tanggul", "class": "sekunder"},
         "geometry": {"type": "LineString", "coordinates": [
             [113.420, -8.020], [113.450, -8.100], [113.480, -8.180],
             [113.500, -8.260], [113.490, -8.330]]}},
        {"type": "Feature", "properties": {"name": "Kali Mayang", "class": "sekunder"},
         "geometry": {"type": "LineString", "coordinates": [
             [113.800, -8.080], [113.790, -8.150], [113.780, -8.220],
             [113.760, -8.300], [113.740, -8.360]]}},
    ]})


@main_bp.route("/peta/data/irrigation")
def data_irrigation():
    return jsonify({"type": "FeatureCollection", "features": [
        {"type": "Feature", "properties": {"name": "Saluran Primer Bedadung", "type": "primer"},
         "geometry": {"type": "LineString", "coordinates": [
             [113.680, -8.120], [113.660, -8.160], [113.640, -8.200],
             [113.610, -8.240], [113.580, -8.270]]}},
        {"type": "Feature", "properties": {"name": "Saluran Sekunder Wuluhan", "type": "sekunder"},
         "geometry": {"type": "LineString", "coordinates": [
             [113.580, -8.270], [113.560, -8.290], [113.540, -8.300]]}},
    ]})


# ============================================================
# DATA CENTER
# ============================================================
@main_bp.route("/data")
@require_login
def data_center():
    return render_template("data.html",
        app_name=current_app.config["APP_NAME"],
        app_subtitle=current_app.config["APP_SUBTITLE"],
        app_region=current_app.config["APP_REGION"],
        user=current_user(),
        datasets=catalog.all_datasets(),
        categories=catalog.all_categories())


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
# EXPORT CSV (Reports)
# ============================================================
def _csv_response(rows, headers, filename):
    """Helper: build CSV response dari list of dict."""
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