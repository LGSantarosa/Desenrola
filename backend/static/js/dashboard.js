document.addEventListener('DOMContentLoaded', async () => {
  if (!requireAuth()) return;
  showNavUser();

  const token = getToken();
  const headers = { 'Authorization': 'Bearer ' + token };

  document.getElementById('logout-btn').addEventListener('click', (e) => {
    e.preventDefault();
    logout();
  });

  setupPosts(headers);
  setupDiscover(headers);
});

function setupPosts(headers) {
  const token = getToken();
  const postContent = document.getElementById('post-content');
  const postImage = document.getElementById('post-image');
  const postBtn = document.getElementById('post-btn');
  const addImageBtn = document.getElementById('add-image-btn');
  const imagePreview = document.getElementById('image-preview');
  const previewImg = document.getElementById('preview-img');
  const removeImg = document.getElementById('remove-img');

  let selectedFile = null;

  addImageBtn.addEventListener('click', () => postImage.click());

  postImage.addEventListener('change', () => {
    const file = postImage.files[0];
    if (!file) return;
    selectedFile = file;
    const reader = new FileReader();
    reader.onload = (e) => {
      previewImg.src = e.target.result;
      imagePreview.style.display = 'block';
    };
    reader.readAsDataURL(file);
  });

  removeImg.addEventListener('click', () => {
    selectedFile = null;
    postImage.value = '';
    imagePreview.style.display = 'none';
  });

  postBtn.addEventListener('click', async () => {
    const content = postContent.value.trim();
    if (!content) return;

    const formData = new FormData();
    formData.append('content', content);
    if (selectedFile) formData.append('image', selectedFile);

    const res = await fetch(API + '/posts/', {
      method: 'POST',
      headers: { 'Authorization': 'Bearer ' + token },
      body: formData,
    });

    if (res.ok) {
      postContent.value = '';
      selectedFile = null;
      postImage.value = '';
      imagePreview.style.display = 'none';
      loadPosts();
    }
  });

  loadPosts();

  async function loadPosts() {
    const container = document.getElementById('posts-feed');
    container.innerHTML = '';

    const res = await fetch(API + '/posts/', {
      headers: { 'Authorization': 'Bearer ' + token },
    });
    const posts = await res.json();

    if (posts.length === 0) {
      container.innerHTML = '<div class="empty-state">Nenhuma publicacao ainda. Seja o primeiro!</div>';
      return;
    }

    posts.forEach(post => {
      const initials = post.author.name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2);
      const avatarHTML = post.author.avatar
        ? '<img src="' + API + '/uploads/' + post.author.avatar + '" alt="avatar">'
        : initials;

      const date = new Date(post.created_at);
      const timeStr = date.toLocaleDateString('pt-BR') + ' ' + date.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });

      let imageHTML = '';
      if (post.image) {
        imageHTML = '<img class="post-image" src="' + API + '/uploads/' + post.image + '" alt="post">';
      }

      const card = document.createElement('div');
      card.className = 'post-card';
      card.innerHTML =
        '<div class="post-header">' +
          '<div class="post-avatar">' + avatarHTML + '</div>' +
          '<div>' +
            '<div class="post-author"><a href="/user?id=' + post.author.id + '">' + post.author.name + '</a></div>' +
            '<div class="post-time">' + timeStr + '</div>' +
          '</div>' +
        '</div>' +
        '<div class="post-content">' + post.content + '</div>' +
        imageHTML;

      container.appendChild(card);
    });
  }
}

