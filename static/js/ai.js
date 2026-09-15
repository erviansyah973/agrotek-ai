/* ============================================================
   AGROTEK AI — Analisis Sawah Saya Scripts
   ============================================================ */
(function () {
    'use strict';

    const selKec = document.getElementById('selKecamatan');
    const selKom = document.getElementById('selKomoditas');
    const btnAnalyze = document.getElementById('btnAnalyze');
    const resultBox = document.getElementById('aiResult');

    if (!selKec || !selKom || !btnAnalyze || !resultBox) {
        console.warn('[AGROTEK] Elemen AI tidak ditemukan.');
        return;
    }

    /* -------------------- ENABLE BUTTON -------------------- */
    function checkInputs() {
        const ok = selKec.value && selKom.value;
        btnAnalyze.disabled = !ok;
    }
    selKec.addEventListener('change', checkInputs);
    selKom.addEventListener('change', checkInputs);

    /* -------------------- HELPER: COLOR BY CLASS -------------------- */
    function classColor(kelas) {
        return {
            "S1": "#10b981",
            "S2": "#0ea5e9",
            "S3": "#f59e0b",
            "N":  "#ef4444",
        }[kelas] || "#64748b";
    }

    function scoreColor(score) {
        if (score >= 80) return "#10b981";
        if (score >= 65) return "#0ea5e9";
        if (score >= 45) return "#f59e0b";
        return "#ef4444";
    }

    function scoreBarColor(score) {
        return `linear-gradient(90deg, ${scoreColor(score)} 0%, ${scoreColor(score)}dd 100%)`;
    }

    /* -------------------- LABELS PARAMETER -------------------- */
    const PARAM_LABELS = {
        "curah_hujan":      "Curah Hujan",
        "elevasi":          "Elevasi",
        "kemiringan":       "Kemiringan",
        "ketersediaan_air": "Ketersediaan Air",
        "risiko":           "Risiko Bencana",
    };

    const PARAM_UNITS = {
        "curah_hujan":      "mm/tahun",
        "elevasi":          "m dpl",
        "kemiringan":       "%",
    };

    /* -------------------- RENDER RESULT -------------------- */
    function renderResult(r) {
        const color = classColor(r.kelas);

        // ---- Score rows ----
        const scoreRows = Object.keys(r.scores).map(k => {
            const val = r.scores[k];
            const bobot = (r.bobot[k] * 100).toFixed(0);
            return `
                <div class="score-row">
                    <div class="score-row-label">
                        ${PARAM_LABELS[k] || k}
                        <small>Bobot ${bobot}%</small>
                    </div>
                    <div class="score-row-bar">
                        <i style="width: ${val}%; background: ${scoreBarColor(val)};"></i>
                    </div>
                    <div class="score-row-value">${val.toFixed(0)}</div>
                </div>
            `;
        }).join('');

        // ---- Params grid ----
        const p = r.params;
        const rule = r.rule;
        const paramsGrid = `
            <div class="param-item ${p.curah_hujan >= rule.curah_hujan[0] && p.curah_hujan <= rule.curah_hujan[1] ? 'ok' : 'warn'}">
                <span>Curah Hujan Aktual</span>
                <strong>${p.curah_hujan} mm/tahun</strong>
            </div>
            <div class="param-item ${p.elevasi >= rule.elevasi[0] && p.elevasi <= rule.elevasi[1] ? 'ok' : 'warn'}">
                <span>Elevasi Aktual</span>
                <strong>${p.elevasi} m dpl</strong>
            </div>
            <div class="param-item ${p.kemiringan >= rule.kemiringan[0] && p.kemiringan <= rule.kemiringan[1] ? 'ok' : 'warn'}">
                <span>Kemiringan Lahan</span>
                <strong>${p.kemiringan} %</strong>
            </div>
            <div class="param-item">
                <span>Ketersediaan Air</span>
                <strong>${p.ketersediaan_air.charAt(0).toUpperCase() + p.ketersediaan_air.slice(1)}</strong>
            </div>
            <div class="param-item ${p.risiko_banjir === 'rendah' ? 'ok' : 'warn'}">
                <span>Risiko Banjir</span>
                <strong>${p.risiko_banjir.charAt(0).toUpperCase() + p.risiko_banjir.slice(1)}</strong>
            </div>
            <div class="param-item ${p.risiko_kekeringan === 'rendah' ? 'ok' : 'warn'}">
                <span>Risiko Kekeringan</span>
                <strong>${p.risiko_kekeringan.charAt(0).toUpperCase() + p.risiko_kekeringan.slice(1)}</strong>
            </div>
        `;

        // ---- Rekomendasi ----
        const rekomendasiList = r.rekomendasi.map(item =>
            `<div class="rekomendasi-item">${item}</div>`
        ).join('');

        // ---- Full HTML ----
        resultBox.innerHTML = `
            <div class="result-header">
                <div class="result-score-circle" style="background: linear-gradient(135deg, ${color}, ${color}dd);">
                    <strong>${r.skor_total.toFixed(0)}</strong>
                    <small>Skor</small>
                </div>
                <div class="result-header-info">
                    <h2>${r.komoditas_icon} ${r.komoditas} di ${r.kecamatan}</h2>
                    <p>Hasil analisis kesesuaian lahan berdasarkan 5 parameter lingkungan dengan metode weighted overlay.</p>
                    <span class="result-kelas" style="background: ${color}20; color: ${color};">
                        ${r.kelas} · ${r.kelas_label}
                    </span>
                </div>
            </div>

            <div class="result-section">
                <h3>Skor per Parameter</h3>
                <div class="score-list">
                    ${scoreRows}
                </div>
            </div>

            <div class="result-section">
                <h3>Parameter Lingkungan</h3>
                <div class="params-grid">
                    ${paramsGrid}
                </div>
            </div>

            <div class="result-section">
                <h3>Rekomendasi</h3>
                <div class="rekomendasi-list">
                    ${rekomendasiList}
                </div>
            </div>

            <div class="transparency-box">
                <strong>⚠️ Transparansi Metode:</strong> Hasil ini dihitung menggunakan
                <strong>rule-based weighted overlay</strong> — bukan machine learning.
                Semua bobot parameter ditampilkan secara terbuka (Curah Hujan 30%,
                Kemiringan 20%, Ketersediaan Air 20%, Elevasi 15%, Risiko 15%).
                Data parameter masih DEMO dan akan disinkronkan dengan data lapangan
                SID di fase berikutnya.
            </div>
        `;

        // Scroll ke hasil
        setTimeout(() => {
            resultBox.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 100);
    }

    /* -------------------- ERROR RENDER -------------------- */
    function renderError(msg) {
        resultBox.innerHTML = `
            <div class="result-placeholder">
                <div class="result-placeholder-icon" style="color:#dc2626;">⚠️</div>
                <h3 style="color:#dc2626;">Analisis Gagal</h3>
                <p>${msg}</p>
            </div>
        `;
    }

    /* -------------------- SUBMIT -------------------- */
    btnAnalyze.addEventListener('click', async () => {
        const kecamatan = selKec.value;
        const komoditas = selKom.value;

        if (!kecamatan || !komoditas) return;

        // Loading state
        btnAnalyze.disabled = true;
        btnAnalyze.classList.add('loading');
        const btnText = btnAnalyze.querySelector('.btn-text');
        const originalText = btnText.textContent;
        btnText.textContent = 'Menganalisis...';

        // Show loading placeholder
        resultBox.innerHTML = `
            <div class="result-placeholder">
                <div class="result-placeholder-icon" style="animation: spin 2s linear infinite;">⚙️</div>
                <h3>Menganalisis...</h3>
                <p>Menghitung skor kesesuaian lahan untuk <strong>${komoditas}</strong> di <strong>${kecamatan}</strong>.</p>
            </div>
        `;

        try {
            const res = await fetch('/ai/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ kecamatan, komoditas }),
            });
            const json = await res.json();

            if (json.ok) {
                renderResult(json.result);
            } else {
                renderError(json.error || 'Terjadi kesalahan.');
            }
        } catch (err) {
            console.error('[AGROTEK] AI error:', err);
            renderError('Gagal terhubung ke server. Coba lagi.');
        } finally {
            btnAnalyze.disabled = false;
            btnAnalyze.classList.remove('loading');
            btnText.textContent = originalText;
            checkInputs();
        }
    });

    console.log('[AGROTEK] AI module loaded.');
})();