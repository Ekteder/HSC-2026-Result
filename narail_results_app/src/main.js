// src/main.js
import './styles/main.css';
import { dataLoader } from './utils/dataLoader.js';
import { StudentModal } from './components/StudentModal.js';
import { SearchHero } from './components/SearchHero.js';
import { AnalyticsDashboard } from './components/AnalyticsDashboard.js';
import { FilterPanel } from './components/FilterPanel.js';
import { StudentTable } from './components/StudentTable.js';
import { CollegeMatrix } from './components/CollegeMatrix.js';

class App {
  constructor() {
    this.currentView = 'analytics';
    this.studentModal = null;
    this.searchHero = null;
    this.analyticsDashboard = null;
    this.filterPanel = null;
    this.studentTable = null;
    this.collegeMatrix = null;
  }

  async init() {
    // 1. Loading state
    const loadingStatus = document.getElementById('app-loading-indicator');
    if (loadingStatus) {
      dataLoader.onProgress((msg, pct) => {
        loadingStatus.innerText = `${msg} (${pct}%)`;
      });
    }

    try {
      await dataLoader.init();
    } catch (e) {
      console.error('App init error:', e);
    }

    if (loadingStatus) {
      loadingStatus.style.display = 'none';
    }

    // 2. Initialize Modal
    this.studentModal = new StudentModal();

    // 3. Initialize Search Hero
    this.searchHero = new SearchHero('search-hero-container', {
      dataLoader: dataLoader,
      onSelectStudent: (student) => {
        this.studentModal.open(student);
      }
    });
    this.searchHero.render();

    // 4. Initialize Analytics Dashboard
    this.analyticsDashboard = new AnalyticsDashboard('analytics-view', {
      onCollegeClick: (college) => {
        this.filterByCollege(college.eiin);
      }
    });

    // 5. Initialize Filter Panel & Student Table
    this.filterPanel = new FilterPanel('filter-panel-container', {
      colleges: (dataLoader.manifest && dataLoader.manifest.colleges) || [],
      onChange: (criteria) => {
        const filtered = dataLoader.filterStudents(criteria);
        this.studentTable.setData(filtered);
      }
    });

    this.studentTable = new StudentTable('student-table-container', {
      onStudentClick: (student) => {
        this.studentModal.open(student);
      }
    });

    // 6. Initialize College Matrix
    this.collegeMatrix = new CollegeMatrix('colleges-view', {
      onCollegeClick: (college) => {
        this.filterByCollege(college.eiin);
      }
    });

    // Initial render of components
    if (dataLoader.manifest) {
      this.analyticsDashboard.render(dataLoader.manifest);
      this.filterPanel.setColleges(dataLoader.manifest.colleges || []);
      this.collegeMatrix.setColleges(dataLoader.manifest.colleges || []);
    }

    const initialStudents = dataLoader.filterStudents(this.filterPanel.state);
    this.studentTable.setData(initialStudents);

    // 7. Navigation Tabs
    this._bindNavigationTabs();

    // 8. Hash routing check
    this._handleInitialRoute();
  }

  filterByCollege(eiin) {
    this.switchView('roster');
    this.filterPanel.setFilter({ collegeEiin: String(eiin), upazila: 'ALL' });
    document.getElementById('student-roster-section').scrollIntoView({ behavior: 'smooth' });
  }

  switchView(viewName) {
    this.currentView = viewName;
    const views = ['analytics', 'roster', 'colleges'];
    
    views.forEach(v => {
      const el = document.getElementById(`${v}-view`);
      if (el) {
        el.style.display = (v === viewName) ? 'block' : 'none';
      }
      const tabBtn = document.querySelector(`[data-tab="${v}"]`);
      if (tabBtn) {
        if (v === viewName) tabBtn.classList.add('active');
        else tabBtn.classList.remove('active');
      }
    });

    if (viewName === 'analytics' && dataLoader.manifest) {
      this.analyticsDashboard.render(dataLoader.manifest);
    }
  }

  _bindNavigationTabs() {
    const tabs = document.querySelectorAll('[data-tab]');
    tabs.forEach(tab => {
      tab.addEventListener('click', () => {
        const targetView = tab.getAttribute('data-tab');
        this.switchView(targetView);
      });
    });
  }

  _handleInitialRoute() {
    const hash = window.location.hash;
    if (hash.startsWith('#roll=')) {
      const roll = hash.replace('#roll=', '').trim();
      const student = dataLoader.getStudentByRoll(roll);
      if (student) {
        this.studentModal.open(student);
      }
    } else if (hash === '#roster') {
      this.switchView('roster');
    } else if (hash === '#colleges') {
      this.switchView('colleges');
    } else {
      this.switchView('analytics');
    }

    window.addEventListener('hashchange', () => {
      const newHash = window.location.hash;
      if (newHash.startsWith('#roll=')) {
        const roll = newHash.replace('#roll=', '').trim();
        const student = dataLoader.getStudentByRoll(roll);
        if (student) this.studentModal.open(student);
      }
    });
  }
}

// Auto-boot on DOM ready
document.addEventListener('DOMContentLoaded', () => {
  const app = new App();
  app.init();
});
