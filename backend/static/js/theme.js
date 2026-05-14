function applyTheme(theme) {
  if (theme === 'light') {
    document.documentElement.setAttribute('data-theme', 'light');
  } else {
    document.documentElement.removeAttribute('data-theme');
  }
  localStorage.setItem('theme', theme === 'light' ? 'light' : 'dark');
}

function toggleTheme() {
  const current = document.documentElement.getAttribute('data-theme') === 'light' ? 'light' : 'dark';
  applyTheme(current === 'light' ? 'dark' : 'light');
}

document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.theme-toggle').forEach(function (btn) {
    btn.addEventListener('click', toggleTheme);
  });
});
