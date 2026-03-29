function getToken() {
  return localStorage.getItem('token');
}

function getUser() {
  const data = localStorage.getItem('user');
  return data ? JSON.parse(data) : null;
}

function logout() {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
  window.location.href = 'login.html';
}

function requireAuth() {
  if (!getToken()) {
    window.location.href = 'login.html';
    return false;
  }
  return true;
}

function showNavUser() {
  const user = getUser();
  const navUser = document.getElementById('nav-user');
  if (!user || !navUser) return;

  const initials = user.name
    .split(' ')
    .map(w => w[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);

  navUser.innerHTML =
    '<span class="avatar-small">' + initials + '</span>' +
    '<span>' + user.name + '</span>';
}
