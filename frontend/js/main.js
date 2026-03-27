document.addEventListener('DOMContentLoaded', () => {
  initScrollReveal();
  initNavScroll();
  initStatCounters();
});

function initScrollReveal() {
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
        }
      });
    },
    { threshold: 0.1, rootMargin: '0px 0px -30px 0px' }
  );

  document.querySelectorAll('.reveal').forEach((el) => observer.observe(el));
}

function initNavScroll() {
  const nav = document.querySelector('nav');

  window.addEventListener('scroll', () => {
    nav.classList.toggle('scrolled', window.scrollY > 50);
  });
}

function initStatCounters() {
  const DURATION_MS = 1800;

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;

        const el = entry.target;
        const target = parseInt(el.dataset.target, 10);
        const startTime = performance.now();

        function updateCounter(currentTime) {
          const elapsed = currentTime - startTime;
          const progress = Math.min(elapsed / DURATION_MS, 1);
          const eased = 1 - Math.pow(1 - progress, 4);
          const currentValue = Math.floor(eased * target);

          el.textContent = currentValue.toLocaleString('pt-BR') + '+';

          if (progress < 1) {
            requestAnimationFrame(updateCounter);
          }
        }

        requestAnimationFrame(updateCounter);
        observer.unobserve(el);
      });
    },
    { threshold: 0.5 }
  );

  document.querySelectorAll('[data-target]').forEach((el) => observer.observe(el));
}
