const NAV_ITEMS = [
  { section: 'Main Menu', items: [
    { href: '/index.html', icon: 'fa-th-large', label: 'Dashboard', key: 'dashboard' },
    { href: '/members.html', icon: 'fa-users', label: 'Members', key: 'members' },
    { href: '/attendance.html', icon: 'fa-fingerprint', label: 'Attendance', key: 'attendance' },
  ] },
  { section: 'Finance', items: [
    { href: '/fees.html', icon: 'fa-credit-card', label: 'Fee Management', key: 'fees' },
    { href: '/plans.html', icon: 'fa-tags', label: 'Membership Plans', key: 'plans' },
  ] },
  { section: 'Operations', items: [
    { href: '/inquiries.html', icon: 'fa-user-clock', label: 'Inquiries', key: 'inquiries' },
    { href: '/biometric.html', icon: 'fa-server', label: 'Biometric Setup', key: 'biometric' },
  ] },
];

function renderLayout(activeKey, pageTitle) {
  requireAuth();

  // Sidebar overlay
  document.body.insertAdjacentHTML('beforeend', '<div class="sidebar-overlay" id="sidebarOverlay" onclick="closeSidebar()"></div>');

  const navHtml = NAV_ITEMS.map((group) => `
    <div class="sidebar-section-label">${group.section}</div>
    ${group.items.map((item) => `
      <a href="${item.href}" class="nav-link ${item.key === activeKey ? 'active' : ''}">
        <span class="nav-icon"><i class="fas ${item.icon}"></i></span>
        ${item.label}
      </a>
    `).join('')}
  `).join('');

  const today = new Date().toLocaleDateString(undefined, { weekday: 'short', day: '2-digit', month: 'short', year: 'numeric' });

  document.body.insertAdjacentHTML('afterbegin', `
    <div class="app-shell">
      <aside class="sidebar" id="sidebar">
        <div class="sidebar-brand">
          <div class="sidebar-brand-icon"><i class="fas fa-dumbbell"></i></div>
          <div>
            <div class="sidebar-brand-text" id="sidebarBrandText">My Gym</div>
            <div style="color:#475569;font-size:0.68rem;">Gym Management</div>
          </div>
        </div>
        ${navHtml}
        <div class="sidebar-footer">
          <a class="user-pill" id="userPill" onclick="window.location.href='/profile.html'" style="cursor:pointer;">
            <div class="user-avatar" id="userInitials">--</div>
            <div class="user-info">
              <div class="user-name" id="userName">...</div>
              <div class="user-role" id="userRole"></div>
            </div>
            <button class="logout-btn" title="Logout" onclick="event.stopPropagation();logout()"><i class="fas fa-sign-out-alt"></i></button>
          </a>
        </div>
      </aside>
      <div class="main-content">
        <div class="topbar">
          <div style="display:flex;align-items:center;gap:1rem;">
            <button class="sidebar-toggle btn-outline-sm" onclick="toggleSidebar()">
              <i class="fas fa-bars"></i>
            </button>
            <span class="topbar-title">${pageTitle}</span>
          </div>
          <div class="topbar-right">
            <span class="topbar-date"><i class="fas fa-calendar-alt" style="margin-right:6px;"></i>${today}</span>
            <a href="/members.html?add=1" class="btn-primary-sm" style="padding:0.4rem 0.9rem;font-size:0.78rem;">
              <i class="fas fa-user-plus"></i><span class="topbar-add-text"> Add Member</span>
            </a>
            <button class="btn-primary-sm" onclick="logout()" style="padding:0.4rem 0.9rem;font-size:0.78rem;background:#dc2626;">
              <i class="fas fa-sign-out-alt"></i><span class="topbar-logout-text"> Logout</span>
            </button>
          </div>
        </div>
        <div class="page-body" id="pageBody"></div>
      </div>
    </div>
  `);

  // Close sidebar when nav link is clicked on mobile
  document.querySelectorAll('.sidebar .nav-link').forEach(function(link) {
    link.addEventListener('click', function() {
      if (window.innerWidth <= 768) closeSidebar();
    });
  });

  api.get('/auth/me').then((user) => {
    document.getElementById('userInitials').textContent = user.username.slice(0, 2).toUpperCase();
    document.getElementById('userName').textContent = user.first_name ? `${user.first_name} ${user.last_name || ''}`.trim() : user.username;
    document.getElementById('userRole').textContent = user.role === 'super_admin' ? 'Super Admin' : 'Gym Admin';
    if (user.gym && user.gym.name) {
      document.getElementById('sidebarBrandText').textContent = user.gym.name;
    }
  }).catch(() => logout());
}

function toggleSidebar() {
  var sidebar = document.getElementById('sidebar');
  var overlay = document.getElementById('sidebarOverlay');
  sidebar.classList.toggle('open');
  if (overlay) overlay.classList.toggle('show', sidebar.classList.contains('open'));
}
function closeSidebar() {
  var sidebar = document.getElementById('sidebar');
  var overlay = document.getElementById('sidebarOverlay');
  if (sidebar) sidebar.classList.remove('open');
  if (overlay) overlay.classList.remove('show');
}
