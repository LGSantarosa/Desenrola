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

  function openModal(postId) {
    deleteForm.action = '/posts/' + postId + '/delete';
    modal.hidden = false;
    cancel.focus();
  }

  function closeModal() {
    modal.hidden = true;
  }

  document.querySelectorAll('.post-delete-btn').forEach(btn => {
    btn.addEventListener('click', () => openModal(btn.dataset.postId));
  });

  if (cancel) cancel.addEventListener('click', closeModal);
  if (modal) modal.addEventListener('click', (e) => { if (e.target === modal) closeModal(); });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && modal && !modal.hidden) closeModal();
  });
});

// Front (JS) — feed: preview de imagem ao postar e modal de confirmacao de exclusao

