/* ============================================================
   AGROTEK AI — Modul Hidrologi Scripts
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
        cyanLight: 'rgba(6,182,212,0.15)',
        amber: '#f59e0b',
        amberLight: 'rgba(245,158,11,0.15)',
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

    /* -------------------- CURAH HUJAN -------------------- */
    const rainEl = document.getElementById('chartRainfall');
    if (rainEl) {
        fetch('/hidrologi/data/rainfall')
            .then(r => r.json())
            .then(d => {
                new Chart(rainEl, {
                    type: 'line',
                    data: {
                        labels: d.labels,
                        datasets: [{
                            label: 'mm',
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

    /* -------------------- TMA -------------------- */
    const tmaEl = document.getElementById('chartTMA');
    if (tmaEl) {
        fetch('/hidrologi/data/tma')
            .then(r => r.json())
            .then(d => {
                new Chart(tmaEl, {
                    type: 'line',
                    data: {
                        labels: d.labels,
                        datasets: [{
                            label: 'TMA (cm)',
                            data: d.data,
                            borderColor: C.emerald,
                            backgroundColor: C.emeraldLight,
                            fill: true,
                            tension: 0.35,
                            borderWidth: 2,
                            pointRadius: 0,
                            pointHoverRadius: 4,
                        }]
                    },
                    options: {
                        plugins: { legend: { display: false } },
                        scales: { x: axis(), y: axis({ beginAtZero: false }) },
                        interaction: { intersect: false, mode: 'index' },
                    }
                });
            })
            .catch(err => console.error('[AGROTEK] tma error:', err));
    }

    /* -------------------- DEBIT -------------------- */
    const debitEl = document.getElementById('chartDebit');
    if (debitEl) {
        fetch('/hidrologi/data/debit')
            .then(r => r.json())
            .then(d => {
                new Chart(debitEl, {
                    type: 'line',
                    data: {
                        labels: d.labels,
                        datasets: [{
                            label: 'Debit (m³/s)',
                            data: d.data,
                            borderColor: C.amber,
                            backgroundColor: C.amberLight,
                            fill: true,
                            tension: 0.35,
                            borderWidth: 2,
                            pointRadius: 0,
                            pointHoverRadius: 4,
                        }]
                    },
                    options: {
                        plugins: { legend: { display: false } },
                        scales: { x: axis(), y: axis({ beginAtZero: true }) },
                        interaction: { intersect: false, mode: 'index' },
                    }
                });
            })
            .catch(err => console.error('[AGROTEK] debit error:', err));
    }

    console.log('[AGROTEK] Hidrologi loaded.');
})();