document.addEventListener('DOMContentLoaded', () => {
  const email = document.getElementById('email');
  const password = document.getElementById('password');
  if (email) email.addEventListener('blur', () => validateField(email, validateEmail));
  if (password) password.addEventListener('blur', () => validateField(password, v => v.length > 0));
});

// Front (JS) — tela de login (validacao basica de email/senha)

