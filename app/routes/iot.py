"""
AGROTEK AI — IoT Ready
=======================
Halaman /iot: monitoring device IoT + endpoint untuk ingest data sensor.
Arsitektur siap menerima sensor fisik di masa depan.

Alur:
Sensor → Gateway → API /api/iot/ingest → DB → Dashboard → AI
"""

from flask import Blueprint, render_template, current_app, jsonify, request
from app.auth_utils import require_login, current_user
from datetime import datetime

iot_bp = Blueprint("iot", __name__)


# ============================================================
# DEVICE TERDAFTAR (DEMO)
# ============================================================
DEVICES = [
    {"code": "AWLR-BDD-01",   "name": "AWLR Bedadung",           "type": "water_level",   "kecamatan": "Patrang",   "status": "online",  "battery": 87, "last_seen": "2 menit lalu"},
    {"code": "AWLR-WLH-01",   "name": "AWLR Wuluhan",            "type": "water_level",   "kecamatan": "Wuluhan",   "status": "online",  "battery": 92, "last_seen": "1 menit lalu"},
    {"code": "ARR-JGW-01",    "name": "Pos Hujan Jenggawah",     "type": "rain_gauge",    "kecamatan": "Jenggawah", "status": "online",  "battery": 78, "last_seen": "5 menit lalu"},
    {"code": "ARR-AMB-01",    "name": "Pos Hujan Ambulu",        "type": "rain_gauge",    "kecamatan": "Ambulu",    "status": "online",  "battery": 81, "last_seen": "3 menit lalu"},
    {"code": "AWS-SIL-01",    "name": "AWS Silo",                "type": "weather_station","kecamatan": "Silo",     "status": "offline", "battery": 12, "last_seen": "6 jam lalu"},
    {"code": "SM-TNH-A01",    "name": "Sensor Tanah Blok A1",    "type": "soil_moisture", "kecamatan": "Wuluhan",   "status": "online",  "battery": 65, "last_seen": "1 menit lalu"},
    {"code": "SM-TNH-A02",    "name": "Sensor Tanah Blok A2",    "type": "soil_moisture", "kecamatan": "Wuluhan",   "status": "online",  "battery": 71, "last_seen": "2 menit lalu"},
    {"code": "SM-TNH-B01",    "name": "Sensor Tanah Blok B1",    "type": "soil_moisture", "kecamatan": "Ambulu",    "status": "warning", "battery": 34, "last_seen": "15 menit lalu"},
]

# ============================================================
# PEMBACAAN SENSOR TERKINI (DEMO - realtime)
# ============================================================
LATEST_READINGS = [
    {"device_code": "AWLR-BDD-01", "parameter": "water_level",  "value": 182,  "unit": "cm",    "time": "08:00", "quality": "good"},
    {"device_code": "AWLR-WLH-01", "parameter": "water_level",  "value": 215,  "unit": "cm",    "time": "08:05", "quality": "good"},
    {"device_code": "ARR-JGW-01",  "parameter": "rainfall",     "value": 12,   "unit": "mm",    "time": "08:10", "quality": "good"},
    {"device_code": "ARR-AMB-01",  "parameter": "rainfall",     "value": 8,    "unit": "mm",    "time": "08:12", "quality": "good"},
    {"device_code": "SM-TNH-A01",  "parameter": "soil_moisture","value": 38,   "unit": "%",     "time": "08:15", "quality": "good"},
    {"device_code": "SM-TNH-A02",  "parameter": "soil_moisture","value": 45,   "unit": "%",     "time": "08:15", "quality": "good"},
    {"device_code": "SM-TNH-B01",  "parameter": "soil_moisture","value": 28,   "unit": "%",     "time": "08:14", "quality": "suspect"},
]

# Tipe device + label
DEVICE_TYPES = {
    "water_level":     {"label": "Water Level",     "icon": "🌊", "color": "sky"},
    "rain_gauge":      {"label": "Rain Gauge",      "icon": "🌧️", "color": "cyan"},
    "weather_station": {"label": "Weather Station", "icon": "🌤️", "color": "amber"},
    "soil_moisture":   {"label": "Soil Moisture",   "icon": "🌱", "color": "emerald"},
}


