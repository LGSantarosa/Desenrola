document.addEventListener('DOMContentLoaded', async () => {
  if (!requireAuth()) return;
  showNavUser();

  const user = getUser();
  const initials = user.name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2);
  document.getElementById('avatar-initials').textContent = initials;

  const avatarInput = document.getElementById('avatar-input');
  const avatarBtn = document.getElementById('avatar-btn');
  const avatarPreview = document.getElementById('avatar-preview');

  avatarBtn.addEventListener('click', () => avatarInput.click());

  avatarInput.addEventListener('change', () => {
    const file = avatarInput.files[0];
    if (!file) return;

    if (file.size > 2 * 1024 * 1024) {
      alert('Imagem deve ter no maximo 2MB');
      return;
    }

    const reader = new FileReader();
    reader.onload = async (e) => {
      avatarPreview.innerHTML = '<img src="' + e.target.result + '" alt="avatar">';

      const formData = new FormData();
      formData.append('file', file);

      await fetch(API + '/upload/avatar', {
        method: 'POST',
        headers: { 'Authorization': 'Bearer ' + getToken() },
        body: formData,
      });
    };
    reader.readAsDataURL(file);
  });

  let categories = [];
  try {
    const res = await fetch(API + '/skills/categories');
    categories = await res.json();
  } catch {
    return;
  }

  const teachesSelected = new Set();
  const learnsSelected = new Set();

  function renderCategories(containerId, selectedSet, colorClass) {
    const container = document.getElementById(containerId);
    container.innerHTML = '';

    categories.forEach(cat => {
      const group = document.createElement('div');
      group.className = 'category-group';

      const header = document.createElement('div');
      header.className = 'category-header';
      header.innerHTML = '<span>' + cat.name + '</span><span class="arrow">&#9654;</span>';
      header.addEventListener('click', () => group.classList.toggle('open'));

      const skillsDiv = document.createElement('div');
      skillsDiv.className = 'category-skills';

      cat.skills.forEach(skill => {
        const btn = document.createElement('button');
        btn.className = 'skill-option';
        btn.textContent = skill.name;
        btn.type = 'button';

        btn.addEventListener('click', () => {
          if (selectedSet.has(skill.id)) {
            selectedSet.delete(skill.id);
            btn.classList.remove(colorClass);
          } else {
            selectedSet.add(skill.id);
            btn.classList.add(colorClass);
          }
          updateSelectedDisplay(selectedSet, colorClass, categories);
          updateButtons();
        });

        skillsDiv.appendChild(btn);
      });

      group.appendChild(header);
      group.appendChild(skillsDiv);
      container.appendChild(group);
    });
  }

  function updateSelectedDisplay(selectedSet, colorClass, categories) {
    const tagColor = colorClass === 'selected-green' ? 'green' : 'orange';
    const containerId = colorClass === 'selected-green' ? 'teaches-selected' : 'learns-selected';
    const container = document.getElementById(containerId);
    container.innerHTML = '';

    const allSkills = categories.flatMap(c => c.skills);
    selectedSet.forEach(id => {
      const skill = allSkills.find(s => s.id === id);
      if (skill) {
        const tag = document.createElement('span');
        tag.className = 'selected-tag ' + tagColor;
        tag.textContent = skill.name;
        container.appendChild(tag);
      }
    });
  }

  function updateButtons() {
    document.getElementById('next-2').disabled = teachesSelected.size === 0;
    document.getElementById('finish-btn').disabled = learnsSelected.size === 0;
  }

  renderCategories('teaches-list', teachesSelected, 'selected-green');
  renderCategories('learns-list', learnsSelected, 'selected-orange');

  document.getElementById('next-1').addEventListener('click', () => {
    document.getElementById('step-1').classList.add('hidden');
    document.getElementById('step-2').classList.remove('hidden');
  });

  document.getElementById('skip-1').addEventListener('click', () => {
    document.getElementById('step-1').classList.add('hidden');
    document.getElementById('step-2').classList.remove('hidden');
  });

  document.getElementById('next-2').addEventListener('click', () => {
    document.getElementById('step-2').classList.add('hidden');
    document.getElementById('step-3').classList.remove('hidden');
  });

  document.getElementById('finish-btn').addEventListener('click', async () => {
    const token = getToken();
    const headers = {
      'Authorization': 'Bearer ' + token,
      'Content-Type': 'application/json',
    };

    for (const skillId of teachesSelected) {
      await fetch(API + '/skills/me?skill_id=' + skillId + '&type=teaches', {
        method: 'POST',
        headers,
      });
    }

    for (const skillId of learnsSelected) {
      await fetch(API + '/skills/me?skill_id=' + skillId + '&type=learns', {
        method: 'POST',
        headers,
      });
    }

    window.location.href = '/dashboard';
  });
});
