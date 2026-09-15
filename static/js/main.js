/* ============================================================
   AGROTEK AI — Main Script
   ============================================================ */
(function () {
    'use strict';

    /* ------------------------------------------------------------
       1. NAVBAR — sticky & hamburger
       ------------------------------------------------------------ */
    const header  = document.getElementById('siteHeader');
    const navMenu = document.getElementById('navMenu');
    const navBtn  = document.getElementById('navToggle');

    function onScroll() {
        if (!header) return;
        header.classList.toggle('scrolled', window.scrollY > 20);
    }
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();

    if (navBtn && navMenu) {
        navBtn.addEventListener('click', () => {
            const open = navMenu.classList.toggle('open');
            navBtn.classList.toggle('open', open);
            navBtn.setAttribute('aria-expanded', String(open));
            document.body.style.overflow = open ? 'hidden' : '';
        });

        // Tutup menu saat link diklik
        navMenu.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                navMenu.classList.remove('open');
                navBtn.classList.remove('open');
                navBtn.setAttribute('aria-expanded', 'false');
                document.body.style.overflow = '';
            });
        });
    }

    /* ------------------------------------------------------------
       2. REVEAL ON SCROLL
       ------------------------------------------------------------ */
    const revealEls = document.querySelectorAll('.reveal');
    if ('IntersectionObserver' in window) {
        const io = new IntersectionObserver((entries) => {
            entries.forEach((e, i) => {
                if (e.isIntersecting) {
                    setTimeout(() => e.target.classList.add('visible'), i * 60);
                    io.unobserve(e.target);
                }
            });
        }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
        revealEls.forEach(el => io.observe(el));
    } else {
        revealEls.forEach(el => el.classList.add('visible'));
    }

    /* ------------------------------------------------------------
       3. COUNTER ANIMATION
       ------------------------------------------------------------ */
    const counters = document.querySelectorAll('.counter');

    function animateCounter(el) {
        const target = parseFloat(el.dataset.target);
        if (isNaN(target)) return;

        const isFloat   = target % 1 !== 0;
        const duration  = 1400;
        const startTime = performance.now();

        function step(now) {
            const p = Math.min((now - startTime) / duration, 1);
            const eased = 1 - Math.pow(1 - p, 3);
            const value = target * eased;

            el.textContent = isFloat
                ? value.toFixed(1)
                : Math.round(value).toLocaleString('id-ID');

            if (p < 1) requestAnimationFrame(step);
        }
        requestAnimationFrame(step);
    }

    if ('IntersectionObserver' in window) {
        const cio = new IntersectionObserver((entries) => {
            entries.forEach(e => {
                if (e.isIntersecting) {
                    animateCounter(e.target);
                    cio.unobserve(e.target);
                }
            });
        }, { threshold: 0.5 });
        counters.forEach(c => cio.observe(c));
    } else {
        counters.forEach(animateCounter);
    }

    /* ------------------------------------------------------------
       4. HERO CLOCK + LAST UPDATED
       ------------------------------------------------------------ */
    const clockEl = document.getElementById('heroClock');
    const updEl   = document.getElementById('lastUpdated');

    const fmtDate = new Intl.DateTimeFormat('id-ID', {
        day: '2-digit', month: '2-digit', year: 'numeric'
    });

    const fmtDateTime = new Intl.DateTimeFormat('id-ID', {
        day: '2-digit', month: '2-digit', year: 'numeric',
        hour: '2-digit', minute: '2-digit'
    });

    function tick() {
        const now = new Date();
        if (clockEl) {
            clockEl.textContent =
                fmtDate.format(now) + ' — ' + now.toLocaleTimeString('id-ID');
        }
    }

    if (clockEl) {
        tick();
        setInterval(tick, 1000);
    }

    if (updEl) {
        updEl.textContent = fmtDateTime.format(new Date())
            .replace(/\./g, ':');
    }

    /* ------------------------------------------------------------
       5. ACTIVE NAV LINK ON SCROLL
       ------------------------------------------------------------ */
    const sections = document.querySelectorAll('section[id]');
    const navLinks = document.querySelectorAll('.nav-menu ul a');

    if ('IntersectionObserver' in window && sections.length && navLinks.length) {
        const sio = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const id = entry.target.id;
                    navLinks.forEach(a => {
                        a.classList.toggle(
                            'active',
                            a.getAttribute('href') === '#' + id
                        );
                    });
                }
            });
        }, { rootMargin: '-45% 0px -50% 0px' });
        sections.forEach(s => sio.observe(s));
    }

    /* ------------------------------------------------------------
       6. SMOOTH ANCHOR (fallback)
       ------------------------------------------------------------ */
    document.querySelectorAll('a[href^="#"]').forEach(link => {
        link.addEventListener('click', (e) => {
            const id = link.getAttribute('href');
            if (!id || id === '#') return;
            const target = document.querySelector(id);
            if (!target) return;
            e.preventDefault();
            const top = target.getBoundingClientRect().top + window.scrollY - 80;
            window.scrollTo({ top, behavior: 'smooth' });
        });
    });

    /* ------------------------------------------------------------
       7. LOG
       ------------------------------------------------------------ */
    console.log('[AGROTEK] Platform loaded.');
})();