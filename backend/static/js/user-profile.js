document.addEventListener('DOMContentLoaded', async () => {
  if (!requireAuth()) return;
  showNavUser();

  document.getElementById('logout-btn').addEventListener('click', (e) => {
    e.preventDefault();
    logout();
  });

  const params = new URLSearchParams(window.location.search);
  const userId = params.get('id');

  if (!userId) {
    window.location.href = '/dashboard';
    return;
  }

  const token = getToken();
  const headers = { 'Authorization': 'Bearer ' + token };

  try {
    const res = await fetch(API + '/users/' + userId, { headers });
    if (!res.ok) {
      document.getElementById('user-card').innerHTML = '<div style="text-align:center;color:var(--gray);padding:40px">Usuario nao encontrado.</div>';
      return;
    }

    const user = await res.json();
    const initials = user.name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2);
    const avatarHTML = user.avatar
      ? '<img src="' + API + '/uploads/' + user.avatar + '" alt="avatar">'
      : initials;

    const teachTags = user.teaches.map(s => '<span class="tag tag-green">' + s + '</span>').join('');
    const learnTags = user.learns.map(s => '<span class="tag tag-orange">' + s + '</span>').join('');

    document.getElementById('user-card').innerHTML =
      '<div class="user-avatar-large">' + avatarHTML + '</div>' +
      '<div class="user-name-large">' + user.name + '</div>' +
      '<div class="user-skills-section">' +
        '<div class="user-skills-label green">Ensina</div>' +
        '<div class="user-skills-tags">' + (teachTags || '<span style="color:var(--gray);font-size:13px">Nenhuma</span>') + '</div>' +
      '</div>' +
      '<div class="user-skills-section">' +
        '<div class="user-skills-label orange">Quer aprender</div>' +
        '<div class="user-skills-tags">' + (learnTags || '<span style="color:var(--gray);font-size:13px">Nenhuma</span>') + '</div>' +
      '</div>' +
      '<div class="user-actions">' +
        '<button class="btn btn-green btn-full" id="propose-btn">Propor troca</button>' +
      '</div>';

    document.getElementById('propose-btn').addEventListener('click', async () => {
      const btn = document.getElementById('propose-btn');
      const mySkillsRes = await fetch(API + '/skills/me', { headers });
      const mySkills = await mySkillsRes.json();

      const catsRes = await fetch(API + '/skills/categories');
      const cats = await catsRes.json();
      const allSkills = cats.flatMap(c => c.skills);

      const myTeachIds = mySkills.teaches.map(s => s.skill_id);
      const myLearnIds = mySkills.learns.map(s => s.skill_id);

      const theirTeachIds = user.teaches.map(name => {
        const s = allSkills.find(sk => sk.name === name);
        return s ? s.id : null;
      }).filter(Boolean);

      const theirLearnIds = user.learns.map(name => {
        const s = allSkills.find(sk => sk.name === name);
        return s ? s.id : null;
      }).filter(Boolean);

      const offeredId = myTeachIds.find(id => theirLearnIds.includes(id));
      const desiredId = myLearnIds.find(id => theirTeachIds.includes(id));

      if (!offeredId || !desiredId) {
        btn.textContent = 'Sem match compativel';
        btn.disabled = true;
        return;
      }

      const res = await fetch(API + '/swaps/?receiver_id=' + userId +
        '&offered_skill_id=' + offeredId +
        '&desired_skill_id=' + desiredId, {
        method: 'POST',
        headers,
      });

      const data = await res.json();
      if (res.ok) {
        btn.textContent = 'Solicitacao enviada!';
        btn.disabled = true;
      } else {
        btn.textContent = data.detail || 'Erro';
      }
    });

  } catch {
    document.getElementById('user-card').innerHTML = '<div style="text-align:center;color:var(--gray);padding:40px">Erro ao carregar perfil.</div>';
  }
});
