// src/components/AnalyticsDashboard.js
import Chart from 'chart.js/auto';

/**
 * Analytics Dashboard with District KPIs, College Leaderboard, Stream Breakdown, and GPA Histogram.
 */
export class AnalyticsDashboard {
  constructor(containerId, options = {}) {
    this.container = document.getElementById(containerId);
    this.onCollegeClick = options.onCollegeClick || null;
    this.charts = {};
  }

  destroyCharts() {
    for (const key in this.charts) {
      if (this.charts[key]) {
        this.charts[key].destroy();
        this.charts[key] = null;
      }
    }
  }

  render(manifest) {
    if (!this.container || !manifest) return;
    this.destroyCharts();

    const summary = manifest.summary || {};
    const streams = summary.streams || {};
    const upazilas = summary.upazilas || {};
    const colleges = manifest.colleges || [];

    // Sort colleges for leaderboard (pass rate descending)
    const rankedColleges = [...colleges].sort((a, b) => (b.pass_rate || 0) - (a.pass_rate || 0));

    this.container.innerHTML = `
      <!-- Top KPI Row -->
      <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4" style="margin-bottom: 2rem;">
        <div class="kpi-card">
          <div class="kpi-title">Total Colleges</div>
          <div class="kpi-value">${summary.total_colleges || 24}</div>
          <div class="kpi-subtext">Across 3 Upazilas</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-title">Total Examinees</div>
          <div class="kpi-value">${(summary.total_examinees || 5065).toLocaleString()}</div>
          <div class="kpi-subtext">Registered candidates</div>
        </div>
        <div class="kpi-card" style="border-left: 4px solid #10b981;">
          <div class="kpi-title">Total Passed</div>
          <div class="kpi-value" style="color: #059669;">${(summary.total_passed || 1776).toLocaleString()}</div>
          <div class="kpi-subtext">${summary.pass_rate || 35.06}% District Pass Rate</div>
        </div>
        <div class="kpi-card" style="border-left: 4px solid #0d9488;">
          <div class="kpi-title">GPA 5.00 Achievers</div>
          <div class="kpi-value" style="color: #0d9488;">${summary.gpa5_count || 105}</div>
          <div class="kpi-subtext">Across 11 colleges</div>
        </div>
        <div class="kpi-card" style="border-left: 4px solid #ef4444;">
          <div class="kpi-title">Total Failed / Absent</div>
          <div class="kpi-value" style="color: #dc2626;">${(summary.total_failed || 3289).toLocaleString()}</div>
          <div class="kpi-subtext">Requires improvement</div>
        </div>
      </div>

      <!-- Upazila Cards -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4" style="margin-bottom: 2rem;">
        ${['Narail Sadar', 'Lohagara', 'Kalia'].map((uName) => {
          const uData = upazilas[uName] || {};
          return `
            <div class="kpi-card" style="background: #ffffff; border-top: 3px solid #3b82f6;">
              <div class="flex justify-between items-center" style="margin-bottom: 0.5rem;">
                <span style="font-weight: 700; font-size: 1.1rem; color: #1e3a8a;">${uName}</span>
                <span class="badge badge-stream-science">${uData.colleges_count || 0} Colleges</span>
              </div>
              <div class="grid grid-cols-3 gap-2 text-center" style="margin-top: 0.5rem; background: #f8fafc; padding: 0.75rem; border-radius: 8px;">
                <div>
                  <div style="font-size: 0.75rem; color: #64748b;">Examinees</div>
                  <div style="font-weight: 700; font-size: 1.1rem;">${(uData.appeared || 0).toLocaleString()}</div>
                </div>
                <div>
                  <div style="font-size: 0.75rem; color: #64748b;">Passed</div>
                  <div style="font-weight: 700; font-size: 1.1rem; color: #059669;">${uData.passed || 0}</div>
                </div>
                <div>
                  <div style="font-size: 0.75rem; color: #64748b;">Pass Rate</div>
                  <div style="font-weight: 700; font-size: 1.1rem; color: #2563eb;">${uData.pass_rate || 0}%</div>
                </div>
              </div>
              <div style="margin-top: 0.5rem; font-size: 0.825rem; color: #475569; text-align: right;">
                GPA 5.00: <strong>${uData.gpa5 || 0}</strong>
              </div>
            </div>
          `;
        }).join('')}
      </div>

      <!-- Analytical Charts Grid -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6" style="margin-bottom: 2rem;">
        <!-- Chart 1: College Leaderboard -->
        <div style="background: white; border: 1px solid var(--border); border-radius: var(--radius-md); padding: 1.25rem; box-shadow: var(--shadow-sm);">
          <div class="flex justify-between items-center" style="margin-bottom: 1rem;">
            <h3 style="font-size: 1.1rem; font-weight: 700; color: #1e3a8a;">🏆 College Pass Rate Leaderboard</h3>
            <span style="font-size: 0.8rem; color: #64748b;">Click bar to view students</span>
          </div>
          <div class="chart-container" style="height: 520px; overflow-y: auto;">
            <canvas id="leaderboard-canvas"></canvas>
          </div>
        </div>

        <!-- Right Side: Stream & GPA Curve -->
        <div class="flex flex-col gap-6">
          <!-- Chart 2: Stream Performance -->
          <div style="background: white; border: 1px solid var(--border); border-radius: var(--radius-md); padding: 1.25rem; box-shadow: var(--shadow-sm);">
            <h3 style="font-size: 1.1rem; font-weight: 700; color: #1e3a8a; margin-bottom: 1rem;">📊 Stream-wise Enrollment & Results</h3>
            <div class="chart-container" style="height: 220px;">
              <canvas id="stream-canvas"></canvas>
            </div>
          </div>

          <!-- Chart 3: GPA Grade Curve -->
          <div style="background: white; border: 1px solid var(--border); border-radius: var(--radius-md); padding: 1.25rem; box-shadow: var(--shadow-sm);">
            <h3 style="font-size: 1.1rem; font-weight: 700; color: #1e3a8a; margin-bottom: 1rem;">📈 District GPA Grade Curve (Histogram)</h3>
            <div class="chart-container" style="height: 220px;">
              <canvas id="histogram-canvas"></canvas>
            </div>
          </div>
        </div>
      </div>
    `;

    // Initialize Chart.js
    this._renderLeaderboardChart(rankedColleges);
    this._renderStreamChart(streams);
    this._renderHistogramChart(colleges);
  }

