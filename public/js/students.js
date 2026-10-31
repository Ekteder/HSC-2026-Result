/**
 * All Students & Student Detail Modal Module (js/students.js)
 * Manages searching, filtering, sorting, pagination, and the student details modal.
 */

(function () {
  let allStudents = [];
  let filteredStudents = [];

  const state = {
    searchQuery: '',
    college: 'ALL',
    result: 'ALL',
    gpaRange: 'ALL',
    sortBy: 'roll',
    sortDir: 'asc',
    rowsPerPage: 25,
    currentPage: 1
  };

  function formatResultBadge(result) {
    if (result === 'PASS') {
      return '<span class="result-badge pass">PASS</span>';
    }
    if (result === 'FAIL') {
      return '<span class="result-badge fail">FAIL</span>';
    }
    if (result === 'ABSENT') {
      return '<span class="result-badge absent">ABSENT</span>';
    }
    return `<span class="result-badge absent">${result || 'Not Available'}</span>`;
  }

  function formatGpaCell(student) {
    if (typeof student.gpa === 'number' && !Number.isNaN(student.gpa)) {
      return student.gpa.toFixed(2);
    }
    return '<span style="color: var(--text-muted);">Not Available</span>';
  }

  function formatGradeBadge(grade) {
    const g = (grade || '').trim();
    let cls = 'grade-b';
    if (g === 'A+') cls = 'grade-aplus';
    else if (g === 'A') cls = 'grade-a';
    else if (g === 'A-') cls = 'grade-aminus';
    else if (g === 'B') cls = 'grade-b';
    else if (g === 'C') cls = 'grade-c';
    else if (g === 'D') cls = 'grade-d';
    else if (g === 'F') cls = 'grade-f';
    return `<span class="grade-badge ${cls}">${g || 'Not Available'}</span>`;
  }

  function getGradePointText(grade) {
    const map = {
      'A+': '5.00',
      'A': '4.00',
      'A-': '3.50',
      'B': '3.00',
      'C': '2.00',
      'D': '1.00',
      'F': '0.00'
    };
    return map[(grade || '').trim()] || '—';
  }

  function matchesGpaFilter(student, gpaRange) {
    if (gpaRange === 'ALL') return true;
    // Strictly exclude students with missing/null GPA from numeric GPA ranges
    if (typeof student.gpa !== 'number' || Number.isNaN(student.gpa)) {
      return false;
    }
    const g = student.gpa;
    if (gpaRange === 'GPA_5') return g === 5.0;
    if (gpaRange === 'GPA_4_499') return g >= 4.0 && g <= 4.99;
    if (gpaRange === 'GPA_3_399') return g >= 3.0 && g <= 3.99;
    if (gpaRange === 'GPA_BELOW_3') return g < 3.0;
    return true;
  }

  function applyFiltersAndSort() {
    const q = state.searchQuery.trim().toLowerCase();

    filteredStudents = allStudents.filter((s) => {
      if (state.college !== 'ALL' && s.college !== state.college) {
        return false;
      }
      if (state.result !== 'ALL' && s.result !== state.result) {
        return false;
      }
      if (!matchesGpaFilter(s, state.gpaRange)) {
        return false;
      }
      if (q) {
        const haystack = [
          s.name,
          s.fatherName,
          s.motherName,
          s.roll,
          s.registration,
          s.college,
          s.collegeOriginal
        ]
          .join(' ')
          .toLowerCase();
        if (!haystack.includes(q)) return false;
      }
      return true;
    });

    // Sort
    const resultOrder = { PASS: 1, FAIL: 2, ABSENT: 3 };
    filteredStudents.sort((a, b) => {
      const dir = state.sortDir === 'asc' ? 1 : -1;

      if (state.sortBy === 'roll') {
        const rA = parseInt(a.roll, 10) || 0;
        const rB = parseInt(b.roll, 10) || 0;
        return (rA - rB) * dir;
      }

      if (state.sortBy === 'name') {
        return a.name.localeCompare(b.name) * dir;
      }

      if (state.sortBy === 'college') {
        const cmp = a.college.localeCompare(b.college);
        if (cmp !== 0) return cmp * dir;
        return (parseInt(a.roll, 10) || 0) - (parseInt(b.roll, 10) || 0);
      }

      if (state.sortBy === 'gpa') {
        const gA = typeof a.gpa === 'number' ? a.gpa : -1;
        const gB = typeof b.gpa === 'number' ? b.gpa : -1;
        if (gA !== gB) return (gA - gB) * dir;
        return (parseInt(a.roll, 10) || 0) - (parseInt(b.roll, 10) || 0);
      }

      if (state.sortBy === 'result') {
        const oA = resultOrder[a.result] || 99;
        const oB = resultOrder[b.result] || 99;
        if (oA !== oB) return (oA - oB) * dir;
        const gA = typeof a.gpa === 'number' ? a.gpa : -1;
        const gB = typeof b.gpa === 'number' ? b.gpa : -1;
        return gB - gA;
      }

      return 0;
    });

    renderStudentsTable();
  }

  function updateHeaderSortIndicators() {
    const headers = document.querySelectorAll('#all-students-table th[data-student-sort]');
    headers.forEach((th) => {
      const col = th.getAttribute('data-student-sort');
      const ind = th.querySelector('.sort-indicator');
      if (col === state.sortBy) {
        th.classList.add('active-sort');
        if (ind) ind.textContent = state.sortDir === 'asc' ? '↑' : '↓';
      } else {
        th.classList.remove('active-sort');
        if (ind) ind.textContent = '';
      }
    });

    // Sync dropdown if matching option exists
    const sortSelect = document.getElementById('sort-students-select');
    if (sortSelect) {
      const key = `${state.sortBy}-${state.sortDir}`;
      if ([...sortSelect.options].some((o) => o.value === key)) {
        sortSelect.value = key;
      }
    }
  }

  function renderStudentsTable() {
    const tbody = document.getElementById('all-students-tbody');
    const emptyState = document.getElementById('students-empty-state');
    const paginationBar = document.getElementById('students-pagination-bar');
    const matchingSummary = document.getElementById('students-matching-summary');
    const activeFiltersSummary = document.getElementById('students-active-filters-summary');
    const resetSearchBtn = document.getElementById('students-reset-search-btn');

    if (!tbody) return;

    if (resetSearchBtn) {
      resetSearchBtn.classList.toggle('hidden', !state.searchQuery.trim());
    }

    const totalMatching = filteredStudents.length;
    const totalPages = Math.max(1, Math.ceil(totalMatching / state.rowsPerPage));
    if (state.currentPage > totalPages) {
      state.currentPage = totalPages;
    }

    const startIdx = (state.currentPage - 1) * state.rowsPerPage;
    const endIdx = Math.min(startIdx + state.rowsPerPage, totalMatching);
    const pageSlice = filteredStudents.slice(startIdx, endIdx);

    // Update status summary
    if (matchingSummary) {
      if (totalMatching === 0) {
        matchingSummary.innerHTML = `Showing <strong>0</strong> of <strong>0</strong> matching students (from ${allStudents.length} total)`;
      } else {
        matchingSummary.innerHTML = `Showing <strong>${startIdx + 1}–${endIdx}</strong> of <strong>${totalMatching}</strong> matching students`;
      }
    }

    if (activeFiltersSummary) {
      const parts = [];
      if (state.college !== 'ALL') parts.push(`College: ${state.college}`);
      if (state.result !== 'ALL') parts.push(`Result: ${state.result}`);
      if (state.gpaRange !== 'ALL') {
        const gpaLabelMap = {
          GPA_5: 'GPA 5.00',
          GPA_4_499: 'GPA 4.00–4.99',
          GPA_3_399: 'GPA 3.00–3.99',
          GPA_BELOW_3: 'Below 3.00'
        };
        parts.push(`GPA: ${gpaLabelMap[state.gpaRange]}`);
      }
      if (state.searchQuery.trim()) {
        parts.push(`Search: "${state.searchQuery.trim()}"`);
      }
      activeFiltersSummary.textContent = parts.length > 0 ? parts.join(' · ') : 'Showing all records';
    }

    if (totalMatching === 0) {
      tbody.innerHTML = '';
      if (emptyState) emptyState.classList.remove('hidden');
      if (paginationBar) paginationBar.classList.add('hidden');
      return;
    }

    if (emptyState) emptyState.classList.add('hidden');
    if (paginationBar) paginationBar.classList.remove('hidden');

    tbody.innerHTML = pageSlice
      .map((s, idx) => {
        const sl = startIdx + idx + 1;
        return `
          <tr class="clickable-row" data-roll="${s.roll}" title="Click to view complete details for ${s.name}">
            <td class="col-sl">${sl}</td>
            <td>${s.college}</td>
            <td><strong>${s.name}</strong></td>
            <td>${s.fatherName}</td>
            <td>${s.motherName}</td>
            <td class="text-right mono">${s.roll}</td>
            <td class="text-right mono">${s.registration}</td>
            <td class="text-center">${formatResultBadge(s.result)}</td>
            <td class="text-right mono"><strong>${formatGpaCell(s)}</strong></td>
          </tr>
        `;
      })
      .join('');

    // Attach click listeners to open student detail modal
    tbody.querySelectorAll('tr[data-roll]').forEach((row) => {
      row.addEventListener('click', () => {
        const roll = row.getAttribute('data-roll');
        openStudentModalByRoll(roll);
      });
    });

    renderPaginationControls(totalPages, totalMatching);
  }

  function renderPaginationControls(totalPages, totalMatching) {
    const curEl = document.getElementById('page-current-num');
    const totEl = document.getElementById('page-total-num');
    const recEl = document.getElementById('page-total-records');
    const prevBtn = document.getElementById('page-prev-btn');
    const nextBtn = document.getElementById('page-next-btn');
    const numsContainer = document.getElementById('page-numbers-container');

    if (curEl) curEl.textContent = String(state.currentPage);
    if (totEl) totEl.textContent = String(totalPages);
    if (recEl) recEl.textContent = `${totalMatching} matching student${totalMatching === 1 ? '' : 's'}`;

    if (prevBtn) prevBtn.disabled = state.currentPage <= 1;
    if (nextBtn) nextBtn.disabled = state.currentPage >= totalPages;

    if (!numsContainer) return;

    // Build compact page number buttons
    const pages = [];
    const maxButtons = 5;
    let startPage = Math.max(1, state.currentPage - 2);
    let endPage = Math.min(totalPages, startPage + maxButtons - 1);
    if (endPage - startPage < maxButtons - 1) {
      startPage = Math.max(1, endPage - maxButtons + 1);
    }

    for (let p = startPage; p <= endPage; p++) {
      pages.push(p);
    }

    numsContainer.innerHTML = pages
      .map(
        (p) => `
        <button type="button" class="page-num-btn ${p === state.currentPage ? 'active' : ''}" data-page="${p}">
          ${p}
        </button>
      `
      )
      .join('');

    numsContainer.querySelectorAll('button[data-page]').forEach((btn) => {
      btn.addEventListener('click', () => {
        const targetPage = parseInt(btn.getAttribute('data-page'), 10);
        if (targetPage && targetPage !== state.currentPage) {
          state.currentPage = targetPage;
          renderStudentsTable();
        }
      });
    });
  }

  function resetAllFilters() {
    state.searchQuery = '';
    state.college = 'ALL';
    state.result = 'ALL';
    state.gpaRange = 'ALL';
    state.sortBy = 'roll';
    state.sortDir = 'asc';
    state.currentPage = 1;

    const searchInput = document.getElementById('students-search-input');
    const colSelect = document.getElementById('filter-college');
    const resSelect = document.getElementById('filter-result');
    const gpaSelect = document.getElementById('filter-gpa');
    const sortSelect = document.getElementById('sort-students-select');

    if (searchInput) searchInput.value = '';
    if (colSelect) colSelect.value = 'ALL';
    if (resSelect) resSelect.value = 'ALL';
    if (gpaSelect) gpaSelect.value = 'ALL';
    if (sortSelect) sortSelect.value = 'roll-asc';

    updateHeaderSortIndicators();
    applyFiltersAndSort();
  }

  function openStudentModalByRoll(roll) {
    const student = allStudents.find((s) => String(s.roll) === String(roll));
    if (!student) return;

    const modal = document.getElementById('student-detail-modal');
    const collegeEl = document.getElementById('modal-student-college');
    const nameEl = document.getElementById('modal-student-name');
    const bannerEl = document.getElementById('modal-academic-banner');
    const personalEl = document.getElementById('modal-personal-info');
    const gradesEl = document.getElementById('modal-grades-container');

    if (!modal || !personalEl || !gradesEl) return;

    if (collegeEl) {
      collegeEl.textContent = `${student.college} (EIIN: ${student.eiin || 'Not Available'})`;
    }
    if (nameEl) {
      nameEl.textContent = student.name;
    }

    const gpaDisplay =
      typeof student.gpa === 'number' && !Number.isNaN(student.gpa)
        ? student.gpa.toFixed(2)
        : 'Not Available';

    const subjectEntries = Object.entries(student.subjects || {});

    if (bannerEl) {
      bannerEl.innerHTML = `
        <div class="mab-item">
          <span class="mab-label">Examination Result</span>
          <div class="mab-value">${formatResultBadge(student.result)}</div>
        </div>
        <div class="mab-item">
          <span class="mab-label">GPA Achieved</span>
          <div class="mab-value">${gpaDisplay}</div>
        </div>
        <div class="mab-item">
          <span class="mab-label">Roll Number</span>
          <div class="mab-value">${student.roll}</div>
        </div>
        <div class="mab-item">
          <span class="mab-label">Examination Center</span>
          <div class="mab-value">${student.center}</div>
        </div>
      `;
    }

    personalEl.innerHTML = `
      <div class="info-row">
        <dt>Student Name</dt>
        <dd>${student.name}</dd>
      </div>
      <div class="info-row">
        <dt>Father's Name</dt>
        <dd>${student.fatherName}</dd>
      </div>
      <div class="info-row">
        <dt>Mother's Name</dt>
        <dd>${student.motherName}</dd>
      </div>
      <div class="info-row">
        <dt>College Name</dt>
        <dd>${student.college}</dd>
      </div>
      <div class="info-row">
        <dt>Roll Number</dt>
        <dd class="mono">${student.roll}</dd>
      </div>
      <div class="info-row">
        <dt>Registration Number</dt>
        <dd class="mono">${student.registration}</dd>
      </div>
      <div class="info-row">
        <dt>Examination Center</dt>
        <dd>${student.center}</dd>
      </div>
      <div class="info-row">
        <dt>Group & Session</dt>
        <dd>${student.group} · ${student.session}</dd>
      </div>
      <div class="info-row">
        <dt>Student Type & Passing Year</dt>
        <dd>${student.studentType} · ${student.passingYear}</dd>
      </div>
    `;

    if (subjectEntries.length === 0) {
      gradesEl.innerHTML = `
        <div class="empty-state" style="padding: 28px 16px; border: 1px dashed var(--border-subtle); border-radius: var(--radius-sm);">
          <p class="empty-state-title" style="font-size: 0.92rem;">No Subject Grades Recorded</p>
          <p class="empty-state-text" style="font-size: 0.8rem;">
            This student's examination status is <strong>${student.result}</strong> and no individual subject grades were present in the official grade sheet.
          </p>
        </div>
      `;
    } else {
      gradesEl.innerHTML = `
        <div class="table-responsive">
          <table class="data-table">
            <thead>
              <tr>
                <th>Subject</th>
                <th class="text-center">Grade</th>
                <th class="text-right">Grade Point</th>
              </tr>
            </thead>
            <tbody>
              ${subjectEntries
                .map(
                  ([sub, grd]) => `
                  <tr>
                    <td><strong>${sub}</strong></td>
                    <td class="text-center">${formatGradeBadge(grd)}</td>
                    <td class="text-right mono">${getGradePointText(grd)}</td>
                  </tr>
                `
                )
                .join('')}
            </tbody>
          </table>
        </div>
      `;
    }

    modal.classList.remove('hidden');
  }

  function closeStudentModal() {
    const modal = document.getElementById('student-detail-modal');
    if (modal) modal.classList.add('hidden');
  }

  function initStudents(students) {
    allStudents = students;

    // Populate College filter dropdown
    const colSelect = document.getElementById('filter-college');
    if (colSelect) {
      const uniqueColleges = [...new Set(students.map((s) => s.college))].sort();
      colSelect.innerHTML =
        `<option value="ALL">All Colleges (${uniqueColleges.length})</option>` +
        uniqueColleges.map((c) => `<option value="${c}">${c}</option>`).join('');

      colSelect.addEventListener('change', () => {
        state.college = colSelect.value;
        state.currentPage = 1;
        applyFiltersAndSort();
      });
    }

    const searchInput = document.getElementById('students-search-input');
    if (searchInput) {
      searchInput.addEventListener('input', () => {
        state.searchQuery = searchInput.value;
        state.currentPage = 1;
        applyFiltersAndSort();
      });
    }

    const resetSearchBtn = document.getElementById('students-reset-search-btn');
    if (resetSearchBtn) {
      resetSearchBtn.addEventListener('click', () => {
        state.searchQuery = '';
        if (searchInput) {
          searchInput.value = '';
          searchInput.focus();
        }
        state.currentPage = 1;
        applyFiltersAndSort();
      });
    }

    const resSelect = document.getElementById('filter-result');
    if (resSelect) {
      resSelect.addEventListener('change', () => {
        state.result = resSelect.value;
        state.currentPage = 1;
        applyFiltersAndSort();
      });
    }

    const gpaSelect = document.getElementById('filter-gpa');
    if (gpaSelect) {
      gpaSelect.addEventListener('change', () => {
        state.gpaRange = gpaSelect.value;
        state.currentPage = 1;
        applyFiltersAndSort();
      });
    }

    const sortSelect = document.getElementById('sort-students-select');
    if (sortSelect) {
      sortSelect.addEventListener('change', () => {
        const [field, dir] = sortSelect.value.split('-');
        state.sortBy = field;
        state.sortDir = dir;
        state.currentPage = 1;
        updateHeaderSortIndicators();
        applyFiltersAndSort();
      });
    }

    const perPageSelect = document.getElementById('students-per-page');
    if (perPageSelect) {
      perPageSelect.addEventListener('change', () => {
        state.rowsPerPage = parseInt(perPageSelect.value, 10) || 25;
        state.currentPage = 1;
        renderStudentsTable();
      });
    }

    // Table header sorting
    document.querySelectorAll('#all-students-table th[data-student-sort]').forEach((th) => {
      th.addEventListener('click', () => {
        const field = th.getAttribute('data-student-sort');
        if (state.sortBy === field) {
          state.sortDir = state.sortDir === 'asc' ? 'desc' : 'asc';
        } else {
          state.sortBy = field;
          state.sortDir = field === 'gpa' ? 'desc' : 'asc';
        }
        state.currentPage = 1;
        updateHeaderSortIndicators();
        applyFiltersAndSort();
      });
    });

    // Clear filters buttons
    const clearBtn = document.getElementById('students-clear-filters-btn');
    if (clearBtn) clearBtn.addEventListener('click', resetAllFilters);

    const emptyResetBtn = document.getElementById('empty-state-reset-btn');
    if (emptyResetBtn) emptyResetBtn.addEventListener('click', resetAllFilters);

    // Pagination prev/next
    const prevBtn = document.getElementById('page-prev-btn');
    const nextBtn = document.getElementById('page-next-btn');
    if (prevBtn) {
      prevBtn.addEventListener('click', () => {
        if (state.currentPage > 1) {
          state.currentPage -= 1;
          renderStudentsTable();
        }
      });
    }
    if (nextBtn) {
      nextBtn.addEventListener('click', () => {
        const totalPages = Math.max(1, Math.ceil(filteredStudents.length / state.rowsPerPage));
        if (state.currentPage < totalPages) {
          state.currentPage += 1;
          renderStudentsTable();
        }
      });
    }

    // Modal close events
    const closeBtn = document.getElementById('modal-close-btn');
    const returnBtn = document.getElementById('modal-return-btn');
    const printBtn = document.getElementById('modal-print-btn');
    const modalOverlay = document.getElementById('student-detail-modal');

    if (closeBtn) closeBtn.addEventListener('click', closeStudentModal);
    if (returnBtn) returnBtn.addEventListener('click', closeStudentModal);
    if (printBtn) {
      printBtn.addEventListener('click', () => {
        window.print();
      });
    }
    if (modalOverlay) {
      modalOverlay.addEventListener('click', (e) => {
        if (e.target === modalOverlay) closeStudentModal();
      });
    }
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') closeStudentModal();
    });

    applyFiltersAndSort();
  }

  window.NarailStudents = {
    initStudents,
    openStudentModalByRoll,
    formatResultBadge,
    formatGpaCell,
    formatGradeBadge,
    matchesGpaFilter
  };
})();
