/* ==========================================================================
   Incidex — Premium Interactions Layer
   Scroll reveals, card tilt, magnetic buttons, counters, parallax
   ========================================================================== */

(function () {
  'use strict';

  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // -----------------------------------------------------------------------
  // Page Load Progress Bar
  // -----------------------------------------------------------------------
  function initProgressBar() {
    if (prefersReducedMotion) return;
    const bar = document.createElement('div');
    bar.className = 'page-progress';
    document.body.prepend(bar);
    bar.addEventListener('animationend', () => bar.remove());
  }

  // -----------------------------------------------------------------------
  // Scroll Reveal (IntersectionObserver)
  // -----------------------------------------------------------------------
  function initScrollReveal() {
    const revealSelectors = '.reveal, .reveal-left, .reveal-right, .reveal-scale, .reveal-blur';
    const elements = document.querySelectorAll(revealSelectors);

    if (!elements.length) return;

    if (prefersReducedMotion) {
      elements.forEach(el => el.classList.add('visible'));
      return;
    }

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          observer.unobserve(entry.target);
        }
      });
    }, {
      threshold: 0.08,
      rootMargin: '0px 0px -40px 0px'
    });

    elements.forEach(el => observer.observe(el));
  }

  // Also handle legacy .animate-on-scroll classes
  function initLegacyScrollReveal() {
    const elements = document.querySelectorAll('.animate-on-scroll:not(.reveal):not(.reveal-left):not(.reveal-right):not(.reveal-scale):not(.reveal-blur)');
    if (!elements.length) return;

    if (prefersReducedMotion) {
      elements.forEach(el => el.classList.add('visible'));
      return;
    }

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1 });

    elements.forEach(el => observer.observe(el));
  }

  // -----------------------------------------------------------------------
  // Card 3D Tilt Effect
  // -----------------------------------------------------------------------
  function initCardTilt() {
    if (prefersReducedMotion) return;
    // Only on non-touch devices
    if (window.matchMedia('(hover: none)').matches) return;

    document.querySelectorAll('.card-tilt').forEach(card => {
      card.addEventListener('mousemove', (e) => {
        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        const centerX = rect.width / 2;
        const centerY = rect.height / 2;
        const rotateX = ((y - centerY) / centerY) * -4; // max 4 degrees
        const rotateY = ((x - centerX) / centerX) * 4;

        card.style.transform = `perspective(800px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-2px)`;
      });

      card.addEventListener('mouseleave', () => {
        card.style.transform = '';
      });
    });
  }

  // -----------------------------------------------------------------------
  // Magnetic Button Effect
  // -----------------------------------------------------------------------
  function initMagneticButtons() {
    if (prefersReducedMotion) return;
    if (window.matchMedia('(hover: none)').matches) return;

    document.querySelectorAll('.btn-magnetic').forEach(btn => {
      btn.addEventListener('mousemove', (e) => {
        const rect = btn.getBoundingClientRect();
        const x = e.clientX - rect.left - rect.width / 2;
        const y = e.clientY - rect.top - rect.height / 2;
        btn.style.transform = `translate(${x * 0.15}px, ${y * 0.15}px)`;
      });

      btn.addEventListener('mouseleave', () => {
        btn.style.transform = '';
      });
    });
  }

  // -----------------------------------------------------------------------
  // Counter Animation on Scroll
  // -----------------------------------------------------------------------
  function initScrollCounters() {
    const counters = document.querySelectorAll('[data-count-to]');
    if (!counters.length) return;

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const el = entry.target;
          const target = parseInt(el.getAttribute('data-count-to'), 10);
          if (isNaN(target)) return;
          animateCounter(el, target);
          observer.unobserve(el);
        }
      });
    }, { threshold: 0.3 });

    counters.forEach(el => observer.observe(el));
  }

  function animateCounter(element, target) {
    if (prefersReducedMotion || target === 0) {
      element.textContent = target.toLocaleString();
      return;
    }

    let current = 0;
    const duration = 1500;
    const steps = 45;
    const increment = target / steps;
    const stepDuration = duration / steps;

    const timer = setInterval(() => {
      current += increment;
      if (current >= target) {
        element.textContent = target.toLocaleString();
        clearInterval(timer);
      } else {
        element.textContent = Math.floor(current).toLocaleString();
      }
    }, stepDuration);
  }

  // -----------------------------------------------------------------------
  // Header Scroll State
  // -----------------------------------------------------------------------
  function initHeaderScroll() {
    const header = document.querySelector('.site-header');
    if (!header) return;

    let ticking = false;
    window.addEventListener('scroll', () => {
      if (!ticking) {
        requestAnimationFrame(() => {
          header.classList.toggle('scrolled', window.scrollY > 20);
          ticking = false;
        });
        ticking = true;
      }
    }, { passive: true });
  }

  // -----------------------------------------------------------------------
  // Hero Text Reveal (word-by-word)
  // -----------------------------------------------------------------------
  function initTextReveal() {
    if (prefersReducedMotion) return;

    document.querySelectorAll('.text-reveal').forEach(el => {
      const text = el.textContent.trim();
      if (!text) return;

      // Preserve any child <br> or <span> structure
      const html = el.innerHTML;
      // Split by spaces, wrap each word
      const words = html.split(/(\s+)/);
      let delay = 0.3; // start delay in seconds

      el.innerHTML = words.map(word => {
        if (/^\s+$/.test(word)) return word;
        // Skip HTML tags
        if (/^</.test(word)) return word;
        delay += 0.06;
        return `<span class="word" style="animation-delay: ${delay}s">${word}</span>`;
      }).join('');
    });
  }

  // -----------------------------------------------------------------------
  // Parallax for Hero Orbs
  // -----------------------------------------------------------------------
  function initParallax() {
    if (prefersReducedMotion) return;

    const orbs = document.querySelectorAll('.hero-orb');
    if (!orbs.length) return;

    let ticking = false;
    window.addEventListener('scroll', () => {
      if (!ticking) {
        requestAnimationFrame(() => {
          const scrollY = window.scrollY;
          orbs.forEach((orb, i) => {
            const speed = 0.05 + i * 0.02;
            orb.style.transform = `translateY(${scrollY * speed}px)`;
          });
          ticking = false;
        });
        ticking = true;
      }
    }, { passive: true });
  }

  // -----------------------------------------------------------------------
  // Nav Scroll Hints (Mobile)
  // -----------------------------------------------------------------------
  function initNavScroll() {
    const nav = document.querySelector('.main-nav');
    if (!nav) return;

    // Prevent the browser from restoring scroll position on this element
    if ('scrollRestoration' in history) history.scrollRestoration = 'manual';

    // Wrap nav in a scroll wrapper so we can overlay fade + buttons
    const wrapper = document.createElement('div');
    wrapper.className = 'nav-scroll-wrapper';
    nav.parentNode.insertBefore(wrapper, nav);
    wrapper.appendChild(nav);

    // Left chevron button
    const btnLeft = document.createElement('button');
    btnLeft.className = 'nav-scroll-btn nav-scroll-btn--left';
    btnLeft.setAttribute('aria-label', 'Scroll navigation left');
    btnLeft.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"></polyline></svg>';

    // Right chevron button
    const btnRight = document.createElement('button');
    btnRight.className = 'nav-scroll-btn nav-scroll-btn--right';
    btnRight.setAttribute('aria-label', 'Scroll navigation right');
    btnRight.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg>';

    wrapper.appendChild(btnLeft);
    wrapper.appendChild(btnRight);

    const SCROLL_AMOUNT = 160;
    btnLeft.addEventListener('click', () => nav.scrollBy({ left: -SCROLL_AMOUNT, behavior: 'smooth' }));
    btnRight.addEventListener('click', () => nav.scrollBy({ left: SCROLL_AMOUNT, behavior: 'smooth' }));

    function updateScrollState() {
      const atStart = nav.scrollLeft <= 2;
      const atEnd = nav.scrollLeft + nav.clientWidth >= nav.scrollWidth - 2;
      btnLeft.classList.toggle('visible', !atStart);
      btnRight.classList.toggle('visible', !atEnd);
      wrapper.classList.toggle('fade-left', !atStart);
      wrapper.classList.toggle('fade-right', !atEnd);
    }

    nav.addEventListener('scroll', updateScrollState, { passive: true });
    window.addEventListener('resize', updateScrollState, { passive: true });

    // On load: scroll active tab into center of nav, or to start if no active tab.
    // We apply the position in both rAF and a setTimeout to override browser
    // scroll-restoration which can fire after DOMContentLoaded.
    function applyInitialScroll() {
      const activeLink = nav.querySelector('.nav-link.active');
      if (activeLink) {
        const linkCenter = activeLink.offsetLeft + activeLink.offsetWidth / 2;
        nav.scrollLeft = Math.max(0, linkCenter - nav.clientWidth / 2);
      } else {
        nav.scrollLeft = 0;
      }
      updateScrollState();
    }

    requestAnimationFrame(applyInitialScroll);

    // Re-apply after browser scroll-restoration has had a chance to run,
    // and again after fonts/layout fully settle.
    setTimeout(applyInitialScroll, 50);
    setTimeout(() => {
      applyInitialScroll();
      // Pulse the right chevron once on mobile to hint at scrollability
      if (window.innerWidth <= 1024 && nav.scrollWidth > nav.clientWidth) {
        btnRight.classList.add('nav-scroll-btn--hint');
        setTimeout(() => btnRight.classList.remove('nav-scroll-btn--hint'), 1500);
      }
    }, 200);
  }

  // -----------------------------------------------------------------------
  // Init All
  // -----------------------------------------------------------------------
  function init() {
    initProgressBar();
    initScrollReveal();
    initLegacyScrollReveal();
    initCardTilt();
    initMagneticButtons();
    initScrollCounters();
    initHeaderScroll();
    initTextReveal();
    initParallax();
    initNavScroll();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
