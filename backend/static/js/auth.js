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
  window.location.href = '/login';
}

function requireAuth() {
  if (!getToken()) {
    window.location.href = '/login';
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

  const avatarContent = user.avatar
    ? '<img src="' + API + '/uploads/' + user.avatar + '" alt="avatar">'
    : initials;

  navUser.innerHTML =
    '<span class="avatar-small">' + avatarContent + '</span>' +
    '<span>' + user.name.split(' ')[0] + '</span>';
}
