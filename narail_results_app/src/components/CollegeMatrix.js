// src/components/CollegeMatrix.js

export class CollegeMatrix {
  constructor(containerId, options = {}) {
    this.container = document.getElementById(containerId);
    this.colleges = [];
    this.onCollegeClick = options.onCollegeClick || null;
    this.sortKey = 'pass_rate';
    this.sortAsc = false;
  }

  setColleges(colleges) {
    this.colleges = colleges;
    this.render();
  }

  downloadCSV() {
    if (!this.colleges || this.colleges.length === 0) return;

    const headers = [
      'EIIN', 'College Name', 'Upazila', 'Total Appeared', 'Total Passed', 
      'Pass Rate (%)', 'GPA 5.00 Count',
      'Science Appeared', 'Science Passed', 'Science Pass Rate (%)',
      'Humanities Appeared', 'Humanities Passed', 'Humanities Pass Rate (%)',
      'Business Appeared', 'Business Passed', 'Business Pass Rate (%)'
    ];

    const rows = this.colleges.map(c => {
      const sStats = c.stream_summary || c.stream_stats || {};
      const sci = sStats['Science'] || {};
      const hum = sStats['Humanities'] || {};
      const bus = sStats['Business Studies'] || {};

      return [
        c.eiin,
        `"${(c.name || c.college_name || '').replace(/"/g, '""')}"`,
        c.upazila || '',
        c.total_appeared || 0,
        c.total_passed || 0,
        c.pass_rate || 0.0,
        c.gpa5_count || c.total_gpa5 || 0,
        sci.total || sci.appeared || 0,
        sci.passed || 0,
        sci.pass_rate || 0.0,
        hum.total || hum.appeared || 0,
        hum.passed || 0,
        hum.pass_rate || 0.0,
        bus.total || bus.appeared || 0,
        bus.passed || 0,
        bus.pass_rate || 0.0
      ].join(',');
    });

    const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', 'Narail_HSC_2026_College_Matrix.csv');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }

  render() {
    if (!this.container) return;

    const sorted = [...this.colleges].sort((a, b) => {
      let valA = a[this.sortKey];
      let valB = b[this.sortKey];
      if (this.sortKey === 'gpa5_count') {
        valA = a.gpa5_count || a.total_gpa5 || 0;
        valB = b.gpa5_count || b.total_gpa5 || 0;
      }
      if (typeof valA === 'string') {
        return this.sortAsc ? valA.localeCompare(valB) : valB.localeCompare(valA);
      }
      return this.sortAsc ? (valA || 0) - (valB || 0) : (valB || 0) - (valA || 0);
    });

    this.container.innerHTML = `
      <div style="margin-bottom: 1.5rem;">
        <div class="flex justify-between items-center" style="margin-bottom: 1rem; flex-wrap: wrap; gap: 0.5rem;">
          <div>
            <h2 style="font-size: 1.25rem; font-weight: 700; color: #1e3a8a;">🏫 Narail District 24 Colleges Performance Matrix</h2>
            <p style="font-size: 0.85rem; color: #64748b;">Comprehensive comparison of candidate volume, pass rates, and honors across all participating institutions.</p>
          </div>
          <button id="download-matrix-csv-btn" class="filter-pill-btn active" style="display: flex; align-items: center; gap: 0.4rem; padding: 0.5rem 1rem;">
            <span>📥 Export to CSV</span>
          </button>
        </div>

        <div class="table-container">
          <table class="results-table">
            <thead>
              <tr>
                <th style="cursor: pointer;" data-sort="eiin">EIIN ↕</th>
                <th style="cursor: pointer;" data-sort="name">College Name ↕</th>
                <th style="cursor: pointer;" data-sort="upazila">Upazila ↕</th>
                <th style="cursor: pointer; text-align: center;" data-sort="total_appeared">Appeared ↕</th>
                <th style="cursor: pointer; text-align: center;" data-sort="total_passed">Passed ↕</th>
                <th style="cursor: pointer; text-align: center;" data-sort="pass_rate">Pass Rate ↕</th>
                <th style="cursor: pointer; text-align: center;" data-sort="gpa5_count">GPA 5.00 ↕</th>
                <th style="text-align: center;">Science (App / Pass / Rate)</th>
                <th style="text-align: center;">Humanities (App / Pass / Rate)</th>
                <th style="text-align: center;">Business (App / Pass / Rate)</th>
              </tr>
            </thead>
            <tbody>
              ${sorted.map(c => {
                const sStats = c.stream_summary || c.stream_stats || {};
                const sci = sStats['Science'] || {};
                const hum = sStats['Humanities'] || {};
                const bus = sStats['Business Studies'] || {};
                const gpa5Count = c.gpa5_count || c.total_gpa5 || 0;

                return `
                  <tr data-college-eiin="${c.eiin}">
                    <td style="font-family: monospace; font-weight: 700; color: #1e3a8a;">
                      ${c.eiin}
                    </td>
                    <td style="font-weight: 600;">
                      ${c.name || c.college_name}
                      <div style="font-size: 0.75rem; color: #64748b; font-weight: 400;">Center: ${c.center || 'N/A'}</div>
                    </td>
                    <td>
                      <span class="badge badge-stream-science">${c.upazila}</span>
                    </td>
                    <td style="text-align: center; font-weight: 600;">
                      ${(c.total_appeared || 0).toLocaleString()}
                    </td>
                    <td style="text-align: center; font-weight: 600; color: #059669;">
                      ${(c.total_passed || 0).toLocaleString()}
                    </td>
                    <td style="text-align: center; font-weight: 700; font-size: 0.95rem; color: ${c.pass_rate >= 50 ? '#059669' : c.pass_rate >= 25 ? '#2563eb' : '#dc2626'};">
                      ${c.pass_rate}%
                    </td>
                    <td style="text-align: center; font-weight: 700; color: ${gpa5Count > 0 ? '#0d9488' : '#94a3b8'};">
                      ${gpa5Count > 0 ? `★ ${gpa5Count}` : '0'}
                    </td>
                    <td style="text-align: center; font-size: 0.8rem; color: #334155;">
                      ${sci.total || sci.appeared || 0} / ${sci.passed || 0} (${sci.pass_rate || 0}%)
                    </td>
                    <td style="text-align: center; font-size: 0.8rem; color: #334155;">
                      ${hum.total || hum.appeared || 0} / ${hum.passed || 0} (${hum.pass_rate || 0}%)
                    </td>
                    <td style="text-align: center; font-size: 0.8rem; color: #334155;">
                      ${bus.total || bus.appeared || 0} / ${bus.passed || 0} (${bus.pass_rate || 0}%)
                    </td>
                  </tr>
                `;
              }).join('')}
            </tbody>
          </table>
        </div>
      </div>
    `;

    this._bindEvents();
  }

  _bindEvents() {
    // CSV button
    const csvBtn = document.getElementById('download-matrix-csv-btn');
    if (csvBtn) {
      csvBtn.addEventListener('click', () => this.downloadCSV());
    }

    // Sort header clicks
    const headers = this.container.querySelectorAll('[data-sort]');
    headers.forEach(th => {
      th.addEventListener('click', () => {
        const key = th.getAttribute('data-sort');
        if (this.sortKey === key) {
          this.sortAsc = !this.sortAsc;
        } else {
          this.sortKey = key;
          this.sortAsc = false;
        }
        this.render();
      });
    });

    // Row clicks to filter
    const rows = this.container.querySelectorAll('[data-college-eiin]');
    rows.forEach(tr => {
      tr.addEventListener('click', () => {
        const eiin = tr.getAttribute('data-college-eiin');
        const c = this.colleges.find(item => String(item.eiin) === String(eiin));
        if (c && this.onCollegeClick) {
          this.onCollegeClick(c);
        }
      });
    });
  }
}