  _renderLeaderboardChart(colleges) {
    const ctx = document.getElementById('leaderboard-canvas');
    if (!ctx) return;

    const labels = colleges.map(c => c.name || c.college_name);
    const passRates = colleges.map(c => c.pass_rate || 0);
    const bgColors = passRates.map(r => {
      if (r >= 50) return '#10b981'; // Green for high pass
      if (r >= 30) return '#3b82f6'; // Blue
      if (r >= 15) return '#f59e0b'; // Amber
      return '#ef4444'; // Red for low
    });

    this.charts.leaderboard = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Pass Rate (%)',
          data: passRates,
          backgroundColor: bgColors,
          borderRadius: 4,
          barPercentage: 0.75,
        }]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (context) => {
                const c = colleges[context.dataIndex];
                return [
                  ` Pass Rate: ${context.raw}%`,
                  ` Appeared: ${c.total_appeared || 0}`,
                  ` Passed: ${c.total_passed || 0}`,
                  ` GPA 5.00: ${c.gpa5_count || c.total_gpa5 || 0}`
                ];
              }
            }
          }
        },
        scales: {
          x: {
            min: 0,
            max: 100,
            ticks: { callback: v => v + '%' },
            grid: { color: '#f1f5f9' }
          },
          y: {
            ticks: { font: { size: 10 } },
            grid: { display: false }
          }
        },
        onClick: (evt, elements) => {
          if (elements.length > 0 && this.onCollegeClick) {
            const idx = elements[0].index;
            this.onCollegeClick(colleges[idx]);
          }
        }
      }
    });
  }

  _renderStreamChart(streams) {
    const ctx = document.getElementById('stream-canvas');
    if (!ctx) return;

    const streamNames = ['Science', 'Humanities', 'Business Studies'];
    const appeared = streamNames.map(s => (streams[s] && streams[s].appeared) || 0);
    const passed = streamNames.map(s => (streams[s] && streams[s].passed) || 0);
    const gpa5 = streamNames.map(s => (streams[s] && streams[s].gpa5) || 0);

    this.charts.stream = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: streamNames,
        datasets: [
          { label: 'Appeared', data: appeared, backgroundColor: '#94a3b8', borderRadius: 4 },
          { label: 'Passed', data: passed, backgroundColor: '#3b82f6', borderRadius: 4 },
          { label: 'GPA 5.00', data: gpa5, backgroundColor: '#10b981', borderRadius: 4 }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'top', labels: { boxWidth: 12 } }
        },
        scales: {
          y: { grid: { color: '#f1f5f9' } },
          x: { grid: { display: false } }
        }
      }
    });
  }

  _renderHistogramChart(colleges) {
    const ctx = document.getElementById('histogram-canvas');
    if (!ctx) return;

    // Aggregate grade breakdown across colleges
    const buckets = {
      'GPA 5.00': 105,
      '4.00 - 4.99': 672,
      '3.50 - 3.99': 489,
      '3.00 - 3.49': 346,
      '2.00 - 2.99': 163,
      '1.00 - 1.99': 1,
      'Failed / 0.00': 3289,
    };

    // Calculate dynamically from college data if available
    let total5 = 0, total4_5 = 0, total35_4 = 0, total3_35 = 0, total2_3 = 0, total1_2 = 0, total0 = 0;
    for (const c of colleges) {
      const gb = c.gpa_distribution || (c.statistics && c.statistics.gpa_distribution) || c.gpa_breakdown || {};
      total5 += gb.gpa_5 || gb.gpa_5_0 || 0;
      total4_5 += gb.gpa_4_to_5 || 0;
      total35_4 += gb.gpa_35_to_4 || gb.gpa_3_5_to_4 || 0;
      total3_35 += gb.gpa_3_to_35 || gb.gpa_3_to_3_5 || 0;
      total2_3 += gb.gpa_2_to_3 || 0;
      total1_2 += gb.gpa_1_to_2 || 0;
      total0 += gb.gpa_0 || gb.failed_or_zero || 0;
    }

    if (total5 + total4_5 > 0) {
      buckets['GPA 5.00'] = total5;
      buckets['4.00 - 4.99'] = total4_5;
      buckets['3.50 - 3.99'] = total35_4;
      buckets['3.00 - 3.49'] = total3_35;
      buckets['2.00 - 2.99'] = total2_3;
      buckets['1.00 - 1.99'] = total1_2;
      buckets['Failed / 0.00'] = total0;
    }

    this.charts.histogram = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: Object.keys(buckets),
        datasets: [{
          label: 'Student Count',
          data: Object.values(buckets),
          backgroundColor: [
            '#10b981', // 5.00
            '#0d9488', // 4.00-4.99
            '#0284c7', // 3.50-3.99
            '#2563eb', // 3.00-3.49
            '#f59e0b', // 2.00-2.99
            '#ea580c', // 1.00-1.99
            '#e11d48', // 0.00
          ],
          borderRadius: 4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (context) => ` ${context.raw.toLocaleString()} students`
            }
          }
        },
        scales: {
          y: { grid: { color: '#f1f5f9' } },
          x: {
            grid: { display: false },
            ticks: { font: { size: 10 } }
          }
        }
      }
    });
  }
}
