"""
Konversi SHP (EPSG:3857) -> GeoJSON (WGS84), filter Jember
Dengan SIMPLIFY untuk sungai (agar ringan di browser)
"""

import shapefile
import json
import os
import math

JEMBER_BBOX_WGS84 = (113.30, -8.50, 114.00, -7.90)


def wgs84_to_mercator(lng, lat):
    x = lng * 20037508.34 / 180
    y = math.log(math.tan((90 + lat) * math.pi / 360)) / (math.pi / 180)
    y = y * 20037508.34 / 180
    return x, y


def mercator_to_wgs84(x, y):
    lng = (x / 20037508.34) * 180
    lat = (y / 20037508.34) * 180
    lat = 180 / math.pi * (2 * math.atan(math.exp(lat * math.pi / 180)) - math.pi / 2)
    return round(lng, 6), round(lat, 6)


MIN_LNG, MIN_LAT, MAX_LNG, MAX_LAT = JEMBER_BBOX_WGS84
JEMBER_BBOX_MERC = (
    *wgs84_to_mercator(MIN_LNG, MIN_LAT),
    *wgs84_to_mercator(MAX_LNG, MAX_LAT),
)


def simplify_line(points, tolerance=50):
    """Simplify LineString dengan Douglas-Peucker (tolerance dalam meter Mercator)."""
    if len(points) <= 2:
        return points

    # Cari titik terjauh dari garis awal-akhir
    start, end = points[0], points[-1]
    max_dist = 0
    max_idx = 0

    for i in range(1, len(points) - 1):
        p = points[i]
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        if dx == 0 and dy == 0:
            dist = math.hypot(p[0] - start[0], p[1] - start[1])
        else:
            t = ((p[0] - start[0]) * dx + (p[1] - start[1]) * dy) / (dx * dx + dy * dy)
            t = max(0, min(1, t))
            proj_x = start[0] + t * dx
            proj_y = start[1] + t * dy
            dist = math.hypot(p[0] - proj_x, p[1] - proj_y)
        if dist > max_dist:
            max_dist = dist
            max_idx = i

    if max_dist > tolerance:
        left = simplify_line(points[:max_idx + 1], tolerance)
        right = simplify_line(points[max_idx:], tolerance)
        return left[:-1] + right
    else:
        return [start, end]


def convert_geometry(geom, tolerance=0):
    """Konversi geometri 3857 -> 4326. tolerance=0 artinya tidak simplify."""
    gtype = geom["type"]
    coords = geom["coordinates"]

    if gtype == "Point":
        return {"type": "Point", "coordinates": list(mercator_to_wgs84(*coords))}

    elif gtype == "LineString":
        if tolerance > 0:
            coords = simplify_line(coords, tolerance)
        return {"type": "LineString", "coordinates": [
            list(mercator_to_wgs84(x, y)) for x, y in coords
        ]}

    elif gtype == "Polygon":
        return {"type": "Polygon", "coordinates": [
            [list(mercator_to_wgs84(x, y)) for x, y in ring] for ring in coords
        ]}

    elif gtype == "MultiPoint":
        return {"type": "MultiPoint", "coordinates": [
            list(mercator_to_wgs84(x, y)) for x, y in coords
        ]}

    elif gtype == "MultiLineString":
        return {"type": "MultiLineString", "coordinates": [
            [list(mercator_to_wgs84(x, y)) for x, y in
             (simplify_line(line, tolerance) if tolerance > 0 else line)]
            for line in coords
        ]}

    elif gtype == "MultiPolygon":
        return {"type": "MultiPolygon", "coordinates": [
            [[list(mercator_to_wgs84(x, y)) for x, y in ring] for ring in poly]
            for poly in coords
        ]}

    return geom


