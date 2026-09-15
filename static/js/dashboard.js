/* ============================================================
   AGROTEK AI — Dashboard Scripts (FASE 3)
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
        amber: '#f59e0b',
        purple: '#a855f7',
        cyan: '#06b6d4',
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

    /* ------------------------- RAINFALL ------------------------- */
    const rainfallEl = document.getElementById('chartRainfall');
    if (rainfallEl) {
        fetch('/dashboard/data/rainfall')
            .then(r => r.json())
            .then(d => {
                new Chart(rainfallEl, {
                    type: 'line',
                    data: {
                        labels: d.labels,
                        datasets: [{
                            label: 'Curah Hujan (mm)',
                            data: d.data,
                            borderColor: C.sky,
                            backgroundColor: C.skyLight,
                            fill: true,
                            tension: 0.4,
                            borderWidth: 2.5,
                            pointRadius: 3,
                            pointBackgroundColor: C.sky,
                            pointBorderColor: '#fff',
                            pointBorderWidth: 1.5,
                            pointHoverRadius: 5,
                        }]
                    },
                    options: {
                        plugins: { legend: { display: false } },
                        scales: { x: axis(), y: axis({ beginAtZero: true }) },
                        interaction: { intersect: false, mode: 'index' },
                    }
                });
            })
            .catch(err => console.error('[AGROTEK] rainfall error:', err));
    }

    /* ------------------------- CROPS ------------------------- */
    const cropsEl = document.getElementById('chartCrops');
    if (cropsEl) {
        fetch('/dashboard/data/crops')
            .then(r => r.json())
            .then(d => {
                new Chart(cropsEl, {
                    type: 'bar',
                    data: {
                        labels: d.labels,
                        datasets: [{
                            label: 'Produksi (ribu ton)',
                            data: d.data,
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
            })
            .catch(err => console.error('[AGROTEK] crops error:', err));
    }

    /* ------------------------- LAND USE ------------------------- */
    const landEl = document.getElementById('chartLandUse');
    if (landEl) {
        fetch('/dashboard/data/land-use')
            .then(r => r.json())
            .then(d => {
                new Chart(landEl, {
                    type: 'doughnut',
                    data: {
                        labels: d.labels,
                        datasets: [{
                            data: d.data,
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
            })
            .catch(err => console.error('[AGROTEK] landuse error:', err));
    }

    /* ------------------------- WATER ------------------------- */
    const waterEl = document.getElementById('chartWater');
    if (waterEl) {
        Promise.all([
            fetch('/dashboard/data/water-level').then(r => r.json()),
            fetch('/dashboard/data/discharge').then(r => r.json()),
        ])
        .then(([tma, q]) => {
            new Chart(waterEl, {
                type: 'line',
                data: {
                    labels: tma.labels,
                    datasets: [
                        {
                            label: 'TMA (cm)',
                            data: tma.data,
                            borderColor: C.sky,
                            backgroundColor: C.skyLight,
                            tension: 0.35,
                            borderWidth: 2,
                            pointRadius: 0,
                            pointHoverRadius: 4,
                            yAxisID: 'y',
                        },
                        {
                            label: 'Debit (m³/s)',
                            data: q.data,
                            borderColor: C.emerald,
                            backgroundColor: C.emeraldLight,
                            tension: 0.35,
                            borderWidth: 2,
                            pointRadius: 0,
                            pointHoverRadius: 4,
                            yAxisID: 'y1',
                        }
                    ]
                },
                options: {
                    plugins: { legend: { position: 'top', align: 'end' } },
                    interaction: { intersect: false, mode: 'index' },
                    scales: {
                        x: axis(),
                        y: axis({
                            position: 'left',
                            title: { display: true, text: 'TMA (cm)', color: C.tick, font: { size: 10 } }
                        }),
                        y1: axis({
                            position: 'right',
                            grid: { display: false },
                            title: { display: true, text: 'Debit (m³/s)', color: C.tick, font: { size: 10 } }
                        }),
                    }
                }
            });
        })
        .catch(err => console.error('[AGROTEK] water error:', err));
    }

    console.log('[AGROTEK] Dashboard loaded.');
})();