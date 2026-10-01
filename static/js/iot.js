/* ============================================================
   AGROTEK AI — IoT Monitoring Scripts
   ============================================================ */
(function () {
    'use strict';

    console.log('[AGROTEK] IoT module loaded.');

    /* Poll the gateway health endpoint; this does not refresh simulated readings. */
    let refreshCount = 0;

    async function checkIoTStatus() {
        try {
            const res = await fetch('/api/iot/status');
            const data = await res.json();
            refreshCount++;
            console.log(`[AGROTEK] IoT status (${refreshCount}):`, data.status, data.version);
        } catch (err) {
            console.warn('[AGROTEK] IoT status error:', err);
        }
    }

    // Cek status setelah halaman load
    checkIoTStatus();

    // Recheck service availability every minute.
    setInterval(checkIoTStatus, 60000);

    /* Highlight baris device yang baru update (opsional) */
    document.querySelectorAll('table tbody tr').forEach((row, i) => {
        row.style.opacity = '0';
        row.style.transition = 'opacity .3s';
        setTimeout(() => {
            row.style.opacity = '1';
        }, i * 40);
    });

    console.log('[AGROTEK] IoT demo page ready. Ingest endpoint is a placeholder.');
})();