def shp_to_geojson(shp_path, output_path, bbox_merc, nama="",
                   max_features=5000, tolerance=0):
    """Convert SHP + simplify."""

    print(f"\n=== Proses: {nama} ===")
    print(f"Tolerance: {tolerance} m")

    if not os.path.exists(shp_path):
        print(f"[X] File tidak ada")
        return False

    sf = None
    for enc in ["utf-8", "latin1", "cp1252"]:
        try:
            sf = shapefile.Reader(shp_path, encoding=enc)
            print(f"[OK] Encoding: {enc}")
            break
        except Exception:
            continue

    if sf is None:
        print(f"[X] Gagal baca SHP")
        return False

    xmin, ymin, xmax, ymax = bbox_merc
    features = []
    total = len(sf)
    skipped = 0

    for i, shapeRec in enumerate(sf.iterShapeRecords()):
        if i % 10000 == 0 and i > 0:
            print(f"  ... {i}/{total} | lolos: {len(features)}")

        try:
            sbbox = shapeRec.shape.bbox

            if sbbox[2] < xmin or sbbox[0] > xmax:
                skipped += 1
                continue
            if sbbox[3] < ymin or sbbox[1] > ymax:
                skipped += 1
                continue

            try:
                props = shapeRec.record.as_dict()
            except Exception:
                fields = [f[0] for f in sf.fields[1:]]
                props = dict(zip(fields, shapeRec.record))

            clean_props = {}
            for k, v in props.items():
                if isinstance(v, bytes):
                    try:
                        clean_props[k] = v.decode("utf-8", errors="ignore")
                    except Exception:
                        clean_props[k] = str(v)
                elif hasattr(v, "isoformat"):
                    clean_props[k] = v.isoformat()
                else:
                    clean_props[k] = v

            geom_3857 = shapeRec.shape.__geo_interface__
            geom_4326 = convert_geometry(geom_3857, tolerance)

            features.append({
                "type": "Feature",
                "properties": clean_props,
                "geometry": geom_4326,
            })

            if len(features) >= max_features:
                break

        except Exception:
            skipped += 1
            continue

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    geojson = {"type": "FeatureCollection", "features": features}

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(geojson, f, ensure_ascii=False)

    size_kb = os.path.getsize(output_path) / 1024
    size_mb = size_kb / 1024
    print(f"[OK] Output : {output_path}")
    print(f"[OK] Fitur  : {len(features)} (dari {total})")
    print(f"[OK] Ukuran : {size_mb:.2f} MB")

    return True


SUNGAI_SHP = r"D:\DAS_BEDADUNG_WEBGIS\01_data_mentah\hidrologi\sungai\SHP Sungai Seluruh Indonesia [Lapak GIS.com]\Sungai Line 25K (124).shp"
DAS_SHP = r"D:\DAS_BEDADUNG_WEBGIS\01_data_mentah\hidrologi\das\[LapakGIS.com] DAS INDONESIA\Watershed Boundaries.shp"
IRIGASI_SHP = r"D:\DAS_BEDADUNG_WEBGIS\01_data_mentah\hidrologi\Fitur Hidrografi (Selain Sungai)\IRIGASI (131)\Irigasi 25K (132).shp"

OUTPUT_DIR = r"D:\agrotek_bersih\static\data"


if __name__ == "__main__":
    print("=" * 60)
    print("  KONVERSI SHP -> GEOJSON + SIMPLIFY")
    print("=" * 60)

    # Sungai: tolerance 200m, max 2000 fitur
    shp_to_geojson(SUNGAI_SHP,
                   os.path.join(OUTPUT_DIR, "sungai_jember.geojson"),
                   JEMBER_BBOX_MERC, "Sungai",
                   max_features=2000, tolerance=200)

    # DAS: tanpa simplify (poligon, sudah ringan)
    shp_to_geojson(DAS_SHP,
                   os.path.join(OUTPUT_DIR, "das_jember.geojson"),
                   JEMBER_BBOX_MERC, "DAS",
                   max_features=1000, tolerance=0)

    # Irigasi: simplify ringan
    shp_to_geojson(IRIGASI_SHP,
                   os.path.join(OUTPUT_DIR, "irigasi_jember.geojson"),
                   JEMBER_BBOX_MERC, "Irigasi",
                   max_features=1000, tolerance=100)

    print("\n" + "=" * 60)
    print("  SELESAI!")
    print("=" * 60)