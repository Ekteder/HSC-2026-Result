/**
 * Colleges Analysis Module (js/colleges.js)
 * Renders the 7 college cards grid and the detailed single-college dashboard
 * with visual charts (Result Doughnut, GPA Distribution, Subject-wise Performance)
 * and interactive student roster.
 */

(function () {
  let allStudents = [];
  let collegeStatsList = [];
  let activeCollegeName = null;

  let collegeDoughnutChart = null;
  let collegeGpaChart = null;
  let collegeSubjectsChart = null;

  const rosterState = {
    search: '',
    result: 'ALL',
    gpaRange: 'ALL',
    sort: 'roll-asc'
  };

  function renderCollegeCardsGrid() {
    const grid = document.getElementById('colleges-cards-grid');
    if (!grid) return;

    const orderedNames =
      (window.NARAIL_DATASET_META && window.NARAIL_DATASET_META.collegeNamesOrdered) || [];
    const sorted = [...collegeStatsList].sort((a, b) => {
      const iA = orderedNames.indexOf(a.college);
      const iB = orderedNames.indexOf(b.college);
      return (iA === -1 ? 99 : iA) - (iB === -1 ? 99 : iB);
    });

    grid.innerHTML = sorted
      .map((c) => {
        const passPct = c.total > 0 ? (c.passed / c.total) * 100 : 0;
        const failPct = c.total > 0 ? (c.failed / c.total) * 100 : 0;
        const absentPct = c.total > 0 ? (c.absent / c.total) * 100 : 0;
        const avgGpaStr = c.avgGpa !== null ? c.avgGpa.toFixed(2) : 'N/A';

        return `
          <article class="college-card" data-college-card="${c.college}" tabindex="0" role="button" aria-label="Inspect ${c.college}">
            <div class="college-card-header">
              <div>
                <h3 class="college-card-title">${c.college}</h3>
                <div class="college-card-eiin">EIIN: ${c.eiin} · GPA 5.00: ${c.gpa5Count}</div>
              </div>
              <div class="college-pass-rate-big">
                <span class="cpr-value">${passPct.toFixed(2)}%</span>
                <span class="cpr-label">Pass Rate</span>
              </div>
            </div>

            <div class="college-progress-bar" title="Pass: ${passPct.toFixed(1)}% | Fail: ${failPct.toFixed(1)}% | Absent: ${absentPct.toFixed(1)}%">
              <div class="cpb-segment pass" style="width: ${passPct}%"></div>
              <div class="cpb-segment fail" style="width: ${failPct}%"></div>
              <div class="cpb-segment absent" style="width: ${absentPct}%"></div>
            </div>

            <div class="college-card-stats">
              <div class="ccs-item">
                <span class="ccs-label">Total</span>
                <span class="ccs-val">${c.total}</span>
              </div>
              <div class="ccs-item">
                <span class="ccs-label">Passed</span>
                <span class="ccs-val pass">${c.passed}</span>
              </div>
              <div class="ccs-item">
                <span class="ccs-label">Failed</span>
                <span class="ccs-val fail">${c.failed}</span>
              </div>
              <div class="ccs-item">
                <span class="ccs-label">Absent</span>
                <span class="ccs-val absent">${c.absent}</span>
              </div>
              <div class="ccs-item">
                <span class="ccs-label">Avg GPA</span>
                <span class="ccs-val">${avgGpaStr}</span>
              </div>
            </div>

            <div class="college-card-footer">
              <span>Open Detailed College Analytics</span>
              <span aria-hidden="true">→</span>
            </div>
          </article>
        `;
      })
      .join('');

    grid.querySelectorAll('[data-college-card]').forEach((card) => {
      card.addEventListener('click', () => {
        openCollegeDetail(card.getAttribute('data-college-card'));
      });
      card.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          openCollegeDetail(card.getAttribute('data-college-card'));
        }
      });
    });
  }

  function openCollegeDetail(collegeName) {
    const colStat = collegeStatsList.find((c) => c.college === collegeName);
    if (!colStat) return;

    activeCollegeName = collegeName;

    // Reset roster filters
    rosterState.search = '';
    rosterState.result = 'ALL';
    rosterState.gpaRange = 'ALL';
    rosterState.sort = 'roll-asc';

    const sInput = document.getElementById('college-student-search');
    const rFilter = document.getElementById('college-student-result-filter');
    const gFilter = document.getElementById('college-student-gpa-filter');
    const sSelect = document.getElementById('college-student-sort');
    if (sInput) sInput.value = '';
    if (rFilter) rFilter.value = 'ALL';
    if (gFilter) gFilter.value = 'ALL';
    if (sSelect) sSelect.value = 'roll-asc';

    const gridView = document.getElementById('colleges-grid-view');
    const detailView = document.getElementById('college-detail-view');
    if (gridView) gridView.classList.add('hidden');
    if (detailView) detailView.classList.remove('hidden');

    const switcher = document.getElementById('college-detail-switcher');
    if (switcher) switcher.value = collegeName;

    const headerEl = document.getElementById('college-detail-header');
    if (headerEl) {
      headerEl.innerHTML = `
        <div>
          <div style="font-size: 0.78rem; font-weight: 600; color: var(--accent-blue);">EIIN: ${colStat.eiin} · Jashore Board · Science Group</div>
          <h2 class="section-heading" style="margin-top: 2px;">${colStat.college}</h2>
        </div>
        <div style="text-align: right;">
          <div class="mono" style="font-size: 1.5rem; font-weight: 700; color: var(--status-pass);">${colStat.passRate.toFixed(2)}%</div>
          <div style="font-size: 0.76rem; color: var(--text-muted);">Overall Pass Percentage (${colStat.appearedPassRate.toFixed(2)}% of appeared)</div>
        </div>
      `;
    }

    const kpisEl = document.getElementById('college-detail-kpis');
    if (kpisEl) {
      const avgGpaText = colStat.avgGpa !== null ? colStat.avgGpa.toFixed(2) : 'Not Available';
      const highGpaText = colStat.highestGpa > 0 ? colStat.highestGpa.toFixed(2) : 'Not Available';

      kpisEl.innerHTML = `
        <div class="kpi-card">
          <div class="kpi-card-top"><span class="kpi-label">Total Students</span></div>
          <div class="kpi-value">${colStat.total}</div>
          <div class="kpi-indicator">Appeared: <strong>${colStat.appeared}</strong></div>
        </div>
        <div class="kpi-card">
          <div class="kpi-card-top"><span class="kpi-label">Passed Students</span></div>
          <div class="kpi-value" style="color: var(--status-pass);">${colStat.passed}</div>
          <div class="kpi-indicator">Pass Rate: <strong>${colStat.passRate.toFixed(2)}%</strong></div>
        </div>
        <div class="kpi-card">
          <div class="kpi-card-top"><span class="kpi-label">Failed Students</span></div>
          <div class="kpi-value" style="color: var(--status-fail);">${colStat.failed}</div>
          <div class="kpi-indicator">Fail Rate: <strong>${((colStat.failed / colStat.total) * 100).toFixed(2)}%</strong></div>
        </div>
        <div class="kpi-card">
          <div class="kpi-card-top"><span class="kpi-label">Absent Students</span></div>
          <div class="kpi-value" style="color: var(--status-absent);">${colStat.absent}</div>
          <div class="kpi-indicator">Absent Rate: <strong>${((colStat.absent / colStat.total) * 100).toFixed(2)}%</strong></div>
        </div>
        <div class="kpi-card">
          <div class="kpi-card-top"><span class="kpi-label">Pass Percentage</span></div>
          <div class="kpi-value">${colStat.passRate.toFixed(2)}%</div>
          <div class="kpi-indicator">Of appeared: <strong>${colStat.appearedPassRate.toFixed(2)}%</strong></div>
        </div>
        <div class="kpi-card">
          <div class="kpi-card-top"><span class="kpi-label">Average GPA (Passed)</span></div>
          <div class="kpi-value">${avgGpaText}</div>
          <div class="kpi-indicator">Across <strong>${colStat.gpaCount}</strong> passed students</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-card-top"><span class="kpi-label">Highest GPA</span></div>
          <div class="kpi-value">${highGpaText}</div>
          <div class="kpi-indicator">Top score in college</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-card-top"><span class="kpi-label">GPA 5.00 Achievers</span></div>
          <div class="kpi-value" style="color: var(--accent-blue);">${colStat.gpa5Count}</div>
          <div class="kpi-indicator"><strong>${colStat.passed > 0 ? ((colStat.gpa5Count / colStat.passed) * 100).toFixed(1) : '0.0'}%</strong> of passed</div>
        </div>
      `;
    }

    const collegeStudents = allStudents.filter((s) => s.college === collegeName);
    renderCollegeCharts(colStat, collegeStudents);
    renderCollegeRoster();
  }

  function renderCollegeCharts(colStat, collegeStudents) {
    if (typeof Chart === 'undefined') return;

    // 1. Doughnut chart for PASS / FAIL / ABSENT
    const doughnutCanvas = document.getElementById('chart-college-doughnut');
    const legendEl = document.getElementById('college-doughnut-legend');
    const total = colStat.total;
    const pPct = total > 0 ? ((colStat.passed / total) * 100).toFixed(2) : '0.00';
    const fPct = total > 0 ? ((colStat.failed / total) * 100).toFixed(2) : '0.00';
    const aPct = total > 0 ? ((colStat.absent / total) * 100).toFixed(2) : '0.00';

    if (legendEl) {
      legendEl.innerHTML = `
        <div class="doughnut-stat-item">
          <div class="dsi-left"><span class="color-swatch pass"></span><span class="dsi-label">PASS</span></div>
          <div class="dsi-values"><span class="dsi-count">${colStat.passed}</span><span class="dsi-pct">(${pPct}%)</span></div>
        </div>
        <div class="doughnut-stat-item">
          <div class="dsi-left"><span class="color-swatch fail"></span><span class="dsi-label">FAIL</span></div>
          <div class="dsi-values"><span class="dsi-count">${colStat.failed}</span><span class="dsi-pct">(${fPct}%)</span></div>
        </div>
        <div class="doughnut-stat-item">
          <div class="dsi-left"><span class="color-swatch absent"></span><span class="dsi-label">ABSENT</span></div>
          <div class="dsi-values"><span class="dsi-count">${colStat.absent}</span><span class="dsi-pct">(${aPct}%)</span></div>
        </div>
      `;
    }

    if (doughnutCanvas) {
      if (collegeDoughnutChart) collegeDoughnutChart.destroy();
      collegeDoughnutChart = new Chart(doughnutCanvas, {
        type: 'doughnut',
        data: {
          labels: ['PASS', 'FAIL', 'ABSENT'],
          datasets: [
            {
              data: [colStat.passed, colStat.failed, colStat.absent],
              backgroundColor: ['#16a34a', '#dc2626', '#64748b'],
              borderColor: '#ffffff',
              borderWidth: 2
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          cutout: '64%',
          plugins: { legend: { display: false } }
        }
      });
    }

    // 2. GPA distribution chart
    const gpaCanvas = document.getElementById('chart-college-gpa');
    if (gpaCanvas) {
      if (collegeGpaChart) collegeGpaChart.destroy();

      const validGpas = collegeStudents
        .filter((s) => s.result === 'PASS' && typeof s.gpa === 'number')
        .map((s) => s.gpa);

      const g5 = validGpas.filter((g) => g === 5.0).length;
      const g4 = validGpas.filter((g) => g >= 4.0 && g <= 4.99).length;
      const g35 = validGpas.filter((g) => g >= 3.5 && g <= 3.99).length;
      const g3 = validGpas.filter((g) => g >= 3.0 && g <= 3.49).length;
      const gBelow3 = validGpas.filter((g) => g < 3.0).length;

      collegeGpaChart = new Chart(gpaCanvas, {
        type: 'bar',
        data: {
          labels: ['GPA 5.00', '4.00–4.99', '3.50–3.99', '3.00–3.49', 'Below 3.00'],
          datasets: [
            {
              label: 'Passed Students',
              data: [g5, g4, g35, g3, gBelow3],
              backgroundColor: ['#16a34a', '#2563eb', '#0284c7', '#6366f1', '#f59e0b'],
              borderRadius: 4,
              barPercentage: 0.65
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: { beginAtZero: true, ticks: { precision: 0 }, grid: { color: '#f1f5f9' } },
            x: { grid: { display: false } }
          },
          plugins: { legend: { display: false } }
        }
      });
    }

    // 3. Subject-wise performance chart
    const subCanvas = document.getElementById('chart-college-subjects');
    if (subCanvas) {
      if (collegeSubjectsChart) collegeSubjectsChart.destroy();

      const subMap = {};
      collegeStudents.forEach((s) => {
        Object.entries(s.subjects || {}).forEach(([sub, grd]) => {
          if (!grd || grd === 'Not Available') return;
          if (!subMap[sub]) {
            subMap[sub] = { 'A+': 0, A: 0, 'A-': 0, B: 0, C: 0, D: 0, F: 0, total: 0 };
          }
          if (subMap[sub][grd] !== undefined) {
            subMap[sub][grd] += 1;
            subMap[sub].total += 1;
          }
        });
      });

      const subNames = Object.keys(subMap).sort((a, b) => subMap[b].total - subMap[a].total);
      const gradeConfigs = [
        { key: 'A+', color: '#16a34a' },
        { key: 'A', color: '#2563eb' },
        { key: 'A-', color: '#0284c7' },
        { key: 'B', color: '#64748b' },
        { key: 'C', color: '#ca8a04' },
        { key: 'D', color: '#ea580c' },
        { key: 'F', color: '#dc2626' }
      ];

      collegeSubjectsChart = new Chart(subCanvas, {
        type: 'bar',
        data: {
          labels: subNames,
          datasets: gradeConfigs.map((cfg) => ({
            label: cfg.key,
            data: subNames.map((s) => subMap[s][cfg.key]),
            backgroundColor: cfg.color,
            borderRadius: 2
          }))
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            x: { stacked: true, grid: { display: false } },
            y: { stacked: true, beginAtZero: true, ticks: { precision: 0 }, grid: { color: '#f1f5f9' } }
          },
          plugins: {
            legend: { position: 'top', labels: { boxWidth: 10, font: { size: 11, weight: '600' } } }
          }
        }
      });
    }
  }

  function renderCollegeRoster() {
    if (!activeCollegeName) return;
    const tbody = document.getElementById('college-students-tbody');
    const emptyEl = document.getElementById('college-students-empty');
    const countBar = document.getElementById('college-roster-count-bar');
    const titleEl = document.getElementById('college-roster-title');

    if (!tbody) return;

    const baseList = allStudents.filter((s) => s.college === activeCollegeName);
    if (titleEl) {
      titleEl.textContent = `${activeCollegeName} — Student List (${baseList.length} Students)`;
    }

    const q = rosterState.search.trim().toLowerCase();
    const filtered = baseList.filter((s) => {
      if (rosterState.result !== 'ALL' && s.result !== rosterState.result) return false;
      if (window.NarailStudents && !window.NarailStudents.matchesGpaFilter(s, rosterState.gpaRange)) {
        return false;
      }
      if (q) {
        const hay = `${s.name} ${s.fatherName} ${s.motherName} ${s.roll} ${s.registration}`.toLowerCase();
        if (!hay.includes(q)) return false;
      }
      return true;
    });

    const [sortField, sortDir] = rosterState.sort.split('-');
    const dir = sortDir === 'asc' ? 1 : -1;
    const resOrder = { PASS: 1, FAIL: 2, ABSENT: 3 };

    filtered.sort((a, b) => {
      if (sortField === 'roll') {
        return ((parseInt(a.roll, 10) || 0) - (parseInt(b.roll, 10) || 0)) * dir;
      }
      if (sortField === 'gpa') {
        const gA = typeof a.gpa === 'number' ? a.gpa : -1;
        const gB = typeof b.gpa === 'number' ? b.gpa : -1;
        return (gA - gB) * dir;
      }
      if (sortField === 'name') {
        return a.name.localeCompare(b.name) * dir;
      }
      if (sortField === 'result') {
        return ((resOrder[a.result] || 99) - (resOrder[b.result] || 99)) * dir;
      }
      return 0;
    });

    if (countBar) {
      countBar.innerHTML = `Showing <strong>${filtered.length}</strong> of <strong>${baseList.length}</strong> students in ${activeCollegeName}`;
    }

    if (filtered.length === 0) {
      tbody.innerHTML = '';
      if (emptyEl) emptyEl.classList.remove('hidden');
      return;
    }

    if (emptyEl) emptyEl.classList.add('hidden');

    tbody.innerHTML = filtered
      .map(
        (s, idx) => `
        <tr class="clickable-row" data-roll="${s.roll}" title="Click to inspect ${s.name}">
          <td class="col-sl">${idx + 1}</td>
          <td><strong>${s.name}</strong></td>
          <td>${s.fatherName}</td>
          <td>${s.motherName}</td>
          <td class="text-right mono">${s.roll}</td>
          <td class="text-right mono">${s.registration}</td>
          <td class="text-center">${window.NarailStudents.formatResultBadge(s.result)}</td>
          <td class="text-right mono"><strong>${window.NarailStudents.formatGpaCell(s)}</strong></td>
        </tr>
      `
      )
      .join('');

    tbody.querySelectorAll('tr[data-roll]').forEach((row) => {
      row.addEventListener('click', () => {
        window.NarailStudents.openStudentModalByRoll(row.getAttribute('data-roll'));
      });
    });
  }

  function showCollegesGrid() {
    const gridView = document.getElementById('colleges-grid-view');
    const detailView = document.getElementById('college-detail-view');
    if (gridView) gridView.classList.remove('hidden');
    if (detailView) detailView.classList.add('hidden');
    activeCollegeName = null;
  }

  function initColleges(students) {
    allStudents = students;
    collegeStatsList = window.NarailDashboard.computeCollegeStats(students);

    renderCollegeCardsGrid();

    const switcher = document.getElementById('college-detail-switcher');
    if (switcher) {
      const orderedNames =
        (window.NARAIL_DATASET_META && window.NARAIL_DATASET_META.collegeNamesOrdered) || [];
      const sortedNames = collegeStatsList
        .map((c) => c.college)
        .sort((a, b) => {
          const iA = orderedNames.indexOf(a);
          const iB = orderedNames.indexOf(b);
          return (iA === -1 ? 99 : iA) - (iB === -1 ? 99 : iB);
        });
      switcher.innerHTML = sortedNames.map((n) => `<option value="${n}">${n}</option>`).join('');
      switcher.addEventListener('change', () => {
        openCollegeDetail(switcher.value);
      });
    }

    const backBtn = document.getElementById('back-to-colleges-btn');
    if (backBtn) {
      backBtn.addEventListener('click', showCollegesGrid);
    }

    const searchInput = document.getElementById('college-student-search');
    const resFilter = document.getElementById('college-student-result-filter');
    const gpaFilter = document.getElementById('college-student-gpa-filter');
    const sortSelect = document.getElementById('college-student-sort');
    const resetBtn = document.getElementById('college-student-reset-btn');

    if (searchInput) {
      searchInput.addEventListener('input', () => {
        rosterState.search = searchInput.value;
        renderCollegeRoster();
      });
    }
    if (resFilter) {
      resFilter.addEventListener('change', () => {
        rosterState.result = resFilter.value;
        renderCollegeRoster();
      });
    }
    if (gpaFilter) {
      gpaFilter.addEventListener('change', () => {
        rosterState.gpaRange = gpaFilter.value;
        renderCollegeRoster();
      });
    }
    if (sortSelect) {
      sortSelect.addEventListener('change', () => {
        rosterState.sort = sortSelect.value;
        renderCollegeRoster();
      });
    }
    if (resetBtn) {
      resetBtn.addEventListener('click', () => {
        rosterState.search = '';
        rosterState.result = 'ALL';
        rosterState.gpaRange = 'ALL';
        rosterState.sort = 'roll-asc';
        if (searchInput) searchInput.value = '';
        if (resFilter) resFilter.value = 'ALL';
        if (gpaFilter) gpaFilter.value = 'ALL';
        if (sortSelect) sortSelect.value = 'roll-asc';
        renderCollegeRoster();
      });
    }
  }

  window.NarailColleges = {
    initColleges,
    openCollegeDetail,
    showCollegesGrid
  };
})();
