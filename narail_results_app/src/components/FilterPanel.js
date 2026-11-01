// src/components/FilterPanel.js

export class FilterPanel {
  constructor(containerId, options = {}) {
    this.container = document.getElementById(containerId);
    this.colleges = options.colleges || [];
    this.onChange = options.onChange || null;

    this.state = {
      searchTerm: '',
      upazila: 'ALL',
      collegeEiin: 'ALL',
      stream: 'ALL',
      status: 'ALL',
      minGpa: 0.0,
      maxGpa: 5.0,
      sortBy: 'gpa_desc',
    };
  }

  setColleges(colleges) {
    this.colleges = colleges;
    this.render();
  }

  setFilter(updates) {
    Object.assign(this.state, updates);
    this.render();
    if (this.onChange) this.onChange(this.state);
  }

  reset() {
    this.state = {
      searchTerm: '',
      upazila: 'ALL',
      collegeEiin: 'ALL',
      stream: 'ALL',
      status: 'ALL',
      minGpa: 0.0,
      maxGpa: 5.0,
      sortBy: 'gpa_desc',
    };
    this.render();
    if (this.onChange) this.onChange(this.state);
  }

  render() {
    if (!this.container) return;

    // Filter colleges by upazila if selected
    const displayColleges = this.state.upazila === 'ALL'
      ? this.colleges
      : this.colleges.filter(c => c.upazila === this.state.upazila);

    this.container.innerHTML = `
      <div class="filter-card">
        <div class="flex justify-between items-center" style="margin-bottom: 1rem; border-bottom: 1px solid #f1f5f9; padding-bottom: 0.5rem;">
          <div style="font-weight: 700; font-size: 1.05rem; color: #1e3a8a; display: flex; align-items: center; gap: 0.4rem;">
            <span>⚡ Filters & Search</span>
          </div>
          <button id="reset-filters-btn" style="background: none; border: none; color: #ef4444; font-size: 0.85rem; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 0.25rem;">
            ✕ Reset All
          </button>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          <!-- 1. Search Within Roster -->
          <div>
            <div class="filter-group-title">Search Roster</div>
            <input 
              type="text" 
              id="filter-search-input" 
              class="filter-select" 
              placeholder="Roll, Reg, or Name..." 
              value="${this.state.searchTerm}"
            />
          </div>

          <!-- 2. Upazila -->
          <div>
            <div class="filter-group-title">Upazila</div>
            <select id="filter-upazila-select" class="filter-select">
              <option value="ALL" ${this.state.upazila === 'ALL' ? 'selected' : ''}>All Upazilas (3)</option>
              <option value="Narail Sadar" ${this.state.upazila === 'Narail Sadar' ? 'selected' : ''}>Narail Sadar (12 colleges)</option>
              <option value="Lohagara" ${this.state.upazila === 'Lohagara' ? 'selected' : ''}>Lohagara (7 colleges)</option>
              <option value="Kalia" ${this.state.upazila === 'Kalia' ? 'selected' : ''}>Kalia (5 colleges)</option>
            </select>
          </div>

          <!-- 3. College -->
          <div>
            <div class="filter-group-title">College (EIIN)</div>
            <select id="filter-college-select" class="filter-select">
              <option value="ALL" ${this.state.collegeEiin === 'ALL' ? 'selected' : ''}>All Colleges (${displayColleges.length})</option>
              ${displayColleges.map(c => `
                <option value="${c.eiin}" ${String(this.state.collegeEiin) === String(c.eiin) ? 'selected' : ''}>
                  ${c.name || c.college_name} (${c.eiin})
                </option>
              `).join('')}
            </select>
          </div>

          <!-- 4. Academic Stream -->
          <div>
            <div class="filter-group-title">Academic Stream</div>
            <div class="flex flex-wrap gap-1">
              ${['ALL', 'Science', 'Humanities', 'Business Studies'].map(s => `
                <button 
                  class="filter-pill-btn ${this.state.stream === s ? 'active' : ''}" 
                  data-stream="${s}">
                  ${s === 'ALL' ? 'All' : s}
                </button>
              `).join('')}
            </div>
          </div>

          <!-- 5. Result Status -->
          <div>
            <div class="filter-group-title">Result Status</div>
            <div class="flex flex-wrap gap-1">
              ${['ALL', 'PASSED', 'FAILED', 'ABSENT'].map(st => `
                <button 
                  class="filter-pill-btn ${this.state.status === st ? 'active' : ''}" 
                  data-status="${st}">
                  ${st === 'ALL' ? 'All' : st}
                </button>
              `).join('')}
            </div>
          </div>

          <!-- 6. GPA Presets -->
          <div class="lg:col-span-2">
            <div class="filter-group-title">GPA Bracket Presets</div>
            <div class="flex flex-wrap gap-1">
              <button class="filter-pill-btn ${this.state.minGpa === 0.0 && this.state.maxGpa === 5.0 ? 'active' : ''}" data-gpa-preset="all">All</button>
              <button class="filter-pill-btn ${this.state.minGpa === 5.0 && this.state.maxGpa === 5.0 ? 'active' : ''}" data-gpa-preset="5.00">GPA 5.00</button>
              <button class="filter-pill-btn ${this.state.minGpa === 4.0 && this.state.maxGpa === 4.99 ? 'active' : ''}" data-gpa-preset="4.00-4.99">4.00 - 4.99</button>
              <button class="filter-pill-btn ${this.state.minGpa === 3.5 && this.state.maxGpa === 3.99 ? 'active' : ''}" data-gpa-preset="3.50-3.99">3.50 - 3.99</button>
              <button class="filter-pill-btn ${this.state.minGpa === 3.0 && this.state.maxGpa === 3.49 ? 'active' : ''}" data-gpa-preset="3.00-3.49">3.00 - 3.49</button>
              <button class="filter-pill-btn ${this.state.minGpa === 0.0 && this.state.maxGpa === 2.99 ? 'active' : ''}" data-gpa-preset="below-3">Below 3.00</button>
            </div>
          </div>

          <!-- 7. Sort Order -->
          <div>
            <div class="filter-group-title">Sort By</div>
            <select id="filter-sort-select" class="filter-select">
              <option value="gpa_desc" ${this.state.sortBy === 'gpa_desc' ? 'selected' : ''}>GPA (Highest First)</option>
              <option value="gpa_asc" ${this.state.sortBy === 'gpa_asc' ? 'selected' : ''}>GPA (Lowest First)</option>
              <option value="roll_asc" ${this.state.sortBy === 'roll_asc' ? 'selected' : ''}>Roll Number (Ascending)</option>
              <option value="roll_desc" ${this.state.sortBy === 'roll_desc' ? 'selected' : ''}>Roll Number (Descending)</option>
              <option value="name_asc" ${this.state.sortBy === 'name_asc' ? 'selected' : ''}>Student Name (A-Z)</option>
            </select>
          </div>
        </div>

        <!-- Range slider fine tuning -->
        <div style="margin-top: 1rem; padding-top: 0.75rem; border-top: 1px dashed var(--border); display: flex; align-items: center; gap: 1rem; flex-wrap: wrap;">
          <span style="font-size: 0.85rem; font-weight: 600; color: #64748b;">Min GPA Threshold:</span>
          <input 
            type="range" 
            id="gpa-range-slider" 
            class="range-slider-input" 
            min="0" 
            max="5" 
            step="0.1" 
            value="${this.state.minGpa}"
            style="max-width: 250px;"
          />
          <span id="gpa-slider-value" style="font-weight: 700; color: #1e3a8a; font-size: 0.95rem;">${Number(this.state.minGpa).toFixed(1)} &ndash; ${Number(this.state.maxGpa).toFixed(1)}</span>
        </div>
      </div>
    `;

    this._bindEvents();
  }

