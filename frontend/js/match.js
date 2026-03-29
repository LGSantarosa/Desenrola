document.addEventListener('DOMContentLoaded', async () => {
  if (!requireAuth()) return;
  showNavUser();

  const token = getToken();
  const headers = { 'Authorization': 'Bearer ' + token };

  document.getElementById('logout-btn').addEventListener('click', () => logout());

  const stack = document.getElementById('match-stack');
  const actions = document.getElementById('match-actions');
  const emptyEl = document.getElementById('match-empty');
  const skipBtn = document.getElementById('skip-btn');
  const likeBtn = document.getElementById('like-btn');

  let people = [];
  let currentIndex = 0;
  let swiping = false;
  let skipped = JSON.parse(sessionStorage.getItem('match-skipped') || '[]');

  const res = await fetch(API + '/feed/', { headers });
  const allPeople = await res.json();
  people = allPeople.filter(p => !skipped.includes(p.user.id));

  if (people.length === 0) {
    showEmpty();
  } else {
    renderCards();
  }

  skipBtn.addEventListener('click', () => { if (!swiping) swipeCard('left'); });
  likeBtn.addEventListener('click', () => { if (!swiping) swipeCard('right'); });

  function renderCards() {
    stack.innerHTML = '';

    if (currentIndex >= people.length) {
      showEmpty();
      return;
    }

    if (currentIndex + 1 < people.length) {
      const behind = createCard(people[currentIndex + 1]);
      behind.style.transform = 'scale(0.95) translateY(12px)';
      behind.style.opacity = '0.5';
      behind.style.pointerEvents = 'none';
      stack.appendChild(behind);
    }

    const top = createCard(people[currentIndex]);
    stack.appendChild(top);
    setupDrag(top);
  }

  function createCard(person) {
    const initials = person.user.name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2);
    const avatarContent = person.user.avatar
      ? '<img src="' + API + '/uploads/' + person.user.avatar + '" alt="avatar">'
      : initials;

    let badgeHTML = '';
    if (person.score === 3) {
      badgeHTML = '<span class="match-card-badge perfect">Match perfeito</span>';
    } else if (person.score === 2) {
      badgeHTML = '<span class="match-card-badge partial">Match parcial</span>';
    } else {
      badgeHTML = '<span class="match-card-badge none">Sem match direto</span>';
    }

    const teachTags = person.teaches.map(s =>
      '<span class="tag tag-green">' + s.name + '</span>'
    ).join('');

    const learnTags = person.learns.map(s =>
      '<span class="tag tag-orange">' + s.name + '</span>'
    ).join('');

    const card = document.createElement('div');
    card.className = 'match-card';
    card.innerHTML =
      '<div class="match-card-overlay like">MATCH</div>' +
      '<div class="match-card-overlay nope">NOPE</div>' +
      '<div class="match-card-avatar">' + avatarContent + '</div>' +
      '<div class="match-card-name"><a href="user.html?id=' + person.user.id + '">' + person.user.name + '</a></div>' +
      badgeHTML +
      '<div class="match-card-section">' +
        '<div class="match-card-label green">Ensina</div>' +
        '<div class="match-card-tags">' + (teachTags || '<span style="color:var(--gray);font-size:12px">Nenhuma</span>') + '</div>' +
      '</div>' +
      '<div class="match-card-section">' +
        '<div class="match-card-label orange">Quer aprender</div>' +
        '<div class="match-card-tags">' + (learnTags || '<span style="color:var(--gray);font-size:12px">Nenhuma</span>') + '</div>' +
      '</div>';

    return card;
  }

  function setupDrag(card) {
    let startX = 0;
    let currentX = 0;
    let isDragging = false;

    const likeOverlay = card.querySelector('.match-card-overlay.like');
    const nopeOverlay = card.querySelector('.match-card-overlay.nope');

    card.addEventListener('mousedown', onStart);
    card.addEventListener('touchstart', onStart, { passive: true });

    function onStart(e) {
      if (swiping) return;
      isDragging = true;
      startX = e.type === 'touchstart' ? e.touches[0].clientX : e.clientX;
      card.classList.add('dragging');

      document.addEventListener('mousemove', onMove);
      document.addEventListener('mouseup', onEnd);
      document.addEventListener('touchmove', onMove, { passive: true });
      document.addEventListener('touchend', onEnd);
    }

    function onMove(e) {
      if (!isDragging) return;
      const x = e.type === 'touchmove' ? e.touches[0].clientX : e.clientX;
      currentX = x - startX;

      const rotate = currentX * 0.08;
      card.style.transform = 'translateX(' + currentX + 'px) rotate(' + rotate + 'deg)';

      const progress = Math.min(Math.abs(currentX) / 100, 1);
      if (currentX > 0) {
        likeOverlay.style.opacity = progress;
        nopeOverlay.style.opacity = 0;
      } else {
        nopeOverlay.style.opacity = progress;
        likeOverlay.style.opacity = 0;
      }
    }

    function onEnd() {
      isDragging = false;
      card.classList.remove('dragging');

      document.removeEventListener('mousemove', onMove);
      document.removeEventListener('mouseup', onEnd);
      document.removeEventListener('touchmove', onMove);
      document.removeEventListener('touchend', onEnd);

      if (Math.abs(currentX) > 100) {
        swipeCard(currentX > 0 ? 'right' : 'left');
      } else {
        card.style.transform = '';
        likeOverlay.style.opacity = 0;
        nopeOverlay.style.opacity = 0;
      }
      currentX = 0;
    }
  }

  function swipeCard(direction) {
    swiping = true;
    const topCard = stack.lastElementChild;
    if (!topCard) return;

    topCard.classList.add(direction === 'right' ? 'swipe-right' : 'swipe-left');

    const person = people[currentIndex];

    if (direction === 'right' && person) {
      proposeMatch(person);
    }

    if (direction === 'left' && person) {
      skipped.push(person.user.id);
      sessionStorage.setItem('match-skipped', JSON.stringify(skipped));
    }

    setTimeout(() => {
      currentIndex++;
      swiping = false;
      renderCards();
    }, 400);
  }

  async function proposeMatch(person) {
    const mySkillsRes = await fetch(API + '/skills/me', { headers });
    const mySkills = await mySkillsRes.json();

    const myTeachIds = mySkills.teaches.map(s => s.skill_id);
    const myLearnIds = mySkills.learns.map(s => s.skill_id);

    const theirLearns = person.learns.map(s => s.id);
    const theirTeaches = person.teaches.map(s => s.id);

    const offeredId = myTeachIds.find(id => theirLearns.includes(id));
    const desiredId = myLearnIds.find(id => theirTeaches.includes(id));

    if (!offeredId || !desiredId) return;

    await fetch(API + '/swaps/?receiver_id=' + person.user.id +
      '&offered_skill_id=' + offeredId +
      '&desired_skill_id=' + desiredId, {
      method: 'POST',
      headers,
    });
  }

  function showEmpty() {
    stack.innerHTML = '';
    actions.style.display = 'none';
    emptyEl.style.display = 'block';
  }
});
