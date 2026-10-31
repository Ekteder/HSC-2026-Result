/**
 * Main Application Controller (js/app.js)
 * Coordinates sidebar navigation, mobile menu, global student search in topbar,
 * and initializes Dashboard, Students, Colleges, and Subject Analysis modules.
 */

(function () {
  const SECTION_TITLES = {
    overview: 'Overview',
    students: 'All Students',
    colleges: 'Colleges',
    subjects: 'Subject Analysis'
  };

  function switchSection(sectionId, keepCollegeDetail) {
    if (!SECTION_TITLES[sectionId]) return;

    // Update sidebar active state
    document.querySelectorAll('.nav-item[data-section]').forEach((btn) => {
      const target = btn.getAttribute('data-section');
      btn.classList.toggle('active', target === sectionId);
    });

    // Update section visibility
    document.querySelectorAll('.view-section').forEach((sec) => {
      sec.classList.toggle('active', sec.id === `section-${sectionId}`);
    });

    // Update topbar section title
    const titleEl = document.getElementById('current-section-title');
    if (titleEl) {
      titleEl.textContent = SECTION_TITLES[sectionId];
    }

    // If switching to colleges via sidebar, reset to the 7 college cards grid unless opening a specific college
    if (
      sectionId === 'colleges' &&
      !keepCollegeDetail &&
      window.NarailColleges &&
      typeof window.NarailColleges.showCollegesGrid === 'function'
    ) {
      window.NarailColleges.showCollegesGrid();
    }

    closeMobileSidebar();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  function openCollegeDetails(collegeName) {
    switchSection('colleges', true);
    if (window.NarailColleges && typeof window.NarailColleges.openCollegeDetail === 'function') {
      window.NarailColleges.openCollegeDetail(collegeName);
    }
  }

  function openMobileSidebar() {
    const sidebar = document.getElementById('app-sidebar');
    const backdrop = document.getElementById('sidebar-backdrop');
    if (sidebar) sidebar.classList.add('open');
    if (backdrop) backdrop.classList.add('open');
  }

  function closeMobileSidebar() {
    const sidebar = document.getElementById('app-sidebar');
    const backdrop = document.getElementById('sidebar-backdrop');
    if (sidebar) sidebar.classList.remove('open');
    if (backdrop) backdrop.classList.remove('open');
  }

  function initGlobalSearch(students) {
    const searchInput = document.getElementById('global-student-search');
    const dropdown = document.getElementById('global-search-dropdown');
    const container = document.getElementById('global-search-container');

    if (!searchInput || !dropdown) return;

    function renderDropdown(query) {
      const q = query.trim().toLowerCase();
      if (!q) {
        dropdown.classList.add('hidden');
        dropdown.innerHTML = '';
        return;
      }

      const matches = students
        .filter((s) => {
          const hay = `${s.name} ${s.fatherName} ${s.motherName} ${s.roll} ${s.registration} ${s.college}`.toLowerCase();
          return hay.includes(q);
        })
        .slice(0, 12);

      if (matches.length === 0) {
        dropdown.innerHTML = `
          <div style="padding: 14px; font-size: 0.8rem; color: var(--text-muted); text-align: center;">
            No student found matching "<strong>${query.replace(/</g, '&lt;')}</strong>"
          </div>
        `;
        dropdown.classList.remove('hidden');
        return;
      }

      dropdown.innerHTML = matches
        .map((s) => {
          const gpaStr =
            typeof s.gpa === 'number' && !Number.isNaN(s.gpa) ? `GPA ${s.gpa.toFixed(2)}` : s.result;
          return `
            <button type="button" class="global-search-item" data-global-roll="${s.roll}">
              <div class="gsi-main">
                <div class="gsi-name">${s.name} <span class="mono" style="font-weight: 500; color: var(--text-muted);">(#${s.roll})</span></div>
                <div class="gsi-sub">${s.college} · F: ${s.fatherName} · M: ${s.motherName}</div>
              </div>
              <div class="gsi-meta">
                ${window.NarailStudents.formatResultBadge(s.result)}
                <span class="mono" style="font-size: 0.75rem; font-weight: 700;">${gpaStr}</span>
              </div>
            </button>
          `;
        })
        .join('');

      dropdown.classList.remove('hidden');

      dropdown.querySelectorAll('[data-global-roll]').forEach((btn) => {
        btn.addEventListener('click', () => {
          const roll = btn.getAttribute('data-global-roll');
          dropdown.classList.add('hidden');
          searchInput.value = '';
          if (window.NarailStudents && typeof window.NarailStudents.openStudentModalByRoll === 'function') {
            window.NarailStudents.openStudentModalByRoll(roll);
          }
        });
      });
    }

    searchInput.addEventListener('input', () => {
      renderDropdown(searchInput.value);
    });

    searchInput.addEventListener('focus', () => {
      if (searchInput.value.trim()) {
        renderDropdown(searchInput.value);
      }
    });

    document.addEventListener('click', (e) => {
      if (container && !container.contains(e.target)) {
        dropdown.classList.add('hidden');
      }
    });

    // Keyboard shortcut '/' to focus global search
    document.addEventListener('keydown', (e) => {
      const tag = (e.target && e.target.tagName) || '';
      if (e.key === '/' && tag !== 'INPUT' && tag !== 'TEXTAREA' && tag !== 'SELECT') {
        e.preventDefault();
        searchInput.focus();
      }
    });
  }

  function init() {
    const students = window.NARAIL_STUDENTS_DATA || [];
    const meta = window.NARAIL_DATASET_META || null;

    // Update topbar and sidebar counts dynamically
    const topbarCount = document.getElementById('topbar-total-students');
    const sidebarBadge = document.getElementById('sidebar-student-badge');
    const verifiedCount = document.getElementById('sidebar-verified-count');

    if (topbarCount) topbarCount.textContent = String(students.length);
    if (sidebarBadge) sidebarBadge.textContent = String(students.length);
    if (verifiedCount) verifiedCount.textContent = `${students.length} / ${students.length}`;

    // Sidebar navigation buttons
    document.querySelectorAll('.nav-item[data-section]').forEach((btn) => {
      btn.addEventListener('click', () => {
        const sec = btn.getAttribute('data-section');
        switchSection(sec, false);
      });
    });

    // Mobile menu handlers
    const menuBtn = document.getElementById('mobile-menu-btn');
    const closeBtn = document.getElementById('sidebar-close-btn');
    const backdrop = document.getElementById('sidebar-backdrop');

    if (menuBtn) menuBtn.addEventListener('click', openMobileSidebar);
    if (closeBtn) closeBtn.addEventListener('click', closeMobileSidebar);
    if (backdrop) backdrop.addEventListener('click', closeMobileSidebar);

    // Initialize Chart.js global defaults
    if (typeof Chart !== 'undefined') {
      Chart.defaults.font.family = "'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif";
      Chart.defaults.color = '#475569';
    }

    // Initialize all modules
    if (window.NarailDashboard) {
      window.NarailDashboard.initDashboard(students, meta);
    }
    if (window.NarailStudents) {
      window.NarailStudents.initStudents(students);
    }
    if (window.NarailColleges) {
      window.NarailColleges.initColleges(students);
    }
    if (window.NarailSubjects) {
      window.NarailSubjects.initSubjects(students);
    }

    initGlobalSearch(students);
  }

  window.NarailApp = {
    switchSection,
    openCollegeDetails
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
