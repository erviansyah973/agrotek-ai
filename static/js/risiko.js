/* ============================================================
   AGROTEK AI — Early Warning Scripts
   ============================================================ */
(function () {
    'use strict';

    if (typeof L === 'undefined') {
        console.warn('[AGROTEK] Leaflet belum dimuat.');
        return;
    }

    /* -------------------- INIT MAP -------------------- */
    const map = L.map('mapRisiko', {
        center: [-8.1845, 113.6681],
        zoom: 9,
        zoomControl: true,
        attributionControl: false,
    });

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 18,
    }).addTo(map);

    /* -------------------- COLOR BY LEVEL -------------------- */
    function colorByLevel(level) {
        return {
            "rendah": "#10b981",
            "sedang": "#f59e0b",
            "tinggi": "#ef4444",
        }[level] || "#64748b";
    }

    /* -------------------- ICON BUILDERS -------------------- */
    function createIcon(color, shape) {
        // shape: 'circle' (banjir) atau 'square' (kekeringan)
        const borderRadius = shape === 'circle' ? '50%' : '4px';
        return L.divIcon({
            className: 'agrotek-risiko-marker',
            html: `
                <div style="
                    width: 16px; height: 16px;
                    background: ${color};
                    border: 2px solid #fff;
                    border-radius: ${borderRadius};
                    box-shadow: 0 0 0 3px ${color}40, 0 0 12px ${color}cc;
                    transition: all .2s;
                "></div>
            `,
            iconSize: [16, 16],
            iconAnchor: [8, 8],
        });
    }

    /* -------------------- LAYER STORAGE -------------------- */
    const markers = {};

    /* -------------------- LOAD LAYERS -------------------- */
    function loadLayer(url, shape, label) {
        return fetch(url)
            .then(r => r.json())
            .then(geojson => {
                L.geoJSON(geojson, {
                    pointToLayer: (feature, latlng) => {
                        const p = feature.properties;
                        const color = colorByLevel(p.level);
                        const marker = L.marker(latlng, {
                            icon: createIcon(color, shape),
                        });

                        marker.bindPopup(`
                            <div style="font-family: 'Inter', sans-serif; min-width: 200px;">
                                <div style="font-weight: 700; color: #0f172a; font-size: 1rem; margin-bottom: 8px; padding-bottom: 8px; border-bottom: 1px solid #e2e8f0;">
                                    ${p.district}
                                </div>
                                <div style="display: flex; justify-content: space-between; font-size: .82rem; padding: 3px 0;">
                                    <span style="color: #64748b;">Jenis</span>
                                    <strong style="color: ${color};">${label}</strong>
                                </div>
                                <div style="display: flex; justify-content: space-between; font-size: .82rem; padding: 3px 0;">
                                    <span style="color: #64748b;">Level</span>
                                    <strong style="color: ${color};">${p.level.charAt(0).toUpperCase() + p.level.slice(1)}</strong>
                                </div>
                                <div style="display: flex; justify-content: space-between; font-size: .82rem; padding: 3px 0;">
                                    <span style="color: #64748b;">Skor</span>
                                    <strong style="color: #0f172a;">${p.score}</strong>
                                </div>
                                <div style="margin-top: 8px; padding-top: 8px; border-top: 1px dashed #e2e8f0; font-size: .78rem; color: #64748b; font-style: italic;">
                                    ${p.catatan || '-'}
                                </div>
                            </div>
                        `, { maxWidth: 260 });

                        markers[p.district + '_' + label] = marker;
                        return marker;
                    },
                }).addTo(map);
            })
            .catch(err => console.error(`[AGROTEK] load ${label} error:`, err));
    }

    /* Load banjir & kekeringan */
    Promise.all([
        loadLayer('/risiko/data/banjir', 'circle', 'Banjir'),
        loadLayer('/risiko/data/kering', 'square', 'Kekeringan'),
    ]).then(() => {
        console.log('[AGROTEK] Risiko layers loaded.');
    });

    /* -------------------- FOCUS ALERT (dipanggil onclick) -------------------- */
    window.focusAlert = function (el) {
        const lat = parseFloat(el.dataset.lat);
        const lng = parseFloat(el.dataset.lng);
        const district = el.dataset.district;

        if (isNaN(lat) || isNaN(lng)) return;

        // Fly to lokasi
        map.flyTo([lat, lng], 12, { duration: 1 });

        // Buka semua marker yang match dengan district
        setTimeout(() => {
            Object.keys(markers).forEach(key => {
                if (key.startsWith(district + '_')) {
                    markers[key].openPopup();
                }
            });
        }, 1100);

        // Highlight baris tabel
        document.querySelectorAll('tr.highlight-row').forEach(tr => tr.classList.remove('highlight-row'));
        document.querySelectorAll(`tr[data-district="${district}"]`).forEach(tr => {
            tr.classList.add('highlight-row');
            setTimeout(() => tr.classList.remove('highlight-row'), 2500);
        });

        // Scroll ke peta (opsional, di mobile)
        if (window.innerWidth < 900) {
            document.getElementById('mapRisiko').scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    };

    /* -------------------- LOG -------------------- */
    console.log('[AGROTEK] Early Warning loaded.');
})();