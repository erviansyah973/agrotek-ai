/* ============================================================
   AGROTEK AI — Statistik Page Scripts
   ============================================================ */
(function () {
    'use strict';

    if (typeof Chart === 'undefined') {
        console.warn('[AGROTEK] Chart.js belum dimuat.');
        return;
    }

    const C = {
        emerald: '#10b981',
        sky: '#0ea5e9',
        cyan: '#06b6d4',
        amber: '#f59e0b',
        purple: '#a855f7',
        slate: '#64748b',
        grid: 'rgba(148,163,184,0.12)',
        tick: '#64748b',
    };

    Chart.defaults.font.family = "'Inter', -apple-system, sans-serif";
    Chart.defaults.font.size = 11;
    Chart.defaults.color = C.tick;
    Chart.defaults.plugins.legend.labels.usePointStyle = true;
    Chart.defaults.plugins.legend.labels.boxWidth = 8;
    Chart.defaults.plugins.legend.labels.padding = 12;
    Chart.defaults.maintainAspectRatio = false;

    const axis = (opts = {}) => Object.assign({
        grid: { color: C.grid, drawBorder: false },
        ticks: { color: C.tick, font: { size: 11 } },
    }, opts);

    /* -------------------- PRODUKSI KOMODITAS -------------------- */
    const cropsEl = document.getElementById('chartCrops');
    if (cropsEl) {
        new Chart(cropsEl, {
            type: 'bar',
            data: {
                labels: ['Padi', 'Jagung', 'Kedelai', 'Cabai', 'Tembakau', 'Lainnya'],
                datasets: [{
                    label: 'Produksi (ribu ton)',
                    data: [620, 245, 42, 28, 35, 88],
                    backgroundColor: [
                        C.emerald, C.sky, C.cyan, C.amber, C.purple, C.slate
                    ],
                    borderRadius: 6,
                    borderSkipped: false,
                    barThickness: 28,
                }]
            },
            options: {
                plugins: { legend: { display: false } },
                scales: { x: axis(), y: axis({ beginAtZero: true }) },
            }
        });
    }

    /* -------------------- PENGGUNAAN LAHAN -------------------- */
    const landEl = document.getElementById('chartLandUse');
    if (landEl) {
        new Chart(landEl, {
            type: 'doughnut',
            data: {
                labels: ['Sawah', 'Tegalan', 'Perkebunan', 'Hutan', 'Permukiman', 'Lainnya'],
                datasets: [{
                    data: [96, 58, 82, 145, 42, 25],
                    backgroundColor: [
                        C.emerald, C.amber, C.purple,
                        '#166534', C.sky, C.slate
                    ],
                    borderWidth: 0,
                    hoverOffset: 8,
                }]
            },
            options: {
                cutout: '62%',
                plugins: {
                    legend: {
                        position: 'right',
                        labels: { padding: 12, boxWidth: 8 },
                    },
                    tooltip: {
                        callbacks: {
                            label: (ctx) => ` ${ctx.label}: ${ctx.parsed} ribu ha`
                        }
                    }
                }
            }
        });
    }

    /* -------------------- SEARCH KECAMATAN -------------------- */
    const searchInput = document.getElementById('searchKecamatan');
    const table = document.getElementById('tabelKecamatan');

    if (searchInput && table) {
        searchInput.addEventListener('input', (e) => {
            const q = e.target.value.toLowerCase().trim();
            const rows = table.querySelectorAll('tbody tr');

            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = (!q || text.includes(q)) ? '' : 'none';
            });
        });
    }

    console.log('[AGROTEK] Statistik loaded.');
})();