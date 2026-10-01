/* ============================================================
   AGROTEK AI — Peta GIS (Leaflet)
   ============================================================ */
(function () {
    'use strict';

    if (typeof L === 'undefined') {
        console.error('[AGROTEK] Leaflet belum dimuat.');
        return;
    }

    const CFG = window.AGROTEK_MAP || {};
    const defaultCenter = CFG.center || [-8.1845, 113.6681];
    const defaultZoom = CFG.zoom || 10;

    /* -------------------- INIT MAP -------------------- */
    const map = L.map('map', {
        center: defaultCenter,
        zoom: defaultZoom,
        zoomControl: false,
        attributionControl: true,
    });

    L.control.zoom({ position: 'topright' }).addTo(map);
    L.control.scale({ position: 'bottomleft', imperial: false }).addTo(map);

    /* -------------------- BASEMAPS -------------------- */
    const basemaps = {
        osm: L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '&copy; OpenStreetMap contributors',
        }),
        satellite: L.tileLayer(
            'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            {
                maxZoom: 19,
                attribution: 'Tiles &copy; Esri, Maxar, Earthstar Geographics',
            }
        ),
        terrain: L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', {
            maxZoom: 17,
            attribution: 'Map data &copy; OpenStreetMap | Style &copy; OpenTopoMap',
        }),
        dark: L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
            maxZoom: 20,
            attribution: '&copy; OpenStreetMap contributors &copy; CARTO',
        }),
    };

    basemaps.osm.addTo(map);

    document.querySelectorAll('.basemap-btn').forEach(button => {
        button.addEventListener('click', () => {
            const key = button.dataset.basemap;
            if (!basemaps[key]) return;
            Object.values(basemaps).forEach(layer => map.removeLayer(layer));
            basemaps[key].addTo(map);
            document.querySelectorAll('.basemap-btn').forEach(item => {
                const isActive = item === button;
                item.classList.toggle('active', isActive);
                item.setAttribute('aria-pressed', String(isActive));
            });
        });
    });

    /* -------------------- STYLE DEFINITIONS -------------------- */
    const styleJemberRivers = {
        color: '#2563eb',
        weight: 2,
        opacity: 0.9,
    };

    const jemberBoundaryLayers = {
        jemberBoundaryKabupaten: {
            endpoint: 'kabupaten',
            style: { color: '#0f766e', weight: 3, opacity: 0.95, fillOpacity: 0.02 },
            nameField: 'NAME_2',
            typeField: 'TYPE_2',
            codeField: 'CC_2',
            label: 'batas Kabupaten Jember',
        },
        jemberBoundaryKecamatan: {
            endpoint: 'kecamatan',
            style: { color: '#0891b2', weight: 1.5, opacity: 0.8, fillOpacity: 0.01 },
            nameField: 'NAME_3',
            typeField: 'TYPE_3',
            codeField: 'CC_3',
            label: 'batas kecamatan',
        },
        jemberBoundaryDesa: {
            endpoint: 'desa',
            style: { color: '#64748b', weight: 0.7, opacity: 0.65, fillOpacity: 0.01 },
            nameField: 'NAME_4',
            typeField: 'TYPE_4',
            codeField: 'CC_4',
            label: 'batas desa/kelurahan',
        },
    };

    const epaksiStyles = {
        epaksiBuildings: {
            style: { color: '#ef4444' },
            pointToLayer: (feature, latlng) => L.circleMarker(latlng, {
                radius: 4,
                color: '#fff',
                weight: 1,
                fillColor: '#ef4444',
                fillOpacity: 0.9,
            }),
            label: 'bangunan irigasi',
            url: '/peta/data/epaksi/bangunan',
        },
        epaksiNetworks: {
            style: { color: '#f97316', weight: 2, opacity: 0.9 },
            label: 'jaringan saluran',
            url: '/peta/data/epaksi/jaringan',
        },
        epaksiParcels: {
            style: {
                color: '#22c55e',
                weight: 1,
                opacity: 0.85,
                fillColor: '#22c55e',
                fillOpacity: 0.12,
            },
            label: 'petak irigasi',
            url: '/peta/data/epaksi/petak',
        },
    };

    /* -------------------- BINDERS -------------------- */
    function bindJemberRiver(feature, layer) {
        const properties = feature.properties || {};
        const popup = document.createElement('div');
        const title = document.createElement('div');
        title.className = 'popup-title';
        title.textContent = properties.NAMOBJ || 'Sungai';
        popup.append(title);

        [
            ['Keterangan', properties.REMARK],
            ['Kode unsur', properties.FCODE],
        ].forEach(([label, value]) => {
            if (!value) return;
            const row = document.createElement('div');
            row.className = 'popup-row';
            const rowLabel = document.createElement('span');
            const rowValue = document.createElement('span');
            rowLabel.textContent = label;
            rowValue.textContent = value;
            row.append(rowLabel, rowValue);
            popup.append(row);
        });

        layer.bindPopup(popup);
    }

    function bindJemberBoundary(config, feature, layer) {
        const properties = feature.properties || {};
        const popup = document.createElement('div');
        const title = document.createElement('div');
        title.className = 'popup-title';
        title.textContent = properties[config.nameField] || 'Batas wilayah';
        popup.append(title);

        [
            ['Jenis wilayah', properties[config.typeField]],
            ['Kode wilayah', properties[config.codeField]],
        ].forEach(([label, value]) => {
            if (!value) return;
            const row = document.createElement('div');
            row.className = 'popup-row';
            const rowLabel = document.createElement('span');
            const rowValue = document.createElement('span');
            rowLabel.textContent = label;
            rowValue.textContent = value;
            row.append(rowLabel, rowValue);
            popup.append(row);
        });

        layer.bindPopup(popup);
    }

    function bindEpaksiAsset(feature, layer) {
        const properties = feature.properties || {};
        const popup = document.createElement('div');
        const title = document.createElement('div');
        title.className = 'popup-title';
        title.textContent = properties.nama || properties.jenis_aset || 'Aset irigasi';
        popup.append(title);

        [
            ['Daerah irigasi', properties.daerah_irigasi],
            ['Jenis aset', properties.jenis_aset],
            ['Nomenklatur', properties.nomenklatur],
            ['Saluran', properties.saluran],
            ['Panjang', properties.panjang],
            ['Luas layanan', properties.luas_layanan],
        ].forEach(([label, value]) => {
            if (!value) return;
            const row = document.createElement('div');
            row.className = 'popup-row';
            const rowLabel = document.createElement('span');
            const rowValue = document.createElement('span');
            rowLabel.textContent = label;
            rowValue.textContent = value;
            row.append(rowLabel, rowValue);
            popup.append(row);
        });

        layer.bindPopup(popup);
    }

    /* -------------------- LAYER STORAGE -------------------- */
    const activeLayers = {};
    const epaksiLoads = {};
    const boundaryLoads = {};
    let jemberRiversLoad = null;
    const districtData = { features: [] };

    function registerLayer(name, layer) {
        activeLayers[name] = layer;
        const checkbox = document.querySelector(`input[data-layer="${name}"]`);
        if (checkbox && checkbox.checked) layer.addTo(map);
        return layer;
    }

    /* -------------------- LOAD LAYERS -------------------- */
    function loadJemberRivers() {
        if (activeLayers.jemberRivers) {
            activeLayers.jemberRivers.addTo(map);
            return Promise.resolve(activeLayers.jemberRivers);
        }
        if (jemberRiversLoad) return jemberRiversLoad;

        const status = document.getElementById('jemberRiversStatus');
        if (status) status.textContent = 'Memuat data sungai Jember...';

        jemberRiversLoad = fetch('/peta/data/rivers/jember')
            .then(response => {
                if (!response.ok) throw new Error(`HTTP ${response.status}`);
                return response.json();
            })
            .then(geojson => {
                if (geojson.type !== 'FeatureCollection' || !Array.isArray(geojson.features)) {
                    throw new Error('Format GeoJSON tidak valid');
                }
                const layer = L.geoJSON(geojson, {
                    onEachFeature: bindJemberRiver,
                    style: styleJemberRivers,
                });
                registerLayer('jemberRivers', layer);
                if (status) {
                    status.textContent = `${geojson.features.length.toLocaleString('id-ID')} fitur sungai Jember dimuat.`;
                }
                return layer;
            })
            .catch(error => {
                console.error('[AGROTEK] Gagal memuat sungai Jember:', error);
                if (status) status.textContent = 'Gagal memuat sungai Jember. Matikan lalu aktifkan lagi untuk mencoba ulang.';
                return null;
            })
            .finally(() => {
                jemberRiversLoad = null;
            });

        return jemberRiversLoad;
    }

    function loadJemberBoundary(name) {
        const config = jemberBoundaryLayers[name];
        if (!config) return Promise.resolve(null);
        if (activeLayers[name]) {
            activeLayers[name].addTo(map);
            return Promise.resolve(activeLayers[name]);
        }
        if (boundaryLoads[name]) return boundaryLoads[name];

        const status = document.getElementById('jemberBoundaryStatus');
        if (status) status.textContent = `Memuat ${config.label}...`;

        boundaryLoads[name] = fetch(`/peta/data/boundaries/jember/${config.endpoint}`)
            .then(response => {
                if (!response.ok) throw new Error(`HTTP ${response.status}`);
                return response.json();
            })
            .then(geojson => {
                if (geojson.type !== 'FeatureCollection' || !Array.isArray(geojson.features)) {
                    throw new Error('Format GeoJSON tidak valid');
                }
                if (name === 'jemberBoundaryKecamatan') {
                    districtData.features = geojson.features;
                }
                const layer = L.geoJSON(geojson, {
                    onEachFeature: (feature, featureLayer) => bindJemberBoundary(config, feature, featureLayer),
                    style: config.style,
                });
                registerLayer(name, layer);
                if (status) status.textContent = `${geojson.features.length.toLocaleString('id-ID')} fitur ${config.label} dimuat. Batas GADM 4.1 bukan batas legal.`;
                return layer;
            })
            .catch(error => {
                console.error(`[AGROTEK] Gagal memuat ${config.label}:`, error);
                if (status) status.textContent = `Gagal memuat ${config.label}. Matikan lalu aktifkan lagi untuk mencoba ulang.`;
                return null;
            })
            .finally(() => {
                delete boundaryLoads[name];
            });

        return boundaryLoads[name];
    }

    function loadEpaksiLayer(name) {
        if (activeLayers[name]) {
            activeLayers[name].addTo(map);
            return Promise.resolve(activeLayers[name]);
        }
        if (epaksiLoads[name]) return epaksiLoads[name];

        const config = epaksiStyles[name];
        const status = document.getElementById('epaksiLayerStatus');
        if (!config) return Promise.resolve(null);
        if (status) status.textContent = `Memuat ${config.label}...`;

        epaksiLoads[name] = fetch(config.url)
            .then(response => {
                if (!response.ok) throw new Error(`HTTP ${response.status}`);
                return response.json();
            })
            .then(geojson => {
                if (geojson.type !== 'FeatureCollection' || !Array.isArray(geojson.features)) {
                    throw new Error('Format GeoJSON tidak valid');
                }
                const layer = L.geoJSON(geojson, {
                    onEachFeature: bindEpaksiAsset,
                    style: config.style,
                    pointToLayer: config.pointToLayer,
                });
                registerLayer(name, layer);
                if (status) status.textContent = `Layer ${config.label} berhasil dimuat.`;
                return layer;
            })
            .catch(error => {
                console.error(`[AGROTEK] Gagal memuat ${config.label}:`, error);
                if (status && error.message === 'HTTP 403') {
                    status.textContent = `Akses ${config.label} ditolak (HTTP 403). Muat ulang dan masuk kembali sebagai admin.`;
                } else if (status) {
                    status.textContent = `Gagal memuat ${config.label}. Matikan lalu aktifkan lagi untuk mencoba ulang.`;
                }
                return null;
            })
            .finally(() => {
                delete epaksiLoads[name];
            });

        return epaksiLoads[name];
    }

    /* -------------------- LAYER TOGGLE -------------------- */
    document.querySelectorAll('.layer-item input[data-layer]:checked').forEach(cb => {
        if (jemberBoundaryLayers[cb.dataset.layer]) loadJemberBoundary(cb.dataset.layer);
    });

    document.querySelectorAll('.layer-item input[data-layer]').forEach(cb => {
        cb.addEventListener('change', () => {
            const name = cb.dataset.layer;
            const layer = activeLayers[name];
            if (!cb.checked) {
                if (layer) map.removeLayer(layer);
                return;
            }
            if (layer) {
                layer.addTo(map);
                return;
            }
            if (name === 'jemberRivers') {
                loadJemberRivers();
                return;
            }
            if (jemberBoundaryLayers[name]) {
                loadJemberBoundary(name);
                return;
            }
            if (epaksiStyles[name]) loadEpaksiLayer(name);
        });
    });

    /* -------------------- SEARCH -------------------- */
    const searchInput = document.getElementById('searchInput');
    const searchResults = document.getElementById('searchResults');

    if (searchInput && searchResults) {
        searchInput.addEventListener('input', () => {
            const q = searchInput.value.toLowerCase().trim();
            searchResults.innerHTML = '';

            if (!q) return;

            const nameField = jemberBoundaryLayers.jemberBoundaryKecamatan.nameField;
            const matches = districtData.features
                .filter(f => (f.properties?.[nameField] || '').toLowerCase().includes(q))
                .slice(0, 8);

            matches.forEach(f => {
                const li = document.createElement('li');
                const name = f.properties[nameField];
                li.textContent = name;
                li.addEventListener('click', () => {
                    const bounds = L.geoJSON(f).getBounds();
                    if (bounds.isValid()) {
                        map.flyToBounds(bounds, { padding: [30, 30], maxZoom: 14, duration: 0.8 });
                    }
                    searchResults.innerHTML = '';
                    searchInput.value = name;
                });
                searchResults.appendChild(li);
            });
        });
    }

    /* -------------------- COORDINATE + ZOOM -------------------- */
    const coordEl = document.getElementById('coordDisplay');
    const zoomEl = document.getElementById('zoomDisplay');

    function updateCoords(e) {
        if (coordEl && e && e.latlng) {
            const { lat, lng } = e.latlng;
            coordEl.textContent = `${lat.toFixed(5)}, ${lng.toFixed(5)}`;
        }
    }

    function updateZoom() {
        if (zoomEl) zoomEl.textContent = 'z' + map.getZoom();
    }

    map.on('mousemove', updateCoords);
    map.on('zoomend', updateZoom);
    updateZoom();

    /* -------------------- LOCATE -------------------- */
    const btnLocate = document.getElementById('btnLocate');
    if (btnLocate) {
        btnLocate.addEventListener('click', () => {
            map.locate({ setView: true, maxZoom: 14 });
        });
    }

    let locMarker = null;
    map.on('locationfound', (e) => {
        if (locMarker) map.removeLayer(locMarker);
        locMarker = L.circleMarker(e.latlng, {
            radius: 8,
            color: '#10b981',
            fillColor: '#10b981',
            fillOpacity: 0.5,
            weight: 2,
        }).addTo(map).bindPopup('Lokasi Anda').openPopup();
    });

    map.on('locationerror', () => {
        alert('Tidak dapat mengakses lokasi. Pastikan GPS/izin lokasi aktif.');
    });

    /* -------------------- RESET -------------------- */
    const btnReset = document.getElementById('btnReset');
    if (btnReset) {
        btnReset.addEventListener('click', () => {
            map.flyTo(defaultCenter, defaultZoom, { duration: 0.8 });
        });
    }

    /* -------------------- SIDEBAR TOGGLE (mobile) -------------------- */
    const btnSideToggle = document.getElementById('btnSideToggle');
    const side = document.getElementById('petaSide');

    if (btnSideToggle && side) {
        btnSideToggle.addEventListener('click', () => {
            side.classList.toggle('open');
        });
    }

    /* -------------------- INVALIDATE ON RESIZE -------------------- */
    window.addEventListener('resize', () => {
        map.invalidateSize();
    });

    console.log('[AGROTEK] Peta siap.');
})();