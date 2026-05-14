const REGEX = {
  email: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  cpf: /^\d{3}\.\d{3}\.\d{3}-\d{2}$/,
  phone: /^\(\d{2}\) \d{5}-\d{4}$/,
};

document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.password-toggle').forEach((btn) => {
    btn.addEventListener('click', () => {
      const input = document.getElementById(btn.dataset.target);
      if (!input) return;
      const willShow = input.type === 'password';
      input.type = willShow ? 'text' : 'password';
      btn.classList.toggle('showing', willShow);
      btn.setAttribute('aria-label', willShow ? 'Ocultar senha' : 'Mostrar senha');
    });
  });
});

function maskCPF(input) {
  input.addEventListener('input', () => {
    let v = input.value.replace(/\D/g, '');
    if (v.length > 11) v = v.slice(0, 11);
    if (v.length > 9) v = v.replace(/(\d{3})(\d{3})(\d{3})(\d{1,2})/, '$1.$2.$3-$4');
    else if (v.length > 6) v = v.replace(/(\d{3})(\d{3})(\d{1,3})/, '$1.$2.$3');
    else if (v.length > 3) v = v.replace(/(\d{3})(\d{1,3})/, '$1.$2');
    input.value = v;
  });
}

function maskPhone(input) {
  input.addEventListener('input', () => {
    let v = input.value.replace(/\D/g, '');
    if (v.length > 11) v = v.slice(0, 11);
    if (v.length > 6) v = v.replace(/(\d{2})(\d{5})(\d{1,4})/, '($1) $2-$3');
    else if (v.length > 2) v = v.replace(/(\d{2})(\d{1,5})/, '($1) $2');
    input.value = v;
  });
}

function validateField(input, validatorFn) {
  const valid = validatorFn(input.value);
  input.classList.toggle('error', !valid);
  input.classList.toggle('valid', valid);
  return valid;
}

function validateName(v) { return v.trim().length >= 5; }
function validateEmail(v) { return REGEX.email.test(v); }

function validateCPF(value) {
  if (!REGEX.cpf.test(value)) return false;
  const digits = value.replace(/\D/g, '');
  if (/^(\d)\1{10}$/.test(digits)) return false;
  for (const length of [9, 10]) {
    let total = 0;
    for (let i = 0; i < length; i++) total += parseInt(digits[i], 10) * (length + 1 - i);
    let check = (total * 10) % 11;
    if (check === 10) check = 0;
    if (check !== parseInt(digits[length], 10)) return false;
  }
  return true;
}

function validatePhone(value) {
  if (!REGEX.phone.test(value)) return false;
  const ddd = parseInt(value.slice(1, 3), 10);
  return ddd >= 11 && ddd <= 99;
}

function validateBirthDate(value) {
  if (!value) return false;
  const date = new Date(value + 'T00:00:00');
  const today = new Date();
  if (date >= today) return false;
  let age = today.getFullYear() - date.getFullYear();
  const m = today.getMonth() - date.getMonth();
  if (m < 0 || (m === 0 && today.getDate() < date.getDate())) age--;
  return age >= 16;
}

function validatePassword(value) {
  if (!value || value.length < 8) return false;
  return /[A-Z]/.test(value) && /[a-z]/.test(value) && /\d/.test(value) && /[^A-Za-z0-9]/.test(value);
}

// Validacao (front) — regex e mascaras compartilhadas (CPF, telefone, senha, etc)

