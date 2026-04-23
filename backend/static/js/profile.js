document.addEventListener('DOMContentLoaded', () => {
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

  fields.name.addEventListener('blur', () => validateField(fields.name, validateName));
  fields.email.addEventListener('blur', () => validateField(fields.email, validateEmail));
  fields.cpf.addEventListener('blur', () => validateField(fields.cpf, validateCPF));
  fields.phone.addEventListener('blur', () => validateField(fields.phone, validatePhone));
  fields.birth_date.addEventListener('blur', () => validateField(fields.birth_date, validateBirthDate));
  fields.password.addEventListener('blur', () => {
    if (fields.password.value.length > 0) validateField(fields.password, validatePassword);
    else fields.password.classList.remove('error', 'valid');
  });

  const form = document.getElementById('profile-form');
  form.addEventListener('submit', (e) => {
    const valid =
      validateField(fields.name, validateName) &&
      validateField(fields.email, validateEmail) &&
      validateField(fields.cpf, validateCPF) &&
      validateField(fields.phone, validatePhone) &&
      validateField(fields.birth_date, validateBirthDate);
    const pwValid = fields.password.value.length === 0 || validatePassword(fields.password.value);
    if (!pwValid) {
      validateField(fields.password, validatePassword);
    }
    if (!valid || !pwValid) e.preventDefault();
  });

  const modal = document.getElementById('confirm-modal');
  const deleteBtn = document.getElementById('delete-btn');
  const cancel = document.getElementById('confirm-cancel');

  function openModal() { modal.hidden = false; cancel.focus(); }
  function closeModal() { modal.hidden = true; deleteBtn.focus(); }

  deleteBtn.addEventListener('click', openModal);
  cancel.addEventListener('click', closeModal);
  modal.addEventListener('click', (e) => { if (e.target === modal) closeModal(); });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && !modal.hidden) closeModal();
  });
});
