document.addEventListener('DOMContentLoaded', () => {
  initScrollReveal();
  initNavScroll();
  initMobileMenu();
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

function initMobileMenu() {
  const toggle = document.getElementById('mobile-toggle');
  const nav = document.querySelector('nav');
  if (!toggle || !nav) return;

  toggle.addEventListener('click', () => {
    nav.classList.toggle('menu-open');
  });

  nav.querySelectorAll('.nav-links a').forEach((a) => {
    a.addEventListener('click', () => nav.classList.remove('menu-open'));
  });
}
