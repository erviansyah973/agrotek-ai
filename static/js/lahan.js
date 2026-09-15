/* ============================================================
   AGROTEK AI — Kesesuaian Lahan Scripts
   ============================================================ */
(function () {
    'use strict';

    if (typeof Chart === 'undefined') {
        console.warn('[AGROTEK] Chart.js belum dimuat.');
        return;
    }

    const urlParams = new URLSearchParams(window.location.search);
    const crop = (urlParams.get('crop') || 'PDI').toUpperCase();

    const C = {
        S1: '#10b981',
        S2: '#0ea5e9',
        S3: '#f59e0b',
        N:  '#ef4444',
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

    fetch(`/lahan/data/${crop}`)
        .then(r => r.json())
        .then(d => {
            if (!d.ok) {
                console.error('[AGROTEK] Data error:', d.error);
                return;
            }

            const distEl = document.getElementById('chartDistribusi');
            if (distEl) {
                const distribusi = d.distribusi;
                new Chart(distEl, {
                    type: 'doughnut',
                    data: {
                        labels: ['S1 (Sangat Sesuai)', 'S2 (Sesuai)', 'S3 (Cukup Sesuai)', 'N (Tidak Sesuai)'],
                        datasets: [{
                            data: [distribusi.S1, distribusi.S2, distribusi.S3, distribusi.N],
                            backgroundColor: [C.S1, C.S2, C.S3, C.N],
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
                                    label: (ctx) => ` ${ctx.label}: ${ctx.parsed} kecamatan`
                                }
                            }
                        }
                    }
                });
            }

            const luasEl = document.getElementById('chartLuas');
            if (luasEl) {
                const luas = d.luas;
                new Chart(luasEl, {
                    type: 'bar',
                    data: {
                        labels: ['S1', 'S2', 'S3', 'N'],
                        datasets: [{
                            label: 'Luas (ha)',
                            data: [luas.S1, luas.S2, luas.S3, luas.N],
                            backgroundColor: [C.S1, C.S2, C.S3, C.N],
                            borderRadius: 8,
                            borderSkipped: false,
                            barThickness: 48,
                        }]
                    },
                    options: {
                        plugins: {
                            legend: { display: false },
                            tooltip: {
                                callbacks: {
                                    label: (ctx) => ` ${ctx.parsed.y.toLocaleString('id-ID')} ha`
                                }
                            }
                        },
                        scales: {
                            x: axis(),
                            y: axis({
                                beginAtZero: true,
                                ticks: {
                                    color: C.tick,
                                    callback: (v) => v.toLocaleString('id-ID'),
                                }
                            }),
                        },
                    }
                });
            }

            console.log('[AGROTEK] Lahan charts loaded for', d.label);
        })
        .catch(err => console.error('[AGROTEK] Lahan error:', err));

    console.log('[AGROTEK] Kesesuaian Lahan loaded.');
})();