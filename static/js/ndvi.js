/* ============================================================
   AGROTEK AI — NDVI Monitoring Scripts
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
        amber: '#f59e0b',
        red: '#ef4444',
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

    /* -------------------- NDVI TIME-SERIES -------------------- */
    const tsEl = document.getElementById('chartTimeseries');
    if (tsEl) {
        fetch('/ndvi/data/timeseries')
            .then(r => r.json())
            .then(d => {
                new Chart(tsEl, {
                    type: 'line',
                    data: {
                        labels: d.labels,
                        datasets: [{
                            label: 'NDVI',
                            data: d.data,
                            borderColor: C.emerald,
                            backgroundColor: C.emeraldLight,
                            fill: true,
                            tension: 0.4,
                            borderWidth: 2.5,
                            pointRadius: 4,
                            pointBackgroundColor: C.emerald,
                            pointBorderColor: '#fff',
                            pointBorderWidth: 2,
                            pointHoverRadius: 6,
                        }]
                    },
                    options: {
                        plugins: {
                            legend: { display: false },
                            tooltip: {
                                callbacks: {
                                    label: (ctx) => {
                                        const v = ctx.parsed.y;
                                        let kat = 'Non-Vegetasi';
                                        if (v >= 0.8) kat = 'Sangat Lebat';
                                        else if (v >= 0.6) kat = 'Lebat';
                                        else if (v >= 0.4) kat = 'Sedang';
                                        else if (v >= 0.2) kat = 'Jarang';
                                        return ` NDVI: ${v.toFixed(2)} (${kat})`;
                                    }
                                }
                            }
                        },
                        scales: {
                            x: axis(),
                            y: axis({
                                min: 0,
                                max: 1,
                                title: {
                                    display: true,
                                    text: 'NDVI',
                                    color: C.tick,
                                    font: { size: 10 },
                                }
                            }),
                        },
                        interaction: { intersect: false, mode: 'index' },
                    }
                });
            })
            .catch(err => console.error('[AGROTEK] NDVI timeseries error:', err));
    }

    /* -------------------- NDVI PER KECAMATAN -------------------- */
    const distEl = document.getElementById('chartDistricts');
    if (distEl) {
        fetch('/ndvi/data/districts')
            .then(r => r.json())
            .then(d => {
                // Ambil 8 teratas
                const items = d.labels.map((label, i) => ({
                    label: label,
                    value: d.data[i],
                })).sort((a, b) => b.value - a.value).slice(0, 8);

                const colorByValue = (v) => {
                    if (v >= 0.6) return C.emerald;
                    if (v >= 0.4) return '#eab308';
                    return C.amber;
                };

                new Chart(distEl, {
                    type: 'bar',
                    data: {
                        labels: items.map(i => i.label),
                        datasets: [{
                            label: 'NDVI',
                            data: items.map(i => i.value),
                            backgroundColor: items.map(i => colorByValue(i.value)),
                            borderRadius: 6,
                            borderSkipped: false,
                            barThickness: 20,
                        }]
                    },
                    options: {
                        indexAxis: 'y',
                        plugins: {
                            legend: { display: false },
                            tooltip: {
                                callbacks: {
                                    label: (ctx) => ` NDVI: ${ctx.parsed.x.toFixed(2)}`
                                }
                            }
                        },
                        scales: {
                            x: axis({ beginAtZero: true, max: 1 }),
                            y: axis({ grid: { display: false } }),
                        },
                    }
                });
            })
            .catch(err => console.error('[AGROTEK] NDVI districts error:', err));
    }

    console.log('[AGROTEK] NDVI Monitoring loaded.');
})();