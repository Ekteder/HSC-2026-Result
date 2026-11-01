// src/components/SearchHero.js

export class SearchHero {
  constructor(containerId, options = {}) {
    this.container = document.getElementById(containerId);
    this.dataLoader = options.dataLoader;
    this.onSelectStudent = options.onSelectStudent || null;
    this.selectedIndex = -1;
    this.currentSuggestions = [];
  }

  render() {
    if (!this.container) return;

    this.container.innerHTML = `
      <div class="search-container">
        <div class="search-box-wrapper">
          <input 
            type="search" 
            id="hero-search-input" 
            class="search-input-field" 
            placeholder="Enter 6-digit Roll No., Registration No., or Student Name..."
            autocomplete="off"
            inputmode="numeric"
          />
          <button id="hero-search-submit" class="search-submit-btn">
            <span>Search</span>
            <span>&rarr;</span>
          </button>
        </div>
        <div id="hero-autocomplete" class="autocomplete-dropdown"></div>
      </div>
    `;

    this._bindEvents();
  }

  _bindEvents() {
    const input = document.getElementById('hero-search-input');
    const dropdown = document.getElementById('hero-autocomplete');
    const submitBtn = document.getElementById('hero-search-submit');

    if (!input || !dropdown || !submitBtn) return;

    let debounceTimer;

    input.addEventListener('input', (e) => {
      clearTimeout(debounceTimer);
      const val = e.target.value.trim();

      if (val.length < 2) {
        dropdown.classList.remove('show');
        dropdown.innerHTML = '';
        this.currentSuggestions = [];
        this.selectedIndex = -1;
        return;
      }

      debounceTimer = setTimeout(() => {
        this.currentSuggestions = this.dataLoader.searchCandidates(val, 8);
        this.selectedIndex = -1;
        this._renderDropdown(this.currentSuggestions, dropdown);
      }, 150);
    });

    input.addEventListener('keydown', (e) => {
      if (!dropdown.classList.contains('show') || this.currentSuggestions.length === 0) {
        if (e.key === 'Enter') {
          this._handleDirectSearch(input.value.trim());
        }
        return;
      }

      if (e.key === 'ArrowDown') {
        e.preventDefault();
        this.selectedIndex = (this.selectedIndex + 1) % this.currentSuggestions.length;
        this._updateHighlight(dropdown);
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        this.selectedIndex = (this.selectedIndex - 1 + this.currentSuggestions.length) % this.currentSuggestions.length;
        this._updateHighlight(dropdown);
      } else if (e.key === 'Enter') {
        e.preventDefault();
        if (this.selectedIndex >= 0 && this.selectedIndex < this.currentSuggestions.length) {
          this._selectStudent(this.currentSuggestions[this.selectedIndex], input, dropdown);
        } else {
          this._handleDirectSearch(input.value.trim());
        }
      } else if (e.key === 'Escape') {
        dropdown.classList.remove('show');
      }
    });

    submitBtn.addEventListener('click', () => {
      this._handleDirectSearch(input.value.trim());
    });

    // Close on outside click
    document.addEventListener('click', (e) => {
      if (!this.container.contains(e.target)) {
        dropdown.classList.remove('show');
      }
    });
  }

  _renderDropdown(suggestions, dropdown) {
    if (suggestions.length === 0) {
      dropdown.innerHTML = `
        <div style="padding: 1rem; text-align: center; color: #64748b; font-size: 0.9rem;">
          No matching candidates found for this query.
        </div>
      `;
      dropdown.classList.add('show');
      return;
    }

    dropdown.innerHTML = suggestions.map((s, idx) => {
      const gpa = Number(s.gpa || 0);
      const isPass = (s.status || '').toUpperCase().includes('PASS') || gpa > 0;
      const isAbsent = (s.status || '').toUpperCase().includes('ABS');

      let badge = `<span class="badge badge-failed">${s.status || 'FAIL'}</span>`;
      if (isPass) {
        badge = gpa >= 5.0 
          ? `<span class="badge badge-gpa5">★ GPA 5.00</span>`
          : `<span class="badge badge-passed">GPA ${gpa.toFixed(2)}</span>`;
      } else if (isAbsent) {
        badge = `<span class="badge badge-absent">ABSENT</span>`;
      }

      return `
        <div class="autocomplete-item" data-index="${idx}">
          <div>
            <div style="font-weight: 700; color: #1e3a8a;">
              Roll: ${s.roll} &mdash; ${s.name}
            </div>
            <div style="font-size: 0.8rem; color: #64748b; margin-top: 2px;">
              ${s.institute || ''} &bull; <span style="font-weight: 500;">${s.stream || ''}</span>
            </div>
          </div>
          <div>
            ${badge}
          </div>
        </div>
      `;
    }).join('');

    dropdown.classList.add('show');

    // Click on suggestion
    const items = dropdown.querySelectorAll('.autocomplete-item');
    items.forEach(item => {
      item.addEventListener('click', () => {
        const idx = Number(item.getAttribute('data-index'));
        const s = suggestions[idx];
        const input = document.getElementById('hero-search-input');
        this._selectStudent(s, input, dropdown);
      });
    });
  }

  _updateHighlight(dropdown) {
    const items = dropdown.querySelectorAll('.autocomplete-item');
    items.forEach((item, idx) => {
      if (idx === this.selectedIndex) {
        item.classList.add('selected');
        item.scrollIntoView({ block: 'nearest' });
      } else {
        item.classList.remove('selected');
      }
    });
  }

  _selectStudent(student, input, dropdown) {
    if (!student) return;
    if (input) input.value = student.roll;
    if (dropdown) dropdown.classList.remove('show');
    if (this.onSelectStudent) {
      this.onSelectStudent(student);
    }
  }

  _handleDirectSearch(term) {
    if (!term) return;
    const student = this.dataLoader.getStudentByRoll(term);
    if (student) {
      this._selectStudent(student, document.getElementById('hero-search-input'), document.getElementById('hero-autocomplete'));
    } else {
      // Try search by name
      const results = this.dataLoader.searchCandidates(term, 1);
      if (results.length > 0) {
        this._selectStudent(results[0], document.getElementById('hero-search-input'), document.getElementById('hero-autocomplete'));
      } else {
        alert(`No student found with Roll / Registration "${term}". Please verify the 6-digit roll number.`);
      }
    }
  }
}
