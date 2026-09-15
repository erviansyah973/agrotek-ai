"""
AGROTEK AI — Katalog Dataset
============================
Sumber tunggal untuk semua dataset di Data Center.
Nanti bisa di-upgrade ambil dari DB (tabel dataset_catalog).
"""

DATASETS = [
    {
        "slug": "batas-kecamatan-jember",
        "name": "Batas Administrasi Kecamatan",
        "desc": "Batas wilayah 31 kecamatan Kabupaten Jember. Referensi utama untuk agregasi statistik per wilayah.",
        "category": "administrasi",
        "category_label": "Administrasi",
        "source": "BIG / BPS",
        "year": 2024,
        "format": "GeoJSON",
        "resolution": "1:25.000",
        "license": "CC-BY-4.0",
        "status": "PUBLIC",
        "preview": "/peta",
        "keywords": ["batas", "kecamatan", "administrasi", "wilayah"],
    },
    {
        "slug": "jaringan-sungai",
        "name": "Jaringan Sungai",
        "desc": "Jaringan sungai utama dan sekunder di wilayah Kabupaten Jember.",
        "category": "hidrologi",
        "category_label": "Hidrologi",
        "source": "PUPR",
        "year": 2023,
        "format": "GeoJSON",
        "resolution": "1:50.000",
        "license": "CC-BY-4.0",
        "status": "PUBLIC",
        "preview": "/peta",
        "keywords": ["sungai", "hidrologi", "DAS"],
    },
    {
        "slug": "jaringan-irigasi",
        "name": "Jaringan Irigasi",
        "desc": "Saluran irigasi primer, sekunder, tersier, dan bangunan air (bendung, pintu air).",
        "category": "irigasi",
        "category_label": "Irigasi",
        "source": "Dinas PUPR",
        "year": 2023,
        "format": "GeoJSON",
        "resolution": "1:25.000",
        "license": "CC-BY-4.0",
        "status": "PUBLIC",
        "preview": "/peta",
        "keywords": ["irigasi", "saluran", "bendung"],
    },
    {
        "slug": "lahan-pertanian",
        "name": "Lahan Pertanian",
        "desc": "Peta penggunaan lahan pertanian: sawah, tegalan, dan perkebunan Kabupaten Jember.",
        "category": "pertanian",
        "category_label": "Pertanian",
        "source": "Dinas Pertanian",
        "year": 2023,
        "format": "Shapefile",
        "resolution": "1:25.000",
        "license": "Terbatas",
        "status": "RESTRICTED",
        "preview": None,
        "keywords": ["lahan", "pertanian", "sawah"],
    },
    {
        "slug": "risiko-banjir",
        "name": "Risiko Banjir",
        "desc": "Peta tingkat risiko banjir per kecamatan berdasarkan analisis multi-parameter (curah hujan, elevasi, slope, tutupan lahan).",
        "category": "analisis",
        "category_label": "Analisis Spasial",
        "source": "Hasil Analisis AGROTEK AI",
        "year": 2024,
        "format": "GeoJSON",
        "resolution": "Kecamatan",
        "license": "Internal",
        "status": "INTERNAL",
        "preview": None,
        "keywords": ["banjir", "risiko", "mitigasi"],
    },
    {
        "slug": "risiko-kekeringan",
        "name": "Risiko Kekeringan",
        "desc": "Peta tingkat risiko kekeringan per kecamatan berdasarkan analisis multi-parameter.",
        "category": "analisis",
        "category_label": "Analisis Spasial",
        "source": "Hasil Analisis AGROTEK AI",
        "year": 2024,
        "format": "GeoJSON",
        "resolution": "Kecamatan",
        "license": "Internal",
        "status": "INTERNAL",
        "preview": None,
        "keywords": ["kekeringan", "risiko", "air"],
    },
    {
        "slug": "ndvi-sentinel2",
        "name": "NDVI Sentinel-2",
        "desc": "Time-series NDVI (Normalized Difference Vegetation Index) dari citra Sentinel-2 untuk monitoring kesehatan tanaman.",
        "category": "remote-sensing",
        "category_label": "Remote Sensing",
        "source": "ESA Copernicus",
        "year": 2024,
        "format": "GeoTIFF",
        "resolution": "10 m",
        "license": "CC-BY-SA",
        "status": "PUBLIC",
        "preview": None,
        "keywords": ["NDVI", "Sentinel", "vegetasi", "remote sensing"],
    },
    {
        "slug": "curah-hujan-bulanan",
        "name": "Curah Hujan Bulanan",
        "desc": "Data curah hujan bulanan dari stasiun BMKG dan pos hujan di Kabupaten Jember.",
        "category": "hidrologi",
        "category_label": "Hidrologi",
        "source": "BMKG",
        "year": 2024,
        "format": "CSV",
        "resolution": "Stasiun",
        "license": "Publik",
        "status": "PUBLIC",
        "preview": "/hidrologi",
        "keywords": ["curah hujan", "iklim", "time-series"],
    },
    {
        "slug": "komoditas-pertanian",
        "name": "Komoditas Pertanian",
        "desc": "Data statistik komoditas pertanian: luas tanam, luas panen, produksi, dan produktivitas per kecamatan.",
        "category": "pertanian",
        "category_label": "Pertanian",
        "source": "BPS / Dinas Pertanian",
        "year": 2024,
        "format": "CSV",
        "resolution": "Kecamatan",
        "license": "Publik",
        "status": "PUBLIC",
        "preview": "/statistik",
        "keywords": ["komoditas", "produksi", "padi", "jagung"],
    },
    {
        "slug": "dem-slope",
        "name": "DEM & Slope",
        "desc": "Digital Elevation Model (DEM) dan turunan slope untuk analisis kesesuaian lahan dan risiko.",
        "category": "analisis",
        "category_label": "Analisis Spasial",
        "source": "DEMNAS / BIG",
        "year": 2023,
        "format": "GeoTIFF",
        "resolution": "8 m",
        "license": "CC-BY-4.0",
        "status": "PUBLIC",
        "preview": None,
        "keywords": ["DEM", "elevasi", "slope", "kemiringan"],
    },
]


def all_datasets() -> list:
    return DATASETS


def get_dataset(slug: str):
    for d in DATASETS:
        if d["slug"] == slug:
            return d
    return None


def get_by_category(cat: str) -> list:
    if cat == "all":
        return DATASETS
    return [d for d in DATASETS if d["category"] == cat]


def all_categories() -> list:
    seen = {}
    for d in DATASETS:
        c = d["category"]
        if c not in seen:
            seen[c] = d["category_label"]
    return [{"key": k, "label": v} for k, v in seen.items()]