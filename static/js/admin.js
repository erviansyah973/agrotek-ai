/* ============================================================
   AGROTEK AI — Admin Panel Scripts (Enhanced)
   ============================================================ */
(function () {
    'use strict';

    /* -------------------- TABS -------------------- */
    const tabs = document.querySelectorAll('.tab');
    const panels = document.querySelectorAll('.tab-panel');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const target = tab.dataset.tab;

            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            panels.forEach(p => p.classList.remove('active'));
            const panel = document.getElementById('panel-' + target);
            if (panel) panel.classList.add('active');
        });
    });

    /* -------------------- CHARTS -------------------- */
    if (typeof Chart === 'undefined') {
        console.warn('[AGROTEK] Chart.js belum dimuat.');
        return;
    }

    Chart.defaults.font.family = "'Inter', -apple-system, sans-serif";
    Chart.defaults.font.size = 11;
    Chart.defaults.color = '#64748b';
    Chart.defaults.maintainAspectRatio = false;
    Chart.defaults.plugins.legend.labels.usePointStyle = true;
    Chart.defaults.plugins.legend.labels.boxWidth = 8;
    Chart.defaults.plugins.legend.labels.padding = 12;

    /* ---- Chart 1: Distribusi User per Role ---- */
    const roleEl = document.getElementById('chartRole');
    const roleDataEl = document.getElementById('roleStats');
    if (roleEl && roleDataEl) {
        try {
            const roleData = JSON.parse(roleDataEl.textContent);

            const labels = [];
            const data = [];
            const colors = [];

            const colorMap = {
                "admin":     "#ef4444",
                "mahasiswa": "#0ea5e9",
                "umum":      "#64748b",
            };
            const labelMap = {
                "admin":     "Admin",
                "mahasiswa": "Mahasiswa",
                "umum":      "Umum",
            };

            ["admin", "mahasiswa", "umum"].forEach(role => {
                if (roleData[role] !== undefined) {
                    labels.push(labelMap[role]);
                    data.push(roleData[role]);
                    colors.push(colorMap[role]);
                }
            });

            new Chart(roleEl, {
                type: 'doughnut',
                data: {
                    labels: labels,
                    datasets: [{
                        data: data,
                        backgroundColor: colors,
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
                                label: (ctx) => ` ${ctx.label}: ${ctx.parsed} user`
                            }
                        }
                    }
                }
            });
        } catch (err) {
            console.error('[AGROTEK] Role chart error:', err);
        }
    }

    /* ---- Chart 2: Status Request ---- */
    const statusEl = document.getElementById('chartStatus');
    const statusDataEl = document.getElementById('statusStats');
    if (statusEl && statusDataEl) {
        try {
            const statusData = JSON.parse(statusDataEl.textContent);

            const colorMap = {
                "pending":   "#f59e0b",
                "approved":  "#10b981",
                "rejected":  "#ef4444",
                "delivered": "#0ea5e9",
            };
            const labelMap = {
                "pending":   "Pending",
                "approved":  "Approved",
                "rejected":  "Rejected",
                "delivered": "Delivered",
            };

            const labels = [];
            const data = [];
            const colors = [];

            ["pending", "approved", "rejected", "delivered"].forEach(s => {
                if (statusData[s] !== undefined) {
                    labels.push(labelMap[s]);
                    data.push(statusData[s]);
                    colors.push(colorMap[s]);
                }
            });

            new Chart(statusEl, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        data: data,
                        backgroundColor: colors,
                        borderRadius: 8,
                        borderSkipped: false,
                        barThickness: 40,
                    }]
                },
                options: {
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            callbacks: {
                                label: (ctx) => ` ${ctx.parsed.y} request`
                            }
                        }
                    },
                    scales: {
                        x: {
                            grid: { display: false },
                            ticks: { color: '#64748b' },
                        },
                        y: {
                            beginAtZero: true,
                            grid: { color: 'rgba(148,163,184,0.12)', drawBorder: false },
                            ticks: { color: '#64748b', stepSize: 1 },
                        },
                    },
                }
            });
        } catch (err) {
            console.error('[AGROTEK] Status chart error:', err);
        }
    }

    /* -------------------- FLASH AUTO-DISMISS -------------------- */
    document.querySelectorAll('.flash').forEach(flash => {
        setTimeout(() => {
            flash.style.transition = 'opacity .5s';
            flash.style.opacity = '0';
            setTimeout(() => flash.remove(), 500);
        }, 4000);
    });

    console.log('[AGROTEK] Admin panel loaded.');
})();