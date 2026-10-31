/**
 * Subject Analysis Module (js/subjects.js)
 * Analyzes subject-wise grade distributions (A+, A, A-, B, C, D, F) across all colleges
 * and individual colleges. Never counts missing grades as F.
 */

(function () {
  let allStudents = [];
  let selectedCollege = 'ALL';
  let selectedCompareSubject = 'Physics';

  let stackedGradeChart = null;
  let aPlusPctChart = null;
  let fPctChart = null;
  let collegeCompareChart = null;

  const VALID_GRADES = ['A+', 'A', 'A-', 'B', 'C', 'D', 'F'];

  function computeSubjectStats(students, collegeFilter) {
    const filtered =
      collegeFilter === 'ALL'
        ? students
        : students.filter((s) => s.college === collegeFilter);

    const map = {};

    filtered.forEach((s) => {
      const subs = s.subjects || {};
      Object.entries(subs).forEach(([subName, rawGrade]) => {
        const grade = (rawGrade || '').trim();
        // Never count missing grades as F; only include actual valid grades present in source
        if (!VALID_GRADES.includes(grade)) return;

        if (!map[subName]) {
          map[subName] = {
            subject: subName,
            totalGraded: 0,
            'A+': 0,
            A: 0,
            'A-': 0,
            B: 0,
            C: 0,
            D: 0,
            F: 0
          };
        }
        map[subName][grade] += 1;
        map[subName].totalGraded += 1;
      });
    });

    return Object.values(map)
      .map((item) => {
        const t = item.totalGraded;
        const passed = t - item.F;
        return {
          ...item,
          aPlusPct: t > 0 ? (item['A+'] / t) * 100 : 0,
          fPct: t > 0 ? (item.F / t) * 100 : 0,
          passPct: t > 0 ? (passed / t) * 100 : 0
        };
      })
      .sort((a, b) => b.totalGraded - a.totalGraded);
  }

  function renderSubjectTable(subjectStats) {
    const tbody = document.getElementById('subject-stats-tbody');
    const subtitle = document.getElementById('subject-table-subtitle');
    if (!tbody) return;

    if (subtitle) {
      subtitle.textContent =
        selectedCollege === 'ALL'
          ? 'Showing actual recorded grades across All 7 Colleges (missing/absent grades excluded)'
          : `Showing actual recorded grades for ${selectedCollege} (missing/absent grades excluded)`;
    }

    if (subjectStats.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="12" class="text-center" style="padding: 28px; color: var(--text-muted);">
            No recorded subject grades found for this selection.
          </td>
        </tr>
      `;
      return;
    }

    tbody.innerHTML = subjectStats
      .map(
        (s) => `
        <tr>
          <td><strong>${s.subject}</strong></td>
          <td class="text-right mono">${s.totalGraded}</td>
          <td class="text-right mono" style="color: var(--status-pass); font-weight: 700;">${s['A+']}</td>
          <td class="text-right mono">${s.A}</td>
          <td class="text-right mono">${s['A-']}</td>
          <td class="text-right mono">${s.B}</td>
          <td class="text-right mono">${s.C}</td>
          <td class="text-right mono">${s.D}</td>
          <td class="text-right mono" style="color: var(--status-fail); font-weight: 700;">${s.F}</td>
          <td class="text-right mono">${s.aPlusPct.toFixed(2)}%</td>
          <td class="text-right mono">${s.fPct.toFixed(2)}%</td>
          <td class="text-right mono"><strong>${s.passPct.toFixed(2)}%</strong></td>
        </tr>
      `
      )
      .join('');
  }

  function formatSubjectLabel(sub) {
    if (window.innerWidth > 640) {
      return sub === 'Information & Communication Technology' ? 'ICT' : sub;
    }
    const shortMap = {
      'Information & Communication Technology': 'ICT',
      'Higher Mathematics': 'Higher Math',
      'Agriculture Studies': 'Agriculture'
    };
    return shortMap[sub] || sub;
  }

  function renderSubjectCharts(subjectStats) {
    if (typeof Chart === 'undefined') return;

    const labels = subjectStats.map((s) => formatSubjectLabel(s.subject));

    // 1. Stacked bar chart: Grade distribution by subject
    const stackedCanvas = document.getElementById('chart-subject-stacked');
    if (stackedCanvas) {
      if (stackedGradeChart) stackedGradeChart.destroy();

      const gradeSeries = [
        { key: 'A+', color: '#16a34a' },
        { key: 'A', color: '#2563eb' },
        { key: 'A-', color: '#0284c7' },
        { key: 'B', color: '#64748b' },
        { key: 'C', color: '#ca8a04' },
        { key: 'D', color: '#ea580c' },
        { key: 'F', color: '#dc2626' }
      ];

      stackedGradeChart = new Chart(stackedCanvas, {
        type: 'bar',
        data: {
          labels,
          datasets: gradeSeries.map((g) => ({
            label: g.key,
            data: subjectStats.map((s) => s[g.key]),
            backgroundColor: g.color,
            borderRadius: 2
          }))
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            x: { stacked: true, grid: { display: false } },
            y: {
              stacked: true,
              beginAtZero: true,
              ticks: { precision: 0 },
              grid: { color: '#f1f5f9' },
              title: { display: true, text: 'Number of Graded Students', font: { size: 11, weight: '600' } }
            }
          },
          plugins: {
            legend: {
              position: 'top',
              labels: { boxWidth: 12, font: { size: 11, weight: '600' } }
            },
            tooltip: {
              callbacks: {
                title: function (items) {
                  return subjectStats[items[0].dataIndex].subject;
                }
              }
            }
          }
        }
      });
    }

    // 2. Subject-wise A+ Percentage
    const aPlusCanvas = document.getElementById('chart-subject-aplus');
    if (aPlusCanvas) {
      if (aPlusPctChart) aPlusPctChart.destroy();
      const sortedAPlus = [...subjectStats].sort((a, b) => b.aPlusPct - a.aPlusPct);

      aPlusPctChart = new Chart(aPlusCanvas, {
        type: 'bar',
        data: {
          labels: sortedAPlus.map((s) => formatSubjectLabel(s.subject)),
          datasets: [
            {
              label: 'A+ Percentage (%)',
              data: sortedAPlus.map((s) => Number(s.aPlusPct.toFixed(2))),
              backgroundColor: '#16a34a',
              borderRadius: 4,
              barPercentage: 0.65
            }
          ]
        },
        options: {
          indexAxis: 'y',
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            x: {
              beginAtZero: true,
              max: 100,
              grid: { color: '#f1f5f9' },
              title: { display: true, text: 'A+ Rate (%)', font: { size: 11, weight: '600' } }
            },
            y: { grid: { display: false } }
          },
          plugins: {
            legend: { display: false },
            tooltip: {
              callbacks: {
                title: function (items) {
                  return sortedAPlus[items[0].dataIndex].subject;
                },
                label: function (ctx) {
                  const item = sortedAPlus[ctx.dataIndex];
                  return ` A+ Rate: ${item.aPlusPct.toFixed(2)}% (${item['A+']} of ${item.totalGraded} students)`;
                }
              }
            }
          }
        }
      });
    }

    // 3. Subject-wise F Percentage
    const fCanvas = document.getElementById('chart-subject-f');
    if (fCanvas) {
      if (fPctChart) fPctChart.destroy();
      const sortedF = [...subjectStats].sort((a, b) => b.fPct - a.fPct);

      fPctChart = new Chart(fCanvas, {
        type: 'bar',
        data: {
          labels: sortedF.map((s) => formatSubjectLabel(s.subject)),
          datasets: [
            {
              label: 'F Grade Percentage (%)',
              data: sortedF.map((s) => Number(s.fPct.toFixed(2))),
              backgroundColor: '#dc2626',
              borderRadius: 4,
              barPercentage: 0.65
            }
          ]
        },
        options: {
          indexAxis: 'y',
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            x: {
              beginAtZero: true,
              max: 100,
              grid: { color: '#f1f5f9' },
              title: { display: true, text: 'F Rate (%)', font: { size: 11, weight: '600' } }
            },
            y: { grid: { display: false } }
          },
          plugins: {
            legend: { display: false },
            tooltip: {
              callbacks: {
                title: function (items) {
                  return sortedF[items[0].dataIndex].subject;
                },
                label: function (ctx) {
                  const item = sortedF[ctx.dataIndex];
                  return ` F Rate: ${item.fPct.toFixed(2)}% (${item.F} of ${item.totalGraded} students)`;
                }
              }
            }
          }
        }
      });
    }
  }

  function renderCrossCollegeSubjectComparison() {
    const canvas = document.getElementById('chart-subject-college-compare');
    if (!canvas || typeof Chart === 'undefined') return;

    if (collegeCompareChart) collegeCompareChart.destroy();

    const colleges = [...new Set(allStudents.map((s) => s.college))].sort();
    const rows = colleges.map((col) => {
      let total = 0;
      let passed = 0;
      let aPlus = 0;
      let failed = 0;

      allStudents.forEach((s) => {
        if (s.college !== col) return;
        const grd = ((s.subjects || {})[selectedCompareSubject] || '').trim();
        if (!VALID_GRADES.includes(grd)) return;
        total += 1;
        if (grd === 'F') {
          failed += 1;
        } else {
          passed += 1;
          if (grd === 'A+') aPlus += 1;
        }
      });

      return {
        college: col,
        total,
        passed,
        aPlus,
        failed,
        passPct: total > 0 ? (passed / total) * 100 : 0,
        aPlusPct: total > 0 ? (aPlus / total) * 100 : 0,
        fPct: total > 0 ? (failed / total) * 100 : 0
      };
    });

    collegeCompareChart = new Chart(canvas, {
      type: 'bar',
      data: {
        labels: rows.map((r) => r.college),
        datasets: [
          {
            label: `${selectedCompareSubject} — Pass %`,
            data: rows.map((r) => Number(r.passPct.toFixed(2))),
            backgroundColor: '#2563eb',
            borderRadius: 4
          },
          {
            label: `${selectedCompareSubject} — A+ %`,
            data: rows.map((r) => Number(r.aPlusPct.toFixed(2))),
            backgroundColor: '#16a34a',
            borderRadius: 4
          },
          {
            label: `${selectedCompareSubject} — Fail (F) %`,
            data: rows.map((r) => Number(r.fPct.toFixed(2))),
            backgroundColor: '#dc2626',
            borderRadius: 4
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true,
            max: 100,
            grid: { color: '#f1f5f9' },
            title: { display: true, text: 'Percentage of Graded Students (%)', font: { size: 11, weight: '600' } }
          },
          x: { grid: { display: false } }
        },
        plugins: {
          legend: {
            position: 'top',
            labels: { boxWidth: 12, font: { size: 11, weight: '600' } }
          },
          tooltip: {
            callbacks: {
              afterBody: function (items) {
                const r = rows[items[0].dataIndex];
                return [
                  `────────────────────`,
                  `Graded Students in ${selectedCompareSubject}: ${r.total}`,
                  `Passed: ${r.passed} (${r.passPct.toFixed(2)}%)`,
                  `A+ Count: ${r.aPlus} (${r.aPlusPct.toFixed(2)}%)`,
                  `Failed (F): ${r.failed} (${r.fPct.toFixed(2)}%)`
                ];
              }
            }
          }
        }
      }
    });
  }

  function updateSubjectAnalysisView() {
    const stats = computeSubjectStats(allStudents, selectedCollege);
    renderSubjectTable(stats);
    renderSubjectCharts(stats);
  }

  function initSubjects(students) {
    allStudents = students;

    // Populate College Filter
    const colSelect = document.getElementById('subject-college-filter');
    if (colSelect) {
      const uniqueColleges = [...new Set(students.map((s) => s.college))].sort();
      colSelect.innerHTML =
        `<option value="ALL">All Colleges (Unified Dataset)</option>` +
        uniqueColleges.map((c) => `<option value="${c}">${c}</option>`).join('');

      colSelect.addEventListener('change', () => {
        selectedCollege = colSelect.value;
        updateSubjectAnalysisView();
      });
    }

    // Populate Subject Comparison Selector
    const allSubStats = computeSubjectStats(students, 'ALL');
    const subCompareSelect = document.getElementById('subject-comparison-select');
    if (subCompareSelect) {
      subCompareSelect.innerHTML = allSubStats
        .map(
          (s) =>
            `<option value="${s.subject}" ${s.subject === selectedCompareSubject ? 'selected' : ''}>${s.subject} (${s.totalGraded} graded)</option>`
        )
        .join('');

      subCompareSelect.addEventListener('change', () => {
        selectedCompareSubject = subCompareSelect.value;
        renderCrossCollegeSubjectComparison();
      });
    }

    updateSubjectAnalysisView();
    renderCrossCollegeSubjectComparison();
  }

  window.NarailSubjects = {
    initSubjects,
    computeSubjectStats
  };
})();
