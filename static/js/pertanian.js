/* ============================================================
   AGROTEK AI — Modul Pertanian Scripts
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
        red: '#ef4444',
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

    /* -------------------- PRODUKSI PER KOMODITAS -------------------- */
    const prodEl = document.getElementById('chartProduction');
    if (prodEl) {
        fetch('/pertanian/data/production')
            .then(r => r.json())
            .then(d => {
                new Chart(prodEl, {
                    type: 'bar',
                    data: {
                        labels: d.labels,
                        datasets: [{
                            label: 'Produksi (ribu ton)',
                            data: d.data,
                            backgroundColor: [
                                C.emerald, C.sky, C.cyan, C.amber, C.purple, C.red
                            ],
                            borderRadius: 6,
                            borderSkipped: false,
                            barThickness: 32,
                        }]
                    },
                    options: {
                        plugins: { legend: { display: false } },
                        scales: { x: axis(), y: axis({ beginAtZero: true }) },
                    }
                });
            })
            .catch(err => console.error('[AGROTEK] production error:', err));
    }

    /* -------------------- PRODUKSI PER KATEGORI -------------------- */
    const catEl = document.getElementById('chartCategory');
    if (catEl) {
        fetch('/pertanian/data/category')
            .then(r => r.json())
            .then(d => {
                new Chart(catEl, {
                    type: 'doughnut',
                    data: {
                        labels: d.labels,
                        datasets: [{
                            data: d.data,
                            backgroundColor: [C.emerald, C.amber, C.purple],
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
                                    label: (ctx) => ` ${ctx.label}: ${ctx.parsed.toFixed(1)} ribu ton`
                                }
                            }
                        }
                    }
                });
            })
            .catch(err => console.error('[AGROTEK] category error:', err));
    }

    console.log('[AGROTEK] Pertanian loaded.');
})();