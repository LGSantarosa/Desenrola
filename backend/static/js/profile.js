document.addEventListener('DOMContentLoaded', () => {
  if (!requireAuth()) return;
  showNavUser();

  const form = document.getElementById('profile-form');
  const deleteBtn = document.getElementById('delete-btn');
  const logoutBtn = document.getElementById('logout-btn');
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

  async function loadProfile() {
    try {
      const res = await fetch(API + '/users/me', {
        headers: { 'Authorization': 'Bearer ' + getToken() },
      });

      if (!res.ok) {
        logout();
        return;
      }

      const user = await res.json();
      fields.name.value = user.name;
      fields.email.value = user.email;
      fields.cpf.value = user.cpf;
      fields.phone.value = user.phone;
      fields.birth_date.value = user.birth_date;
    } catch {
      showAlert('alert-error', 'Erro ao carregar perfil');
    }
  }

  loadProfile();

  fields.name.addEventListener('blur', () => validateField(fields.name, validateName));
  fields.email.addEventListener('blur', () => validateField(fields.email, validateEmail));
  fields.cpf.addEventListener('blur', () => validateField(fields.cpf, validateCPF));
  fields.phone.addEventListener('blur', () => validateField(fields.phone, validatePhone));
  fields.birth_date.addEventListener('blur', () => validateField(fields.birth_date, validateBirthDate));
  fields.password.addEventListener('blur', () => {
    if (fields.password.value.length > 0) {
      validateField(fields.password, validatePassword);
    } else {
      fields.password.classList.remove('error', 'valid');
    }
  });

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    hideAlert('alert-success');
    hideAlert('alert-error');

    const valid =
      validateField(fields.name, validateName) &&
      validateField(fields.email, validateEmail) &&
      validateField(fields.cpf, validateCPF) &&
      validateField(fields.phone, validatePhone) &&
      validateField(fields.birth_date, validateBirthDate);

    if (fields.password.value.length > 0 && !validatePassword(fields.password.value)) {
      validateField(fields.password, validatePassword);
      return;
    }

    if (!valid) return;

    const body = {
      name: fields.name.value.trim(),
      email: fields.email.value.trim(),
      cpf: fields.cpf.value,
      phone: fields.phone.value,
      birth_date: fields.birth_date.value,
    };

    if (fields.password.value.length > 0) {
      body.password = fields.password.value;
    }

    try {
      const res = await fetch(API + '/users/me', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ' + getToken(),
        },
        body: JSON.stringify(body),
      });

      const data = await res.json();

      if (!res.ok) {
        showAlert('alert-error', data.detail || 'Erro ao salvar');
        return;
      }

      localStorage.setItem('user', JSON.stringify({ id: data.id, name: data.name, role: data.role }));
      showNavUser();
      showAlert('alert-success', 'Perfil atualizado');
    } catch {
      showAlert('alert-error', 'Erro de conexao com o servidor');
    }
  });

  deleteBtn.addEventListener('click', async () => {
    if (!confirm('Tem certeza que quer excluir sua conta? Essa acao nao pode ser desfeita.')) return;

    try {
      const res = await fetch(API + '/users/me', {
        method: 'DELETE',
        headers: { 'Authorization': 'Bearer ' + getToken() },
      });

      if (res.ok) {
        logout();
      } else {
        showAlert('alert-error', 'Erro ao excluir conta');
      }
    } catch {
      showAlert('alert-error', 'Erro de conexao com o servidor');
    }
  });

  logoutBtn.addEventListener('click', (e) => {
    e.preventDefault();
    logout();
  });
});
