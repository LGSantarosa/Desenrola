document.addEventListener('DOMContentLoaded', () => {
  const stack = document.getElementById('match-stack');
  const actions = document.getElementById('match-actions');
  const emptyEl = document.getElementById('match-empty');
  const skipBtn = document.getElementById('skip-btn');
  const likeBtn = document.getElementById('like-btn');
  const swapForm = document.getElementById('match-swap-form');

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

  function swipeCard(direction) {
    if (currentIndex < 0 || swiping) return;
    swiping = true;

    const card = remaining[currentIndex];
    card.classList.add(direction === 'right' ? 'swipe-right' : 'swipe-left');

    if (direction === 'right') {
      swapForm.querySelector('#swap-receiver').value = card.dataset.userId;
      swapForm.querySelector('#swap-offered').value = card.dataset.offered;
      swapForm.querySelector('#swap-desired').value = card.dataset.desired;
      setTimeout(() => swapForm.submit(), 400);
      return;
    }

    skipped.push(card.dataset.userId);
    sessionStorage.setItem('match-skipped', JSON.stringify(skipped));

    setTimeout(() => {
      currentIndex--;
      swiping = false;
      refreshStack();
    }, 400);
  }

  if (skipBtn) skipBtn.addEventListener('click', () => swipeCard('left'));
  if (likeBtn) likeBtn.addEventListener('click', () => swipeCard('right'));

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
