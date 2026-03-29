document.addEventListener('DOMContentLoaded', async () => {
  if (!requireAuth()) return;
  showNavUser();

  const token = getToken();
  const headers = { 'Authorization': 'Bearer ' + token };

  document.getElementById('logout-btn').addEventListener('click', (e) => {
    e.preventDefault();
    logout();
  });

  const tabs = document.querySelectorAll('.tab');
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
      tab.classList.add('active');
      document.getElementById('tab-' + tab.dataset.tab).classList.add('active');
    });
  });

  await loadSwaps('received');
  await loadSwaps('sent');

  async function loadSwaps(type) {
    const container = document.getElementById('tab-' + type);

    const res = await fetch(API + '/swaps/' + type, { headers });
    const swaps = await res.json();

    if (swaps.length === 0) {
      container.innerHTML = '<div class="empty-state">Nenhuma solicitacao ' +
        (type === 'received' ? 'recebida' : 'enviada') + ' ainda.</div>';
      return;
    }

    swaps.forEach(swap => {
      const otherUser = type === 'received' ? swap.sender : swap.receiver;
      const card = document.createElement('div');
      card.className = 'swap-card';

      let statusText = swap.status === 'pending' ? 'Pendente' : swap.status === 'accepted' ? 'Aceita' : 'Recusada';

      let html =
        '<div class="swap-header">' +
          '<span class="swap-name">' + otherUser.name + '</span>' +
          '<span class="swap-status ' + swap.status + '">' + statusText + '</span>' +
        '</div>' +
        '<div class="swap-detail">Oferece: <strong style="color:var(--green)">' + swap.offered_skill + '</strong></div>' +
        '<div class="swap-detail">Quer: <strong style="color:var(--orange)">' + swap.desired_skill + '</strong></div>';

      if (swap.status === 'accepted') {
        html += '<div class="swap-contact">' +
          '<strong>Contato:</strong> ' + otherUser.email + ' | ' + otherUser.phone +
        '</div>';
      }

      if (type === 'received' && swap.status === 'pending') {
        html += '<div class="swap-actions">' +
          '<button class="btn btn-green accept-btn" data-id="' + swap.id + '">Aceitar</button>' +
          '<button class="btn btn-red reject-btn" data-id="' + swap.id + '">Recusar</button>' +
        '</div>';
      }

      card.innerHTML = html;
      container.appendChild(card);
    });

    container.querySelectorAll('.accept-btn').forEach(btn => {
      btn.addEventListener('click', async () => {
        await fetch(API + '/swaps/' + btn.dataset.id + '?status=accepted', { method: 'PUT', headers });
        location.reload();
      });
    });

    container.querySelectorAll('.reject-btn').forEach(btn => {
      btn.addEventListener('click', async () => {
        await fetch(API + '/swaps/' + btn.dataset.id + '?status=rejected', { method: 'PUT', headers });
        location.reload();
      });
    });
  }
});
