function isLoggedIn() {
  return !!localStorage.getItem('token');
}

function requireAuth() {
  if (!isLoggedIn()) window.location.href = '/login.html';
}

function logout() {
  localStorage.removeItem('token');
  window.location.href = '/login.html';
}

async function login(username, password) {
  const { access_token } = await api.post('/auth/login', { username, password });
  localStorage.setItem('token', access_token);
}

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str ?? '';
  return div.innerHTML;
}
