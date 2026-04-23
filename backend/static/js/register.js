document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('register-form') || document.querySelector('form[action="/auth/register"]');
  const fields = {
    name: document.getElementById('name'),
    email: document.getElementById('email'),
    cpf: document.getElementById('cpf'),
    phone: document.getElementById('phone'),
    birth_date: document.getElementById('birth_date'),
    password: document.getElementById('password'),
  };

  if (fields.cpf) maskCPF(fields.cpf);
  if (fields.phone) maskPhone(fields.phone);

  if (fields.name) fields.name.addEventListener('blur', () => validateField(fields.name, validateName));
  if (fields.email) fields.email.addEventListener('blur', () => validateField(fields.email, validateEmail));
  if (fields.cpf) fields.cpf.addEventListener('blur', () => validateField(fields.cpf, validateCPF));
  if (fields.phone) fields.phone.addEventListener('blur', () => validateField(fields.phone, validatePhone));
  if (fields.birth_date) fields.birth_date.addEventListener('blur', () => validateField(fields.birth_date, validateBirthDate));
  if (fields.password) fields.password.addEventListener('blur', () => validateField(fields.password, validatePassword));

  if (form) {
    form.addEventListener('submit', (e) => {
      const valid =
        validateField(fields.name, validateName) &&
        validateField(fields.email, validateEmail) &&
        validateField(fields.cpf, validateCPF) &&
        validateField(fields.phone, validatePhone) &&
        validateField(fields.birth_date, validateBirthDate) &&
        validateField(fields.password, validatePassword);
      if (!valid) e.preventDefault();
    });
  }
});
