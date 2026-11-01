// src/components/StudentModal.js
/**
 * Student Result Card & Marksheet Modal Component.
 */

export class StudentModal {
  constructor() {
    this.modalEl = document.getElementById('student-modal');
    this.currentRoll = null;
    this._bindEvents();
  }

  _bindEvents() {
    if (!this.modalEl) return;
    
    // Backdrop click dismisses
    this.modalEl.addEventListener('click', (e) => {
      if (e.target === this.modalEl) {
        this.close();
      }
    });

    // Close button
    const closeBtn = this.modalEl.querySelector('.modal-close-btn');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => this.close());
    }

    // Escape key
    window.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && this.modalEl.classList.contains('show')) {
        this.close();
      }
    });

    // Share link button
    const shareBtn = document.getElementById('modal-share-btn');
    if (shareBtn) {
      shareBtn.addEventListener('click', () => {
        if (this.currentRoll) {
          const shareUrl = `${window.location.origin}${window.location.pathname}#roll=${this.currentRoll}`;
          navigator.clipboard.writeText(shareUrl).then(() => {
            shareBtn.innerText = '✓ Link Copied!';
            setTimeout(() => {
              shareBtn.innerText = '📋 Share Link';
            }, 2000);
          }).catch(() => {
            prompt('Copy link:', shareUrl);
          });
        }
      });
    }

    // Print button
    const printBtn = document.getElementById('modal-print-btn');
    if (printBtn) {
      printBtn.addEventListener('click', () => {
        window.print();
      });
    }
  }

  getGradeClass(grade) {
    if (!grade) return 'grade-X';
    const g = String(grade).toUpperCase().trim();
    if (g === 'A+') return 'grade-A-plus';
    if (g === 'A') return 'grade-A';
    if (g === 'A-') return 'grade-A-minus';
    if (g === 'B') return 'grade-B';
    if (g === 'C') return 'grade-C';
    if (g === 'D') return 'grade-D';
    if (g === 'F') return 'grade-F';
    return 'grade-X';
  }

  getGradePoint(grade) {
    if (!grade) return '0.00';
    const g = String(grade).toUpperCase().trim();
    if (g === 'A+') return '5.00';
    if (g === 'A') return '4.00';
    if (g === 'A-') return '3.50';
    if (g === 'B') return '3.00';
    if (g === 'C') return '2.00';
    if (g === 'D') return '1.00';
    return '0.00';
  }

  open(student) {
    if (!student || !this.modalEl) return;
    this.currentRoll = student.roll;

    // Update URL hash without reload
    window.history.replaceState(null, '', `#roll=${student.roll}`);

    // Populate modal fields
    document.getElementById('modal-student-name').innerText = student.name || 'N/A';
    document.getElementById('modal-institute-name').innerText = student.institute || 'Unknown Institution';
    document.getElementById('modal-roll').innerText = student.roll || 'N/A';
    document.getElementById('modal-reg').innerText = student.reg_no || student.regno || 'Not Available';
    document.getElementById('modal-stream').innerText = student.stream || 'General';
    document.getElementById('modal-session').innerText = student.session || '2024-25';
    document.getElementById('modal-type').innerText = student.type || student.candidate_type || 'REGULAR';
    document.getElementById('modal-center').innerText = student.center || 'N/A';
    document.getElementById('modal-father').innerText = student.father_name || 'N/A';
    document.getElementById('modal-mother').innerText = student.mother_name || 'N/A';

    // Status & GPA
    const statusPill = document.getElementById('modal-status-pill');
    const isPass = (student.status || '').toUpperCase().includes('PASS') || Number(student.gpa || 0) > 0;
    const isAbsent = (student.status || '').toUpperCase().includes('ABS');
    const isReported = (student.status || '').toUpperCase().includes('REP') || (student.status || '').toUpperCase().includes('EXPL');
    
    if (isPass) {
      const gpaVal = Number(student.gpa || 0).toFixed(2);
      statusPill.className = 'badge badge-passed';
      statusPill.innerHTML = `✓ PASSED &bull; GPA ${gpaVal}`;
    } else if (isAbsent) {
      statusPill.className = 'badge badge-absent';
      statusPill.innerHTML = `ABSENT`;
    } else if (isReported) {
      statusPill.className = 'badge badge-reported';
      statusPill.innerHTML = `REPORTED / WITHHELD`;
    } else {
      statusPill.className = 'badge badge-failed';
      statusPill.innerHTML = `✕ FAILED (${student.status || 'FAIL'})`;
    }

    // Populate Subjects Table
    const tbody = document.getElementById('modal-subjects-body');
    tbody.innerHTML = '';

    const subjects = student.subjects || [];
    if (Array.isArray(subjects) && subjects.length > 0) {
      subjects.forEach((sub, idx) => {
        const subName = sub.name || sub.subject || `Subject ${idx + 1}`;
        const subCode = sub.code || '';
        const grade = sub.grade || '-';
        const gp = this.getGradePoint(grade);
        const gradeClass = this.getGradeClass(grade);

        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td style="padding: 0.65rem 1rem; border-bottom: 1px solid #f1f5f9; font-weight: 500;">
            ${subName} ${subCode ? `<span style="font-size: 0.8rem; color: #64748b;">(${subCode})</span>` : ''}
          </td>
          <td style="padding: 0.65rem 1rem; border-bottom: 1px solid #f1f5f9; text-align: center;">
            <span class="grade-badge ${gradeClass}">${grade}</span>
          </td>
          <td style="padding: 0.65rem 1rem; border-bottom: 1px solid #f1f5f9; text-align: right; font-weight: 600; color: #334155;">
            ${gp}
          </td>
        `;
        tbody.appendChild(tr);
      });
    } else {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td colspan="3" style="text-align: center; padding: 1.5rem; color: #64748b;">
          ${isAbsent ? 'Candidate was absent in the examination. No subject marks recorded.' : 'No detailed subject breakdown available.'}
        </td>
      `;
      tbody.appendChild(tr);
    }

    this.modalEl.classList.add('show');
    document.body.style.overflow = 'hidden';
  }

  close() {
    if (!this.modalEl) return;
    this.modalEl.classList.remove('show');
    document.body.style.overflow = '';
    // Clear URL hash
    if (window.location.hash.startsWith('#roll=')) {
      window.history.replaceState(null, '', window.location.pathname);
    }
  }
}
