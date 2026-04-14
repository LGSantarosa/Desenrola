document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('register-form');
  const submitBtn = document.getElementById('submit-btn');
  const fields = {
    name: document.getElementById('name'),
    email: document.getElementById('email'),
    cpf: document.getElementById('cpf'),
    phone: document.getElementById('phone'),
    birth_date: document.getElementById('birth_date'),
    password: document.getElementById('password'),
  };

  maskCPF(fields.cpf);
  maskPhone(fields.phone);

  function checkAll() {
    const allValid =
      validateName(fields.name.value) &&
      validateEmail(fields.email.value) &&
      validateCPF(fields.cpf.value) &&
      validatePhone(fields.phone.value) &&
      validateBirthDate(fields.birth_date.value) &&
      validatePassword(fields.password.value);

    submitBtn.disabled = !allValid;
    return allValid;
  }

  fields.name.addEventListener('blur', () => validateField(fields.name, validateName));
  fields.email.addEventListener('blur', () => validateField(fields.email, validateEmail));
  fields.cpf.addEventListener('blur', () => validateField(fields.cpf, validateCPF));
  fields.phone.addEventListener('blur', () => validateField(fields.phone, validatePhone));
  fields.birth_date.addEventListener('blur', () => validateField(fields.birth_date, validateBirthDate));
  fields.password.addEventListener('blur', () => validateField(fields.password, validatePassword));

  Object.values(fields).forEach(f => f.addEventListener('input', checkAll));

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    hideAlert('alert');

    if (!checkAll()) return;

    try {
      const res = await fetch(API + '/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: fields.name.value.trim(),
          email: fields.email.value.trim(),
          cpf: fields.cpf.value,
          phone: fields.phone.value,
          birth_date: fields.birth_date.value,
          password: fields.password.value,
        }),
      });

      const data = await res.json();

      if (!res.ok) {
        showAlert('alert', data.detail || 'Erro ao criar conta');
        return;
      }

      localStorage.setItem('token', data.token);
      localStorage.setItem('user', JSON.stringify(data.user));
      window.location.href = '/onboarding';
    } catch {
      showAlert('alert', 'Erro de conexao com o servidor');
    }
  });
});
