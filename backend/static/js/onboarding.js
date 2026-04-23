document.addEventListener('DOMContentLoaded', () => {
  const avatarInput = document.getElementById('avatar-input');
  const avatarBtn = document.getElementById('avatar-btn');
  const avatarPreview = document.getElementById('avatar-preview');
  const avatarForm = document.getElementById('avatar-form');
  const avatarError = document.getElementById('avatar-error');

  avatarBtn.addEventListener('click', () => avatarInput.click());

  avatarInput.addEventListener('change', () => {
    const file = avatarInput.files[0];
    if (!file) return;

    if (file.size > 2 * 1024 * 1024) {
      avatarError.style.display = 'block';
      avatarInput.value = '';
      return;
    }
    avatarError.style.display = 'none';

    const reader = new FileReader();
    reader.onload = (e) => {
      avatarPreview.innerHTML = '<img src="' + e.target.result + '" alt="avatar">';
    };
    reader.readAsDataURL(file);
    avatarForm.submit();
  });

  document.querySelectorAll('.category-header').forEach(h => {
    h.addEventListener('click', () => h.parentElement.classList.toggle('open'));
  });

  document.querySelectorAll('.skill-option').forEach(label => {
    const input = label.querySelector('input[type=checkbox]');
    const color = input.name === 'teaches' ? 'selected-green' : 'selected-orange';
    label.addEventListener('click', (e) => {
      if (e.target.tagName === 'INPUT') return;
      e.preventDefault();
      input.checked = !input.checked;
      label.classList.toggle(color, input.checked);
    });
  });

  const step1 = document.getElementById('step-1');
  const step2Form = document.getElementById('step-2-form');
  const step2 = document.getElementById('step-2');
  const step3 = document.getElementById('step-3');

  document.getElementById('next-1').addEventListener('click', () => {
    step1.classList.add('hidden');
    step2Form.classList.remove('hidden');
  });

  document.getElementById('next-2').addEventListener('click', () => {
    step2.classList.add('hidden');
    step3.classList.remove('hidden');
  });
});