# ============================================================
# ROUTES
# ============================================================
@iot_bp.route("/iot")
@require_login
def index():
    # KPI
    total_device = len(DEVICES)
    online_count = sum(1 for d in DEVICES if d["status"] == "online")
    offline_count = sum(1 for d in DEVICES if d["status"] == "offline")
    warning_count = sum(1 for d in DEVICES if d["status"] == "warning")

    # Per tipe
    per_tipe = {}
    for d in DEVICES:
        t = d["type"]
        per_tipe[t] = per_tipe.get(t, 0) + 1

    return render_template(
        "iot.html",
        app_name=current_app.config["APP_NAME"],
        app_subtitle=current_app.config["APP_SUBTITLE"],
        app_region=current_app.config["APP_REGION"],
        user=current_user(),
        devices=DEVICES,
        readings=LATEST_READINGS,
        device_types=DEVICE_TYPES,
        kpi={
            "total": total_device,
            "online": online_count,
            "offline": offline_count,
            "warning": warning_count,
        },
        per_tipe=per_tipe,
    )


@iot_bp.route("/iot/data/devices")
def data_devices():
    """Endpoint JSON: daftar device."""
    return jsonify({
        "total": len(DEVICES),
        "devices": DEVICES,
    })


@iot_bp.route("/iot/data/readings")
def data_readings():
    """Endpoint JSON: pembacaan terbaru (bisa di-polling oleh JS)."""
    return jsonify({
        "count": len(LATEST_READINGS),
        "readings": LATEST_READINGS,
        "timestamp": datetime.now().isoformat(),
    })


# ============================================================
# API INGEST — untuk sensor fisik di masa depan
# ============================================================
@iot_bp.route("/api/iot/ingest", methods=["POST"])
def ingest():
    """
    Endpoint untuk menerima data dari gateway IoT.

    Body JSON:
    {
        "device_code": "AWLR-BDD-01",
        "parameter": "water_level",
        "value": 185.5,
        "unit": "cm",
        "timestamp": "2026-09-15T08:00:00"
    }

    NOTE: Belum autentikasi — tambahkan token di FASE 15.
    Data belum disimpan ke DB — tabel iot.sensor_readings sudah ada
    di model, tapi migrasi ke PostGIS dilakukan nanti.
    """
    data = request.get_json(silent=True) or {}

    device_code = (data.get("device_code") or "").strip()
    parameter = (data.get("parameter") or "").strip()
    value = data.get("value")
    unit = (data.get("unit") or "").strip()

    # Validasi
    errors = []
    if not device_code:
        errors.append("device_code wajib")
    if not parameter:
        errors.append("parameter wajib")
    if value is None:
        errors.append("value wajib")
    if errors:
        return jsonify({
            "ok": False,
            "error": "Validasi gagal",
            "details": errors,
        }), 400

    # Cek device terdaftar
    device = next((d for d in DEVICES if d["code"] == device_code), None)
    if not device:
        return jsonify({
            "ok": False,
            "error": f"Device '{device_code}' tidak terdaftar",
        }), 404

    # Simulasi: simpan ke log (di masa depan → DB)
    try:
        from app.models import Log
        from app.extensions import db

        log = Log(
            level="info",
            source="iot-ingest",
            message=f"Ingest: {device_code} {parameter} = {value} {unit}",
        )
        db.session.add(log)
        db.session.commit()
    except Exception:
        pass

    return jsonify({
        "ok": True,
        "received": {
            "device_code": device_code,
            "parameter": parameter,
            "value": value,
            "unit": unit,
        },
        "message": "Data sensor diterima. Akan diproses lebih lanjut.",
        "note": "Endpoint placeholder — penyimpanan ke DB akan diaktifkan di fase berikutnya.",
    })


@iot_bp.route("/api/iot/status")
def api_status():
    """Endpoint untuk cek apakah IoT server sudah aktif."""
    return jsonify({
        "ok": True,
        "service": "AGROTEK IoT Gateway",
        "version": "v0.1-placeholder",
        "status": "ready",
        "endpoints": {
            "ingest": "/api/iot/ingest",
            "devices": "/iot/data/devices",
            "readings": "/iot/data/readings",
        },
        "timestamp": datetime.now().isoformat(),
    })