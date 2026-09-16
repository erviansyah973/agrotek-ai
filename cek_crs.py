import shapefile

SHP = r"D:\DAS_BEDADUNG_WEBGIS\01_data_mentah\hidrologi\sungai\SHP Sungai Seluruh Indonesia [Lapak GIS.com]\Sungai Line 25K (124).shp"

# Baca header saja (cepat)
sf = shapefile.Reader(SHP, encoding="utf-8")
print("Total fitur:", len(sf))
print()

# Baca beberapa shape spesifik (tidak semua)
for idx in [0, 100, 1000, 10000, 50000, 100000]:
    try:
        shape = sf.shape(idx)
        print(f"Bbox #{idx}: {shape.bbox}")
    except Exception as e:
        print(f"Bbox #{idx}: ERROR - {e}")

print()
print("Nama field:", [f[0] for f in sf.fields[1:]])