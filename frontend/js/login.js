document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('login-form');
  const submitBtn = document.getElementById('submit-btn');
  const fields = {
    email: document.getElementById('email'),
    password: document.getElementById('password'),
  };

  function checkAll() {
    const allValid =
      validateEmail(fields.email.value) &&
      fields.password.value.length > 0;

    submitBtn.disabled = !allValid;
    return allValid;
  }

  fields.email.addEventListener('blur', () => validateField(fields.email, validateEmail));
  fields.password.addEventListener('blur', () => validateField(fields.password, (v) => v.length > 0));

  Object.values(fields).forEach(f => f.addEventListener('input', checkAll));

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    hideAlert('alert');

    if (!checkAll()) return;

    try {
      const res = await fetch(API + '/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: fields.email.value.trim(),
          password: fields.password.value,
        }),
      });

      const data = await res.json();

      if (!res.ok) {
        showAlert('alert', data.detail || 'Email ou senha incorretos');
        return;
      }

      localStorage.setItem('token', data.token);
      localStorage.setItem('user', JSON.stringify(data.user));
      window.location.href = 'dashboard.html';
    } catch {
      showAlert('alert', 'Erro de conexao com o servidor');
    }
  });
});