async function setupDiscover(headers) {
  let categories = [];
  try {
    const res = await fetch(API + '/skills/categories');
    categories = await res.json();
  } catch {
    return;
  }

  const filtersEl = document.getElementById('filters');
  let activeFilter = null;

  const allBtn = document.createElement('button');
  allBtn.className = 'filter-btn active';
  allBtn.textContent = 'Todas';
  allBtn.addEventListener('click', () => {
    activeFilter = null;
    setActiveFilter(allBtn);
    loadFeed();
  });
  filtersEl.appendChild(allBtn);

  categories.forEach(cat => {
    const btn = document.createElement('button');
    btn.className = 'filter-btn';
    btn.textContent = cat.name;
    btn.addEventListener('click', () => {
      activeFilter = cat.id;
      setActiveFilter(btn);
      loadFeed();
    });
    filtersEl.appendChild(btn);
  });

  function setActiveFilter(activeBtn) {
    filtersEl.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    activeBtn.classList.add('active');
  }

  async function loadFeed() {
    const feedEl = document.getElementById('discover-feed');
    feedEl.innerHTML = '';

    let url = API + '/feed/';
    if (activeFilter) url += '?category_id=' + activeFilter;

    const res = await fetch(url, { headers });
    const people = await res.json();

    if (people.length === 0) {
      feedEl.innerHTML = '<div class="empty-state">Nenhuma pessoa encontrada.</div>';
      return;
    }

    people.forEach(person => {
      const initials = person.user.name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2);
      const avatarHTML = person.user.avatar
        ? '<img src="' + API + '/uploads/' + person.user.avatar + '" alt="avatar">'
        : initials;

      let badgeHTML = '';
      if (person.score === 3) {
        badgeHTML = '<span class="feed-match-badge perfect">Match</span>';
      } else if (person.score === 2) {
        badgeHTML = '<span class="feed-match-badge partial">Parcial</span>';
      }

      const teachTags = person.teaches.map(s =>
        '<span class="tag tag-green">' + s.name + '</span>'
      ).join('');

      const learnTags = person.learns.map(s =>
        '<span class="tag tag-orange">' + s.name + '</span>'
      ).join('');

      const card = document.createElement('div');
      card.className = 'feed-card';
      card.innerHTML =
        '<div class="feed-card-top">' +
          '<div class="feed-avatar">' + avatarHTML + '</div>' +
          '<div class="feed-name"><a href="/user?id=' + person.user.id + '">' + person.user.name + '</a></div>' +
          badgeHTML +
        '</div>' +
        '<div class="feed-skills">' +
          '<span class="feed-label green">Ensina</span>' +
          '<div class="feed-tags">' + teachTags + '</div>' +
        '</div>' +
        '<div class="feed-skills">' +
          '<span class="feed-label orange">Quer</span>' +
          '<div class="feed-tags">' + learnTags + '</div>' +
        '</div>' +
        '<div class="feed-card-bottom">' +
          '<button class="btn btn-green propose-btn" data-user-id="' + person.user.id + '" ' +
            'data-teaches="' + person.teaches.map(s => s.id).join(',') + '" ' +
            'data-learns="' + person.learns.map(s => s.id).join(',') + '">' +
            'Propor troca</button>' +
        '</div>';

      feedEl.appendChild(card);
    });

    feedEl.querySelectorAll('.propose-btn').forEach(btn => {
      btn.addEventListener('click', () => proposeSwap(btn, headers));
    });
  }

  loadFeed();
}

async function proposeSwap(btn, headers) {
  const receiverId = btn.dataset.userId;
  const theirLearns = btn.dataset.learns.split(',').map(Number);
  const theirTeaches = btn.dataset.teaches.split(',').map(Number);

  const mySkillsRes = await fetch(API + '/skills/me', { headers });
  const mySkills = await mySkillsRes.json();

  const myTeachIds = mySkills.teaches.map(s => s.skill_id);
  const myLearnIds = mySkills.learns.map(s => s.skill_id);

  const offeredId = myTeachIds.find(id => theirLearns.includes(id));
  const desiredId = myLearnIds.find(id => theirTeaches.includes(id));

  if (!offeredId || !desiredId) {
    btn.textContent = 'Sem match';
    btn.disabled = true;
    return;
  }

  const res = await fetch(API + '/swaps/?receiver_id=' + receiverId +
    '&offered_skill_id=' + offeredId +
    '&desired_skill_id=' + desiredId, {
    method: 'POST',
    headers,
  });

  const data = await res.json();
  if (res.ok) {
    btn.textContent = 'Enviado!';
    btn.disabled = true;
  } else {
    btn.textContent = data.detail || 'Erro';
    setTimeout(() => { btn.textContent = 'Propor troca'; btn.disabled = false; }, 2000);
  }
}
