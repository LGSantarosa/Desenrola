document.addEventListener('DOMContentLoaded', () => {
  const email = document.getElementById('email');
  const password = document.getElementById('password');
  if (email) email.addEventListener('blur', () => validateField(email, validateEmail));
  if (password) password.addEventListener('blur', () => validateField(password, v => v.length > 0));
});