  _bindEvents() {
    // Search input with debounce
    const searchInput = document.getElementById('filter-search-input');
    if (searchInput) {
      let timeout;
      searchInput.addEventListener('input', (e) => {
        clearTimeout(timeout);
        timeout = setTimeout(() => {
          this.state.searchTerm = e.target.value;
          if (this.onChange) this.onChange(this.state);
        }, 200);
      });
    }

    // Upazila select
    const upazilaSelect = document.getElementById('filter-upazila-select');
    if (upazilaSelect) {
      upazilaSelect.addEventListener('change', (e) => {
        this.state.upazila = e.target.value;
        this.state.collegeEiin = 'ALL'; // Reset college when upazila changes
        this.render();
        if (this.onChange) this.onChange(this.state);
      });
    }

    // College select
    const collegeSelect = document.getElementById('filter-college-select');
    if (collegeSelect) {
      collegeSelect.addEventListener('change', (e) => {
        this.state.collegeEiin = e.target.value;
        if (this.onChange) this.onChange(this.state);
      });
    }

    // Stream buttons
    const streamBtns = this.container.querySelectorAll('[data-stream]');
    streamBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        this.state.stream = btn.getAttribute('data-stream');
        this.render();
        if (this.onChange) this.onChange(this.state);
      });
    });

    // Status buttons
    const statusBtns = this.container.querySelectorAll('[data-status]');
    statusBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        this.state.status = btn.getAttribute('data-status');
        this.render();
        if (this.onChange) this.onChange(this.state);
      });
    });

    // GPA presets
    const gpaBtns = this.container.querySelectorAll('[data-gpa-preset]');
    gpaBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        const preset = btn.getAttribute('data-gpa-preset');
        if (preset === 'all') {
          this.state.minGpa = 0.0;
          this.state.maxGpa = 5.0;
        } else if (preset === '5.00') {
          this.state.minGpa = 5.0;
          this.state.maxGpa = 5.0;
        } else if (preset === '4.00-4.99') {
          this.state.minGpa = 4.0;
          this.state.maxGpa = 4.99;
        } else if (preset === '3.50-3.99') {
          this.state.minGpa = 3.5;
          this.state.maxGpa = 3.99;
        } else if (preset === '3.00-3.49') {
          this.state.minGpa = 3.0;
          this.state.maxGpa = 3.49;
        } else if (preset === 'below-3') {
          this.state.minGpa = 0.0;
          this.state.maxGpa = 2.99;
        }
        this.render();
        if (this.onChange) this.onChange(this.state);
      });
    });

    // Slider
    const slider = document.getElementById('gpa-range-slider');
    if (slider) {
      slider.addEventListener('input', (e) => {
        this.state.minGpa = Number(e.target.value);
        this.state.maxGpa = 5.0;
        document.getElementById('gpa-slider-value').innerText = `${this.state.minGpa.toFixed(1)} – 5.0`;
        if (this.onChange) this.onChange(this.state);
      });
    }

    // Sort order
    const sortSelect = document.getElementById('filter-sort-select');
    if (sortSelect) {
      sortSelect.addEventListener('change', (e) => {
        this.state.sortBy = e.target.value;
        if (this.onChange) this.onChange(this.state);
      });
    }

    // Reset button
    const resetBtn = document.getElementById('reset-filters-btn');
    if (resetBtn) {
      resetBtn.addEventListener('click', () => {
        this.reset();
      });
    }
  }
}
