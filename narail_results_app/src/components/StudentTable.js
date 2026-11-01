// src/components/StudentTable.js

export class StudentTable {
  constructor(containerId, options = {}) {
    this.container = document.getElementById(containerId);
    this.onStudentClick = options.onStudentClick || null;
    this.currentPage = 1;
    this.pageSize = 50;
    this.students = [];
    this.totalStudents = 0;
  }

  setData(students, totalStudents = null) {
    this.students = students;
    this.totalStudents = totalStudents !== null ? totalStudents : students.length;
    this.currentPage = 1;
    this.render();
  }

  render() {
    if (!this.container) return;

    const total = this.students.length;
    const totalPages = Math.ceil(total / this.pageSize) || 1;
    if (this.currentPage > totalPages) this.currentPage = totalPages;

    const startIdx = (this.currentPage - 1) * this.pageSize;
    const endIdx = Math.min(startIdx + this.pageSize, total);
    const pageItems = this.students.slice(startIdx, endIdx);

    this.container.innerHTML = `
      <!-- Table Header & Counter -->
      <div class="flex justify-between items-center" style="margin-bottom: 0.75rem; flex-wrap: wrap; gap: 0.5rem;">
        <div style="font-weight: 600; font-size: 0.95rem; color: #475569;">
          Showing <span style="color: #1e3a8a; font-weight: 700;">${total > 0 ? (startIdx + 1).toLocaleString() : 0} &ndash; ${endIdx.toLocaleString()}</span> of <span style="color: #1e3a8a; font-weight: 700;">${total.toLocaleString()}</span> students
        </div>
        <div class="flex items-center gap-2">
          <label style="font-size: 0.85rem; color: #64748b;">Per page:</label>
          <select id="table-page-size" class="filter-select" style="padding: 0.25rem 0.5rem; width: auto; font-size: 0.85rem;">
            <option value="25" ${this.pageSize === 25 ? 'selected' : ''}>25</option>
            <option value="50" ${this.pageSize === 50 ? 'selected' : ''}>50</option>
            <option value="100" ${this.pageSize === 100 ? 'selected' : ''}>100</option>
          </select>
        </div>
      </div>

      <!-- Desktop / Tablet Table View (hidden on small mobile) -->
      <div class="table-container" style="margin-bottom: 1rem;">
        <table class="results-table">
          <thead>
            <tr>
              <th style="width: 100px;">Roll No</th>
              <th>Student Name</th>
              <th>Institution / EIIN</th>
              <th>Stream</th>
              <th style="text-align: center; width: 90px;">GPA</th>
              <th style="text-align: center; width: 110px;">Status</th>
              <th style="text-align: center; width: 120px;">Grade Sheet</th>
            </tr>
          </thead>
          <tbody>
            ${pageItems.length === 0 ? `
              <tr>
                <td colspan="7" style="text-align: center; padding: 3rem; color: #64748b;">
                  No students found matching current filter criteria.
                </td>
              </tr>
            ` : pageItems.map(s => {
              const gpa = Number(s.gpa || 0);
              const isPass = (s.status || '').toUpperCase().includes('PASS') || gpa > 0;
              const isAbsent = (s.status || '').toUpperCase().includes('ABS');
              const isGpa5 = gpa >= 5.0;

              let statusBadge = `<span class="badge badge-failed">${s.status || 'FAIL'}</span>`;
              if (isPass) {
                statusBadge = isGpa5 
                  ? `<span class="badge badge-gpa5">★ GPA 5.00</span>` 
                  : `<span class="badge badge-passed">PASSED</span>`;
              } else if (isAbsent) {
                statusBadge = `<span class="badge badge-absent">ABSENT</span>`;
              }

              let streamClass = 'badge-stream-humanities';
              const st = (s.stream || '').toUpperCase();
              if (st.includes('SCI')) streamClass = 'badge-stream-science';
              else if (st.includes('BUS')) streamClass = 'badge-stream-business';

              return `
                <tr data-student-roll="${s.roll}">
                  <td style="font-family: monospace; font-weight: 700; color: #1e3a8a;">
                    ${s.roll}
                  </td>
                  <td style="font-weight: 600;">
                    ${s.name}
                    ${s.reg_no ? `<div style="font-size: 0.75rem; color: #94a3b8; font-weight: 400;">Reg: ${s.reg_no}</div>` : ''}
                  </td>
                  <td style="font-size: 0.85rem; color: #334155;">
                    ${s.institute || 'Unknown'}
                  </td>
                  <td>
                    <span class="badge ${streamClass}">${s.stream || 'General'}</span>
                  </td>
                  <td style="text-align: center; font-weight: 700; font-size: 1rem; color: ${isPass ? '#059669' : '#94a3b8'};">
                    ${isPass ? gpa.toFixed(2) : '-'}
                  </td>
                  <td style="text-align: center;">
                    ${statusBadge}
                  </td>
                  <td style="text-align: center;">
                    <button class="filter-pill-btn" style="padding: 0.25rem 0.65rem; font-size: 0.8rem; background: #eff6ff; color: #1e3a8a; border-color: #bfdbfe;">
                      View Card &rarr;
                    </button>
                  </td>
                </tr>
              `;
            }).join('')}
          </tbody>
        </table>
      </div>

      <!-- Pagination Bar -->
      ${totalPages > 1 ? `
        <div class="pagination-wrapper">
          <div style="font-size: 0.85rem; color: #64748b;">
            Page ${this.currentPage} of ${totalPages}
          </div>
          <div class="flex gap-1">
            <button id="page-prev-btn" class="pagination-btn" ${this.currentPage <= 1 ? 'disabled' : ''}>&larr; Previous</button>
            <button id="page-next-btn" class="pagination-btn" ${this.currentPage >= totalPages ? 'disabled' : ''}>Next &rarr;</button>
          </div>
        </div>
      ` : ''}
    `;

    this._bindEvents(pageItems);
  }

  _bindEvents(pageItems) {
    // Page size dropdown
    const sizeSelect = document.getElementById('table-page-size');
    if (sizeSelect) {
      sizeSelect.addEventListener('change', (e) => {
        this.pageSize = Number(e.target.value);
        this.currentPage = 1;
        this.render();
      });
    }

    // Prev / Next pagination
    const prevBtn = document.getElementById('page-prev-btn');
    if (prevBtn) {
      prevBtn.addEventListener('click', () => {
        if (this.currentPage > 1) {
          this.currentPage--;
          this.render();
          this.container.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      });
    }

    const nextBtn = document.getElementById('page-next-btn');
    if (nextBtn) {
      nextBtn.addEventListener('click', () => {
        const totalPages = Math.ceil(this.students.length / this.pageSize);
        if (this.currentPage < totalPages) {
          this.currentPage++;
          this.render();
          this.container.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      });
    }

    // Row clicks
    const rows = this.container.querySelectorAll('[data-student-roll]');
    rows.forEach(row => {
      row.addEventListener('click', () => {
        const roll = row.getAttribute('data-student-roll');
        const s = pageItems.find(item => String(item.roll) === String(roll));
        if (s && this.onStudentClick) {
          this.onStudentClick(s);
        }
      });
    });
  }
}
