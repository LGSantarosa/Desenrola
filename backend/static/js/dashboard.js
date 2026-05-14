document.addEventListener('DOMContentLoaded', () => {
  const postImage = document.getElementById('post-image');
  const addImageBtn = document.getElementById('add-image-btn');
  const imagePreview = document.getElementById('image-preview');
  const previewImg = document.getElementById('preview-img');
  const removeImg = document.getElementById('remove-img');

  if (addImageBtn) addImageBtn.addEventListener('click', () => postImage.click());

  if (postImage) {
    postImage.addEventListener('change', () => {
      const file = postImage.files[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = (e) => {
        previewImg.src = e.target.result;
        imagePreview.style.display = 'block';
      };
      reader.readAsDataURL(file);
    });
  }

  if (removeImg) {
    removeImg.addEventListener('click', () => {
      postImage.value = '';
      imagePreview.style.display = 'none';
    });
  }

  const modal = document.getElementById('confirm-modal');
  const deleteForm = document.getElementById('delete-form');
  const cancel = document.getElementById('confirm-cancel');
  const modalTitle = document.getElementById('confirm-modal-title');
  const modalDesc = document.getElementById('confirm-modal-desc');

  let modalContext = null;
  let modalCommentId = null;

  function openPostDeleteModal(postId) {
    modalContext = 'post';
    modalCommentId = null;
    deleteForm.action = '/posts/' + postId + '/delete';
    modalTitle.textContent = 'Excluir publicacao?';
    modalDesc.innerHTML = 'Essa acao e <strong>irreversivel</strong>. A publicacao sera apagada permanentemente.';
    modal.hidden = false;
    cancel.focus();
  }

  function openCommentDeleteModal(commentId) {
    modalContext = 'comment';
    modalCommentId = commentId;
    deleteForm.action = '/comments/' + commentId + '/delete';
    modalTitle.textContent = 'Excluir comentario?';
    modalDesc.innerHTML = 'Essa acao e <strong>irreversivel</strong>. O comentario sera apagado.';
    modal.hidden = false;
    cancel.focus();
  }

  function closeModal() {
    modal.hidden = true;
    modalContext = null;
    modalCommentId = null;
  }

  document.querySelectorAll('.post-delete-btn').forEach(btn => {
    btn.addEventListener('click', () => openPostDeleteModal(btn.dataset.postId));
  });

  if (cancel) cancel.addEventListener('click', closeModal);
  if (modal) modal.addEventListener('click', (e) => { if (e.target === modal) closeModal(); });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && modal && !modal.hidden) closeModal();
  });

  if (deleteForm) {
    deleteForm.addEventListener('submit', async (e) => {
      if (modalContext !== 'comment') return;
      e.preventDefault();
      const commentEl = document.getElementById('comment-' + modalCommentId);
      const section = commentEl && commentEl.closest('.comments-section');
      try {
        await fetch(deleteForm.action, { method: 'POST', redirect: 'manual' });
        if (commentEl) {
          commentEl.remove();
          updateCommentCount(section, -1);
        }
      } catch (err) {
      } finally {
        closeModal();
      }
    });
  }

  let currentUser = null;
  const userDataEl = document.getElementById('current-user-data');
  if (userDataEl) {
    try { currentUser = JSON.parse(userDataEl.textContent); } catch (e) {}
  }

  function getInitials(name) {
    const parts = (name || '').trim().split(/\s+/);
    const first = parts[0] ? parts[0][0] : '';
    const last = parts.length > 1 ? parts[parts.length - 1][0] : '';
    return (first + last).toUpperCase();
  }

  function buildCommentEl({ id, authorId, authorName, authorAvatar, content, isOwner }) {
    const wrap = document.createElement('div');
    wrap.className = 'comment-item';
    wrap.id = 'comment-' + id;
    const avatarHtml = authorAvatar
      ? `<img src="/uploads/${authorAvatar}" alt="avatar">`
      : getInitials(authorName);
    const deleteBtn = isOwner
      ? `<button type="button" class="comment-delete" data-comment-id="${id}" title="Excluir comentario">x</button>`
      : '';
    wrap.innerHTML = `
      <div class="comment-avatar">${avatarHtml}</div>
      <div class="comment-body">
        <div class="comment-header">
          <a href="/user/${authorId}" class="comment-author">${escapeHtml(authorName)}</a>
          ${deleteBtn}
        </div>
        <div class="comment-content">${escapeHtml(content)}</div>
      </div>
    `;
    return wrap;
  }

  function escapeHtml(s) {
    const div = document.createElement('div');
    div.textContent = s;
    return div.innerHTML;
  }

  function updateCommentCount(section, delta) {
    if (!section) return;
    const card = section.closest('.post-card');
    const countEl = card && card.querySelector('.comment-count span');
    if (countEl) {
      countEl.textContent = Math.max(0, parseInt(countEl.textContent, 10) + delta);
    }
  }

  document.querySelectorAll('.comment-form').forEach(form => {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const input = form.querySelector('input[name="content"]');
      const content = (input.value || '').trim();
      if (!content || !currentUser) return;
      const section = form.closest('.comments-section');
      const list = section.querySelector('.comments-list');

      const fd = new FormData(form);
      try {
        const res = await fetch(form.action, {
          method: 'POST',
          body: fd,
          headers: { 'Accept': 'application/json' },
        });
        if (!res.ok) throw new Error('failed');
        const data = await res.json();
        if (!data || !data.id) throw new Error('no id');

        const el = buildCommentEl({
          id: data.id,
          authorId: currentUser.id,
          authorName: currentUser.name,
          authorAvatar: currentUser.avatar,
          content: content,
          isOwner: true,
        });
        list.appendChild(el);
        wireCommentDelete(el);
        updateCommentCount(section, +1);
        input.value = '';
      } catch (err) {
      }
    });
  });

  function wireCommentDelete(scope) {
    (scope || document).querySelectorAll('.comment-delete').forEach(btn => {
      if (btn.dataset.wired) return;
      btn.dataset.wired = '1';
      btn.addEventListener('click', () => {
        const cid = btn.dataset.commentId;
        openCommentDeleteModal(cid);
      });
    });
  }
  wireCommentDelete();

  document.querySelectorAll('.like-form').forEach(form => {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const btn = form.querySelector('.like-btn');
      const svg = btn.querySelector('svg');
      const countEl = btn.querySelector('span');
      const wasLiked = btn.classList.contains('liked');

      btn.classList.toggle('liked');
      svg.setAttribute('fill', wasLiked ? 'none' : 'currentColor');
      countEl.textContent = parseInt(countEl.textContent, 10) + (wasLiked ? -1 : 1);

      try {
        await fetch(form.action, { method: 'POST', redirect: 'manual' });
      } catch (err) {
        btn.classList.toggle('liked');
        svg.setAttribute('fill', wasLiked ? 'currentColor' : 'none');
        countEl.textContent = parseInt(countEl.textContent, 10) + (wasLiked ? 1 : -1);
      }
    });
  });
});
