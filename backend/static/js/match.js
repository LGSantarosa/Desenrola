document.addEventListener('DOMContentLoaded', () => {
  const stack = document.getElementById('match-stack');
  const actions = document.getElementById('match-actions');
  const emptyEl = document.getElementById('match-empty');
  const skipBtn = document.getElementById('skip-btn');
  const likeBtn = document.getElementById('like-btn');

  const modal = document.getElementById('swap-modal');
  const modalContent = document.getElementById('swap-modal-content');
  const modalEmpty = document.getElementById('swap-modal-empty');
  const modalEmptyText = document.getElementById('swap-modal-empty-text');
  const modalEmptyLink = document.getElementById('swap-modal-empty-link');
  const modalOffered = document.getElementById('swap-modal-offered');
  const modalDesired = document.getElementById('swap-modal-desired');
  const modalCancel = document.getElementById('swap-modal-cancel');
  const modalConfirm = document.getElementById('swap-modal-confirm');

  const myTeachesEl = document.getElementById('my-teaches-data');
  const myTeaches = myTeachesEl ? JSON.parse(myTeachesEl.textContent || '[]') : [];

  if (!stack) return;

  const cards = Array.from(stack.querySelectorAll('.match-card'));
  const skipped = JSON.parse(sessionStorage.getItem('match-skipped') || '[]');

  cards.forEach(c => {
    if (skipped.includes(c.dataset.userId)) c.remove();
  });

  let remaining = Array.from(stack.querySelectorAll('.match-card'));
  let currentIndex = remaining.length - 1;
  let swiping = false;

  function showEmpty() {
    if (actions) actions.style.display = 'none';
    if (emptyEl) emptyEl.style.display = 'block';
  }

  function refreshStack() {
    remaining.forEach((c, i) => {
      if (i < currentIndex - 1) {
        c.style.display = 'none';
      } else if (i === currentIndex - 1) {
        c.style.display = '';
        c.style.transform = 'scale(0.95) translateY(12px)';
        c.style.opacity = '0.5';
        c.style.pointerEvents = 'none';
      } else if (i === currentIndex) {
        c.style.display = '';
        c.style.transform = '';
        c.style.opacity = '';
        c.style.pointerEvents = '';
      } else {
        c.style.display = 'none';
      }
    });

    if (currentIndex < 0) showEmpty();
  }

  function fillSelect(select, items, preselectedId) {
    select.innerHTML = '';
    items.forEach(s => {
      const opt = document.createElement('option');
      opt.value = s.id;
      opt.textContent = s.name;
      if (preselectedId && String(s.id) === String(preselectedId)) opt.selected = true;
      select.appendChild(opt);
    });
  }

  function showEmptyModal(message, showOnboardingLink) {
    modalContent.hidden = true;
    modalEmpty.hidden = false;
    modalEmptyText.textContent = message;
    modalEmptyLink.style.display = showOnboardingLink ? '' : 'none';
    modalConfirm.style.display = 'none';
    modalCancel.textContent = 'Fechar';
  }

  function showFormModal() {
    modalContent.hidden = false;
    modalEmpty.hidden = true;
    modalConfirm.style.display = '';
    modalCancel.textContent = 'Cancelar';
  }

  function openModal(card) {
    const theirTeaches = JSON.parse(card.dataset.theirTeaches || '[]');
    const offeredPre = card.dataset.offered || '';
    const desiredPre = card.dataset.desired || '';

    modal.dataset.userId = card.dataset.userId;
    modal.hidden = false;

    if (myTeaches.length === 0) {
      showEmptyModal('Voce ainda nao cadastrou nenhuma habilidade que ensina. Cadastre antes de propor uma troca.', true);
      return;
    }
    if (theirTeaches.length === 0) {
      showEmptyModal('Esta pessoa ainda nao cadastrou habilidades que ensina. Tente outra.', false);
      return;
    }

    showFormModal();
    fillSelect(modalOffered, myTeaches, offeredPre);
    fillSelect(modalDesired, theirTeaches, desiredPre);
    modalConfirm.disabled = false;
  }

  function closeModal() {
    modal.hidden = true;
  }

  async function submitSwap(receiverId, offeredId, desiredId) {
    const fd = new FormData();
    fd.append('receiver_id', receiverId);
    fd.append('offered_skill_id', offeredId);
    fd.append('desired_skill_id', desiredId);
    fd.append('redirect_to', '/match');
    try {
      await fetch('/swaps/create', { method: 'POST', body: fd, redirect: 'manual' });
    } catch (err) {}
  }

  function advance() {
    currentIndex--;
    swiping = false;
    refreshStack();
  }

  function swipeCard(direction) {
    if (currentIndex < 0 || swiping) return;
    swiping = true;

    const card = remaining[currentIndex];
    card.classList.add(direction === 'right' ? 'swipe-right' : 'swipe-left');

    if (direction === 'right') {
      const score = parseInt(card.dataset.score || '0', 10);
      if (score === 3) {
        setTimeout(async () => {
          await submitSwap(card.dataset.userId, card.dataset.offered, card.dataset.desired);
          advance();
        }, 400);
        return;
      }
      setTimeout(() => {
        card.classList.remove('swipe-right');
        swiping = false;
        openModal(card);
      }, 250);
      return;
    }

    skipped.push(card.dataset.userId);
    sessionStorage.setItem('match-skipped', JSON.stringify(skipped));

    setTimeout(() => advance(), 400);
  }

  if (skipBtn) skipBtn.addEventListener('click', () => swipeCard('left'));
  if (likeBtn) likeBtn.addEventListener('click', () => swipeCard('right'));

  if (modalCancel) modalCancel.addEventListener('click', () => {
    closeModal();
    const card = remaining[currentIndex];
    if (card) {
      card.style.transform = '';
      const likeOverlay = card.querySelector('.match-card-overlay.like');
      const nopeOverlay = card.querySelector('.match-card-overlay.nope');
      if (likeOverlay) likeOverlay.style.opacity = 0;
      if (nopeOverlay) nopeOverlay.style.opacity = 0;
    }
  });

  if (modalConfirm) modalConfirm.addEventListener('click', async () => {
    if (modalConfirm.disabled || swiping) return;
    swiping = true;
    const card = remaining[currentIndex];
    closeModal();
    await submitSwap(modal.dataset.userId, modalOffered.value, modalDesired.value);
    if (card) card.classList.add('swipe-right');
    setTimeout(() => advance(), 400);
  });

  remaining.forEach(card => setupDrag(card));

  function setupDrag(card) {
    let startX = 0, currentX = 0, isDragging = false;
    const likeOverlay = card.querySelector('.match-card-overlay.like');
    const nopeOverlay = card.querySelector('.match-card-overlay.nope');

    card.addEventListener('mousedown', onStart);
    card.addEventListener('touchstart', onStart, { passive: true });

    function onStart(e) {
      if (swiping || card !== remaining[currentIndex]) return;
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
      card.style.transform = 'translateX(' + currentX + 'px) rotate(' + (currentX * 0.08) + 'deg)';
      const progress = Math.min(Math.abs(currentX) / 100, 1);
      if (currentX > 0) { likeOverlay.style.opacity = progress; nopeOverlay.style.opacity = 0; }
      else { nopeOverlay.style.opacity = progress; likeOverlay.style.opacity = 0; }
    }

    function onEnd() {
      isDragging = false;
      card.classList.remove('dragging');
      document.removeEventListener('mousemove', onMove);
      document.removeEventListener('mouseup', onEnd);
      document.removeEventListener('touchmove', onMove);
      document.removeEventListener('touchend', onEnd);
      if (Math.abs(currentX) > 100) swipeCard(currentX > 0 ? 'right' : 'left');
      else {
        card.style.transform = '';
        likeOverlay.style.opacity = 0;
        nopeOverlay.style.opacity = 0;
      }
      currentX = 0;
    }
  }

  refreshStack();
});

// Front (JS) — match: swipe estilo Tinder, modal de selecao de skills e envio de troca

