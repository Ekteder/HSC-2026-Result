/**
 * Dashboard Overview Module (js/dashboard.js)
 * Dynamically calculates and renders KPI cards, charts, college statistics table,
 * quick insights, and data validation summary from window.NARAIL_STUDENTS_DATA.
 */

(function () {
  let distributionChartInstance = null;
  let collegeComparisonChartInstance = null;
  let currentChartMode = 'total'; // 'total' | 'passRate' | 'passed'
  let currentSortCol = 'passRate';
  let currentSortDir = 'desc';

  function computeCollegeStats(students) {
    const map = {};
    students.forEach((s) => {
      const col = s.college;
      if (!map[col]) {
        map[col] = {
          college: col,
          shortName: s.collegeShort || col,
          eiin: s.eiin || 'Not Available',
          total: 0,
          passed: 0,
          failed: 0,
          absent: 0,
          gpaSum: 0,
          gpaCount: 0,
          highestGpa: 0,
          gpa5Count: 0
        };
      }
      const entry = map[col];
      entry.total += 1;
      if (s.result === 'PASS') {
        entry.passed += 1;
        if (typeof s.gpa === 'number' && !Number.isNaN(s.gpa)) {
          entry.gpaSum += s.gpa;
          entry.gpaCount += 1;
          if (s.gpa > entry.highestGpa) entry.highestGpa = s.gpa;
          if (s.gpa === 5.0) entry.gpa5Count += 1;
        }
      } else if (s.result === 'FAIL') {
        entry.failed += 1;
      } else if (s.result === 'ABSENT') {
        entry.absent += 1;
      }
    });

    return Object.values(map).map((c) => {
      const passRate = c.total > 0 ? (c.passed / c.total) * 100 : 0;
      const appeared = c.total - c.absent;
      const appearedPassRate = appeared > 0 ? (c.passed / appeared) * 100 : 0;
      const avgGpa = c.gpaCount > 0 ? c.gpaSum / c.gpaCount : null;
      return {
        ...c,
        passRate,
        appeared,
        appearedPassRate,
        avgGpa
      };
    });
  }

  function renderKpiCards(students, collegeStats) {
    const totalStudents = students.length;
    const totalColleges = collegeStats.length;
    const passed = students.filter((s) => s.result === 'PASS').length;
    const failed = students.filter((s) => s.result === 'FAIL').length;
    const absent = students.filter((s) => s.result === 'ABSENT').length;
    const passRate = totalStudents > 0 ? ((passed / totalStudents) * 100).toFixed(2) : '0.00';
    const appeared = totalStudents - absent;
    const appearedPassRate = appeared > 0 ? ((passed / appeared) * 100).toFixed(2) : '0.00';
    const failRate = totalStudents > 0 ? ((failed / totalStudents) * 100).toFixed(2) : '0.00';
    const absentRate = totalStudents > 0 ? ((absent / totalStudents) * 100).toFixed(2) : '0.00';

    const container = document.getElementById('overview-kpi-grid');
    if (!container) return;

    container.innerHTML = `
      <div class="kpi-card">
        <div class="kpi-card-top">
          <span class="kpi-label">Total Students</span>
          <div class="kpi-icon blue" aria-hidden="true">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
              <circle cx="9" cy="7" r="4" />
              <path d="M22 21v-2a4 4 0 0 0-3-3.87" />
              <path d="M16 3.13a4 4 0 0 1 0 7.75" />
            </svg>
          </div>
        </div>
        <div class="kpi-value">${totalStudents}</div>
        <div class="kpi-indicator">
          <span>Appeared: <strong>${appeared}</strong></span>
        </div>
      </div>

      <div class="kpi-card">
        <div class="kpi-card-top">
          <span class="kpi-label">Total Colleges</span>
          <div class="kpi-icon blue" aria-hidden="true">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M3 21h18" />
              <path d="M5 21V7l7-4 7 4v14" />
            </svg>
          </div>
        </div>
        <div class="kpi-value">${totalColleges}</div>
        <div class="kpi-indicator">
          <span>Narail · <strong>Science Group</strong></span>
        </div>
      </div>

      <div class="kpi-card">
        <div class="kpi-card-top">
          <span class="kpi-label">Total Passed</span>
          <div class="kpi-icon green" aria-hidden="true">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
              <path d="M20 6 9 17l-5-5" />
            </svg>
          </div>
        </div>
        <div class="kpi-value">${passed}</div>
        <div class="kpi-indicator">
          <span><strong>${passRate}%</strong> of total enrolled</span>
        </div>
      </div>

      <div class="kpi-card">
        <div class="kpi-card-top">
          <span class="kpi-label">Total Failed</span>
          <div class="kpi-icon red" aria-hidden="true">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
              <circle cx="12" cy="12" r="10" />
              <path d="m15 9-6 6M9 9l6 6" />
            </svg>
          </div>
        </div>
        <div class="kpi-value">${failed}</div>
        <div class="kpi-indicator">
          <span><strong>${failRate}%</strong> of total enrolled</span>
        </div>
      </div>

      <div class="kpi-card">
        <div class="kpi-card-top">
          <span class="kpi-label">Total Absent</span>
          <div class="kpi-icon gray" aria-hidden="true">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10" />
              <line x1="8" y1="12" x2="16" y2="12" />
            </svg>
          </div>
        </div>
        <div class="kpi-value">${absent}</div>
        <div class="kpi-indicator">
          <span><strong>${absentRate}%</strong> non-attendance</span>
        </div>
      </div>

      <div class="kpi-card">
        <div class="kpi-card-top">
          <span class="kpi-label">Overall Pass Rate</span>
          <div class="kpi-icon green" aria-hidden="true">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="22 7 13.5 15.5 8.5 10.5 2 17" />
              <polyline points="16 7 22 7 22 13" />
            </svg>
          </div>
        </div>
        <div class="kpi-value">${passRate}%</div>
        <div class="kpi-indicator">
          <span><strong>${appearedPassRate}%</strong> of appeared</span>
        </div>
      </div>
    `;
  }

  function renderDistributionChart(students) {
    const total = students.length;
    const passed = students.filter((s) => s.result === 'PASS').length;
    const failed = students.filter((s) => s.result === 'FAIL').length;
    const absent = students.filter((s) => s.result === 'ABSENT').length;

    const passPct = total > 0 ? ((passed / total) * 100).toFixed(2) : '0.00';
    const failPct = total > 0 ? ((failed / total) * 100).toFixed(2) : '0.00';
    const absentPct = total > 0 ? ((absent / total) * 100).toFixed(2) : '0.00';

    const legendEl = document.getElementById('overall-distribution-legend');
    if (legendEl) {
      legendEl.innerHTML = `
        <div class="doughnut-stat-item">
          <div class="dsi-left">
            <span class="color-swatch pass"></span>
            <span class="dsi-label">PASS</span>
          </div>
          <div class="dsi-values">
            <span class="dsi-count">${passed}</span>
            <span class="dsi-pct">(${passPct}%)</span>
          </div>
        </div>
        <div class="doughnut-stat-item">
          <div class="dsi-left">
            <span class="color-swatch fail"></span>
            <span class="dsi-label">FAIL</span>
          </div>
          <div class="dsi-values">
            <span class="dsi-count">${failed}</span>
            <span class="dsi-pct">(${failPct}%)</span>
          </div>
        </div>
        <div class="doughnut-stat-item">
          <div class="dsi-left">
            <span class="color-swatch absent"></span>
            <span class="dsi-label">ABSENT</span>
          </div>
          <div class="dsi-values">
            <span class="dsi-count">${absent}</span>
            <span class="dsi-pct">(${absentPct}%)</span>
          </div>
        </div>
      `;
    }

    const canvas = document.getElementById('chart-overall-distribution');
    if (!canvas || typeof Chart === 'undefined') return;

    if (distributionChartInstance) {
      distributionChartInstance.destroy();
    }

    distributionChartInstance = new Chart(canvas, {
      type: 'doughnut',
      data: {
        labels: ['PASS', 'FAIL', 'ABSENT'],
        datasets: [
          {
            data: [passed, failed, absent],
            backgroundColor: ['#16a34a', '#dc2626', '#64748b'],
            borderColor: '#ffffff',
            borderWidth: 2,
            hoverOffset: 6
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '66%',
        plugins: {
          legend: {
            display: false
          },
          tooltip: {
            callbacks: {
              label: function (ctx) {
                const count = ctx.raw;
                const pct = total > 0 ? ((count / total) * 100).toFixed(2) : '0.00';
                return ` ${ctx.label}: ${count} students (${pct}%)`;
              }
            }
          }
        }
      }
    });
  }

  function renderCollegeComparisonChart(collegeStats, mode) {
    const canvas = document.getElementById('chart-college-comparison');
    if (!canvas || typeof Chart === 'undefined') return;

    if (collegeComparisonChartInstance) {
      collegeComparisonChartInstance.destroy();
    }

    // Sort according to active mode descending for clean visual comparison
    const sorted = [...collegeStats].sort((a, b) => {
      if (mode === 'passRate') return b.passRate - a.passRate;
      if (mode === 'passed') return b.passed - a.passed;
      return b.total - a.total;
    });

    const labels = sorted.map((c) => c.college);

    let datasets = [];
    let xTitle = '';
    let xMax = undefined;

    if (mode === 'total') {
      xTitle = 'Number of Students';
      datasets = [
        {
          label: 'Total Students',
          data: sorted.map((c) => c.total),
          backgroundColor: '#2563eb',
          borderRadius: 4,
          barPercentage: 0.72
        },
        {
          label: 'Passed',
          data: sorted.map((c) => c.passed),
          backgroundColor: '#16a34a',
          borderRadius: 4,
          barPercentage: 0.72
        },
        {
          label: 'Failed',
          data: sorted.map((c) => c.failed),
          backgroundColor: '#dc2626',
          borderRadius: 4,
          barPercentage: 0.72
        },
        {
          label: 'Absent',
          data: sorted.map((c) => c.absent),
          backgroundColor: '#64748b',
          borderRadius: 4,
          barPercentage: 0.72
        }
      ];
    } else if (mode === 'passRate') {
      xTitle = 'Pass Percentage (%)';
      xMax = 100;
      datasets = [
        {
          label: 'Pass Percentage (%)',
          data: sorted.map((c) => Number(c.passRate.toFixed(2))),
          backgroundColor: '#2563eb',
          borderRadius: 4,
          barThickness: 22
        }
      ];
    } else if (mode === 'passed') {
      xTitle = 'Passed Student Count';
      datasets = [
        {
          label: 'Passed Students',
          data: sorted.map((c) => c.passed),
          backgroundColor: '#16a34a',
          borderRadius: 4,
          barThickness: 22
        }
      ];
    }

    collegeComparisonChartInstance = new Chart(canvas, {
      type: 'bar',
      data: {
        labels,
        datasets
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: {
            beginAtZero: true,
            max: xMax,
            grid: {
              color: '#f1f5f9'
            },
            title: {
              display: true,
              text: xTitle,
              font: { size: 11, weight: '600' },
              color: '#64748b'
            }
          },
          y: {
            grid: {
              display: false
            },
            ticks: {
              font: { size: 12, weight: '600' },
              color: '#0f172a'
            }
          }
        },
        plugins: {
          legend: {
            display: mode === 'total',
            position: 'top',
            labels: {
              boxWidth: 10,
              usePointStyle: false,
              font: { size: 11, weight: '600' }
            }
          },
          tooltip: {
            callbacks: {
              afterBody: function (items) {
                const idx = items[0].dataIndex;
                const col = sorted[idx];
                return [
                  `────────────────────`,
                  `Total Students: ${col.total}`,
                  `Passed: ${col.passed} (${col.passRate.toFixed(2)}%)`,
                  `Failed: ${col.failed}`,
                  `Absent: ${col.absent}`,
                  `GPA 5.00 Count: ${col.gpa5Count}`
                ];
              }
            }
          }
        }
      }
    });
  }

  function renderQuickInsights(students, collegeStats) {
    const eligibleColleges = collegeStats.filter((c) => c.total > 0);
    const bestByPassRate = [...eligibleColleges].sort((a, b) => b.passRate - a.passRate)[0];
    const mostStudents = [...eligibleColleges].sort((a, b) => b.total - a.total)[0];
    const mostSuccessful = [...eligibleColleges].sort((a, b) => b.passed - a.passed)[0];
    const mostFailures = [...eligibleColleges].sort((a, b) => b.failed - a.failed)[0];
    const totalGpa5 = students.filter((s) => s.result === 'PASS' && s.gpa === 5.0).length;

    const container = document.getElementById('overview-insights-grid');
    if (!container) return;

    container.innerHTML = `
      <div class="insight-item">
        <span class="insight-kicker">Best Pass Percentage</span>
        <div class="insight-value">${bestByPassRate ? bestByPassRate.college : 'N/A'}</div>
        <div class="insight-meta">${bestByPassRate ? bestByPassRate.passRate.toFixed(2) + '% Pass Rate' : ''}</div>
      </div>

      <div class="insight-item">
        <span class="insight-kicker">Largest Student Cohort</span>
        <div class="insight-value">${mostStudents ? mostStudents.college : 'N/A'}</div>
        <div class="insight-meta">${mostStudents ? mostStudents.total + ' Students (54.9% of total)' : ''}</div>
      </div>

      <div class="insight-item">
        <span class="insight-kicker">Most Successful Students</span>
        <div class="insight-value">${mostSuccessful ? mostSuccessful.college : 'N/A'}</div>
        <div class="insight-meta">${mostSuccessful ? mostSuccessful.passed + ' Passed Students' : ''}</div>
      </div>

      <div class="insight-item">
        <span class="insight-kicker">Highest Number of Failures</span>
        <div class="insight-value">${mostFailures ? mostFailures.college : 'N/A'}</div>
        <div class="insight-meta">${mostFailures ? mostFailures.failed + ' Failed (' + ((mostFailures.failed / mostFailures.total) * 100).toFixed(1) + '%)' : ''}</div>
      </div>

      <div class="insight-item">
        <span class="insight-kicker">Total Achieving GPA 5.00</span>
        <div class="insight-value">${totalGpa5} Students</div>
        <div class="insight-meta">${((totalGpa5 / students.length) * 100).toFixed(2)}% of all examinees</div>
      </div>
    `;
  }

  function renderCollegeStatsTable(collegeStats) {
    const tbody = document.getElementById('overview-college-tbody');
    const tfoot = document.getElementById('overview-college-tfoot');
    if (!tbody || !tfoot) return;

    const maxPassRate = Math.max(...collegeStats.map((c) => c.passRate));
    const maxTotal = Math.max(...collegeStats.map((c) => c.total));

    const sorted = [...collegeStats].sort((a, b) => {
      let valA = a[currentSortCol];
      let valB = b[currentSortCol];
      if (typeof valA === 'string') {
        return currentSortDir === 'asc'
          ? valA.localeCompare(valB)
          : valB.localeCompare(valA);
      }
      return currentSortDir === 'asc' ? valA - valB : valB - valA;
    });

    tbody.innerHTML = sorted
      .map((c) => {
        const isHighestPass = Math.abs(c.passRate - maxPassRate) < 0.001;
        const isLargestCohort = c.total === maxTotal;

        const descriptors = [];
        if (isHighestPass) descriptors.push('Highest Pass Rate');
        if (isLargestCohort) descriptors.push('Largest Cohort');

        return `
          <tr class="clickable-row" data-open-college="${c.college}" title="Click to view detailed statistics for ${c.college}">
            <td>
              <strong>${c.college}</strong>
              ${descriptors.length > 0 ? `<span class="highlight-meta">· ${descriptors.join(' · ')}</span>` : ''}
            </td>
            <td class="text-right mono">${c.total}${isLargestCohort ? ' ★' : ''}</td>
            <td class="text-right mono">${c.passed}</td>
            <td class="text-right mono">${c.failed}</td>
            <td class="text-right mono">${c.absent}</td>
            <td class="text-right mono ${isHighestPass ? 'highlight-pass-text' : ''}">
              ${c.passRate.toFixed(2)}%
            </td>
          </tr>
        `;
      })
      .join('');

    const totalAll = collegeStats.reduce((acc, c) => acc + c.total, 0);
    const passedAll = collegeStats.reduce((acc, c) => acc + c.passed, 0);
    const failedAll = collegeStats.reduce((acc, c) => acc + c.failed, 0);
    const absentAll = collegeStats.reduce((acc, c) => acc + c.absent, 0);
    const overallPassRate = totalAll > 0 ? ((passedAll / totalAll) * 100).toFixed(2) : '0.00';

    tfoot.innerHTML = `
      <tr>
        <td>All 7 Colleges Total</td>
        <td class="text-right mono">${totalAll}</td>
        <td class="text-right mono">${passedAll}</td>
        <td class="text-right mono">${failedAll}</td>
        <td class="text-right mono">${absentAll}</td>
        <td class="text-right mono">${overallPassRate}%</td>
      </tr>
    `;

    // Bind row clicks to open college detail view
    tbody.querySelectorAll('tr[data-open-college]').forEach((row) => {
      row.addEventListener('click', () => {
        const colName = row.getAttribute('data-open-college');
        if (window.NarailApp && typeof window.NarailApp.openCollegeDetails === 'function') {
          window.NarailApp.openCollegeDetails(colName);
        }
      });
    });
  }

  function renderDataValidationSection(meta, students, collegeStats) {
    const summaryEl = document.getElementById('data-validation-summary');
    const filesTbody = document.getElementById('data-source-files-tbody');
    if (!summaryEl || !filesTbody || !meta) return;

    summaryEl.innerHTML = `
      <div class="val-box">
        <div class="val-box-label">Source Files Processed</div>
        <div class="val-box-value">${meta.totalFilesProcessed}</div>
      </div>
      <div class="val-box">
        <div class="val-box-label">Total Records Found</div>
        <div class="val-box-value">${meta.totalRecordsFound}</div>
      </div>
      <div class="val-box">
        <div class="val-box-label">Successfully Parsed</div>
        <div class="val-box-value">${meta.successfullyParsedRecords}</div>
      </div>
      <div class="val-box">
        <div class="val-box-label">Records with Parsing Issues</div>
        <div class="val-box-value">${meta.recordsWithParsingIssues}</div>
      </div>
      <div class="val-box">
        <div class="val-box-label">Duplicate Records Detected</div>
        <div class="val-box-value">${meta.duplicateRecordsDetected}</div>
      </div>
    `;

    // Map source file to college
    const fileToCollege = {};
    students.forEach((s) => {
      if (!fileToCollege[s.sourceFile]) {
        fileToCollege[s.sourceFile] = { college: s.college, eiin: s.eiin };
      }
    });

    filesTbody.innerHTML = (meta.sourceFiles || [])
      .map((f) => {
        const colInfo = fileToCollege[f.fileName] || { college: 'Not Available', eiin: 'Not Available' };
        return `
          <tr>
            <td class="mono">${f.fileName}</td>
            <td><strong>${colInfo.college}</strong></td>
            <td class="mono">${colInfo.eiin}</td>
            <td class="text-right mono">${f.recordsFound}</td>
            <td class="text-right mono">${f.recordsParsed}</td>
            <td class="text-right mono">${f.parsingIssues}</td>
          </tr>
        `;
      })
      .join('');
  }

  function initDashboard(students, meta) {
    const collegeStats = computeCollegeStats(students);

    renderKpiCards(students, collegeStats);
    renderDistributionChart(students);
    renderCollegeComparisonChart(collegeStats, currentChartMode);
    renderQuickInsights(students, collegeStats);
    renderCollegeStatsTable(collegeStats);
    renderDataValidationSection(meta, students, collegeStats);

    // Chart mode toggle buttons
    document.querySelectorAll('[data-chart-mode]').forEach((btn) => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('[data-chart-mode]').forEach((b) => b.classList.remove('active'));
        btn.classList.add('active');
        currentChartMode = btn.getAttribute('data-chart-mode');
        renderCollegeComparisonChart(collegeStats, currentChartMode);
      });
    });

    // Sortable table headers
    const tableHeaders = document.querySelectorAll('#overview-college-table th[data-sort-col]');
    tableHeaders.forEach((th) => {
      th.addEventListener('click', () => {
        const col = th.getAttribute('data-sort-col');
        if (currentSortCol === col) {
          currentSortDir = currentSortDir === 'asc' ? 'desc' : 'asc';
        } else {
          currentSortCol = col;
          currentSortDir = col === 'college' ? 'asc' : 'desc';
        }

        tableHeaders.forEach((h) => {
          h.classList.remove('active-sort');
          const ind = h.querySelector('.sort-indicator');
          if (ind) ind.textContent = '';
        });

        th.classList.add('active-sort');
        const activeInd = th.querySelector('.sort-indicator');
        if (activeInd) activeInd.textContent = currentSortDir === 'asc' ? '↑' : '↓';

        renderCollegeStatsTable(collegeStats);
      });
    });

    const exploreBtn = document.getElementById('overview-explore-students-btn');
    if (exploreBtn) {
      exploreBtn.addEventListener('click', () => {
        if (window.NarailApp && typeof window.NarailApp.switchSection === 'function') {
          window.NarailApp.switchSection('students');
        }
      });
    }
  }

  window.NarailDashboard = {
    initDashboard,
    computeCollegeStats
  };
})();
