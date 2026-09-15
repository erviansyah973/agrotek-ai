/* ============================================================
   AGROTEK AI — Modul Irigasi Scripts
   ============================================================ */
(function () {
    'use strict';

    if (typeof Chart === 'undefined') {
        console.warn('[AGROTEK] Chart.js belum dimuat.');
        return;
    }

    const C = {
        emerald: '#10b981',
        emeraldLight: 'rgba(16,185,129,0.15)',
        sky: '#0ea5e9',
        skyLight: 'rgba(14,165,233,0.15)',
        cyan: '#06b6d4',
        amber: '#f59e0b',
        red: '#ef4444',
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

    /* -------------------- NERACA AIR PER KECAMATAN -------------------- */
    const neracaEl = document.getElementById('chartNeraca');
    if (neracaEl) {
        fetch('/irigasi/data/neraca')
            .then(r => r.json())
            .then(d => {
                // Warna bar berdasarkan status: hijau (surplus) / merah (defisit)
                const colors = d.neraca.map(v =>
                    v >= 0 ? 'rgba(16,185,129,0.85)' : 'rgba(239,68,68,0.85)'
                );

                new Chart(neracaEl, {
                    type: 'bar',
                    data: {
                        labels: d.labels,
                        datasets: [{
                            label: 'Neraca (juta m³)',
                            data: d.neraca,
                            backgroundColor: colors,
                            borderRadius: 6,
                            borderSkipped: false,
                            barThickness: 32,
                        }]
                    },
                    options: {
                        plugins: {
                            legend: { display: false },
                            tooltip: {
                                callbacks: {
                                    label: (ctx) => {
                                        const v = ctx.parsed.y;
                                        const status = v >= 0 ? 'Surplus' : 'Defisit';
                                        return ` Neraca: ${v >= 0 ? '+' : ''}${v.toFixed(1)} juta m³ (${status})`;
                                    }
                                }
                            }
                        },
                        scales: {
                            x: axis(),
                            y: axis({
                                beginAtZero: true,
                                title: {
                                    display: true,
                                    text: 'Neraca Air (juta m³)',
                                    color: C.tick,
                                    font: { size: 10 },
                                }
                            })
                        },
                    }
                });
            })
            .catch(err => console.error('[AGROTEK] neraca error:', err));
    }

    /* -------------------- DISTRIBUSI SALURAN -------------------- */
    const saluranEl = document.getElementById('chartSaluran');
    if (saluranEl) {
        fetch('/irigasi/data/saluran')
            .then(r => r.json())
            .then(d => {
                new Chart(saluranEl, {
                    type: 'doughnut',
                    data: {
                        labels: d.labels,
                        datasets: [{
                            data: d.data,
                            backgroundColor: [C.emerald, C.sky, C.amber, C.slate],
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
                                    label: (ctx) => ` ${ctx.label}: ${ctx.parsed} km`
                                }
                            }
                        }
                    }
                });
            })
            .catch(err => console.error('[AGROTEK] saluran error:', err));
    }

    console.log('[AGROTEK] Irigasi loaded.');
})();