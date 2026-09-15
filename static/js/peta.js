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
    };

    basemaps.osm.addTo(map);

    document.querySelectorAll('input[name="basemap"]').forEach(radio => {
        radio.addEventListener('change', () => {
            const key = radio.value;
            Object.values(basemaps).forEach(layer => map.removeLayer(layer));
            basemaps[key].addTo(map);
        });
    });

    /* -------------------- STYLE DEFINITIONS -------------------- */
    const styleRivers = {
        color: '#0ea5e9',
        weight: 3,
        opacity: 0.9,
    };

    const styleIrrigation = {
        color: '#f59e0b',
        weight: 2.5,
        dashArray: '5 4',
    };

    /* Custom divIcon untuk marker kecamatan */
    const districtIcon = L.divIcon({
        className: 'agrotek-marker',
        html: '<span></span>',
        iconSize: [12, 12],
        iconAnchor: [6, 6],
    });

    /* -------------------- BINDERS -------------------- */
    function bindDistrict(feature, layer) {
        const p = feature.properties || {};
        const name = p.name || '-';
        layer.bindPopup(`
            <div class="popup-title">Kecamatan ${name}</div>
            <div class="popup-row"><span>Luas wilayah</span><span>${p.area_km2 || '-'} km²</span></div>
            <div class="popup-row"><span>Jumlah desa</span><span>${p.village_count || '-'}</span></div>
            <div class="popup-row"><span>Sumber data</span><span>DEMO</span></div>
        `, { maxWidth: 260 });

        layer.bindTooltip(name, {
            direction: 'top',
            offset: [0, -8],
            className: 'agrotek-tooltip',
        });
    }

    function bindRiver(feature, layer) {
        const p = feature.properties || {};
        layer.bindPopup(`
            <div class="popup-title">${p.name || 'Sungai'}</div>
            <div class="popup-row"><span>Kelas</span><span>${p.class || '-'}</span></div>
        `);
    }

    function bindIrrigation(feature, layer) {
        const p = feature.properties || {};
        layer.bindPopup(`
            <div class="popup-title">${p.name || 'Irigasi'}</div>
            <div class="popup-row"><span>Tipe</span><span>${p.type || '-'}</span></div>
        `);
    }

    /* -------------------- LAYER STORAGE -------------------- */
    const activeLayers = {};
    const districtData = { features: [] };

    /* -------------------- LOAD LAYERS -------------------- */
    function loadDistricts() {
        return fetch('/peta/data/districts')
            .then(r => r.json())
            .then(geojson => {
                districtData.features = geojson.features || [];

                const layer = L.geoJSON(geojson, {
                    onEachFeature: bindDistrict,
                    pointToLayer: (feature, latlng) => L.marker(latlng, { icon: districtIcon }),
                });

                layer.addTo(map);
                activeLayers.districts = layer;
                return layer;
            })
            .catch(err => console.error('[AGROTEK] districts error:', err));
    }

    function loadRivers() {
        return fetch('/peta/data/rivers')
            .then(r => r.json())
            .then(geojson => {
                const layer = L.geoJSON(geojson, {
                    onEachFeature: bindRiver,
                    style: styleRivers,
                });
                layer.addTo(map);
                activeLayers.rivers = layer;
            })
            .catch(err => console.error('[AGROTEK] rivers error:', err));
    }

    function loadIrrigation() {
        return fetch('/peta/data/irrigation')
            .then(r => r.json())
            .then(geojson => {
                const layer = L.geoJSON(geojson, {
                    onEachFeature: bindIrrigation,
                    style: styleIrrigation,
                });
                layer.addTo(map);
                activeLayers.irrigation = layer;
            })
            .catch(err => console.error('[AGROTEK] irrigation error:', err));
    }

    // Load semua layer paralel
    Promise.all([
        loadDistricts(),
        loadRivers(),
        loadIrrigation(),
    ]).then(() => {
        console.log('[AGROTEK] Semua layer dimuat.');
    });

    /* -------------------- LAYER TOGGLE -------------------- */
    document.querySelectorAll('.layer-toggle input').forEach(cb => {
        cb.addEventListener('change', () => {
            const name = cb.dataset.layer;
            const layer = activeLayers[name];
            if (!layer) return;

            if (cb.checked) layer.addTo(map);
            else map.removeLayer(layer);
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

            const matches = districtData.features
                .filter(f => (f.properties.name || '').toLowerCase().includes(q))
                .slice(0, 8);

            matches.forEach(f => {
                const li = document.createElement('li');
                li.textContent = f.properties.name;
                li.addEventListener('click', () => {
                    const [lng, lat] = f.geometry.coordinates;
                    map.flyTo([lat, lng], 14, { duration: 0.8 });
                    searchResults.innerHTML = '';
                    searchInput.value = f.properties.name;
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