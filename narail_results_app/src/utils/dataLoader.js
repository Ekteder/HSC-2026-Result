// src/utils/dataLoader.js
/**
 * In-memory client-side data engine for Narail HSC 2026 Examination Results.
 * Efficiently loads and caches manifest, roll lookup index, and full student dataset.
 */

class DataLoader {
  constructor() {
    this.manifest = null;
    this.rollLookup = null;
    this.allStudents = null;
    this.rollMap = new Map();
    this.nameIndex = [];
    this.collegeMap = new Map();
    this.isLoaded = false;
    this.loadProgressCallback = null;
  }

  onProgress(cb) {
    this.loadProgressCallback = cb;
  }

  _notifyProgress(msg, percent) {
    if (this.loadProgressCallback) {
      this.loadProgressCallback(msg, percent);
    }
  }

  async _fetchJsonWithFallbacks(paths) {
    for (const p of paths) {
      try {
        const res = await fetch(p);
        if (res.ok) {
          return await res.json();
        }
      } catch (err) {
        // try next fallback
      }
    }
    throw new Error(`Failed to load JSON from any path: ${paths.join(', ')}`);
  }

  async init() {
    if (this.isLoaded) return;

    this._notifyProgress('Loading summary manifest...', 20);
    // 1. Load Tier 1 Manifest (<30 KB)
    try {
      this.manifest = await this._fetchJsonWithFallbacks([
        './data/manifest.json',
        '/data/manifest.json',
        'public/data/manifest.json',
        '../data/manifest.json',
      ]);
      if (this.manifest && this.manifest.colleges) {
        for (const col of this.manifest.colleges) {
          this.collegeMap.set(Number(col.eiin), col);
        }
      }
    } catch (e) {
      console.warn('Manifest load warning:', e);
    }

    this._notifyProgress('Loading fast search index...', 50);
    // 2. Load Tier 2 Roll Lookup (~1.2 MB)
    try {
      this.rollLookup = await this._fetchJsonWithFallbacks([
        './data/roll_lookup.json',
        '/data/roll_lookup.json',
        'public/data/roll_lookup.json',
        '../data/roll_lookup.json',
      ]);
    } catch (e) {
      console.warn('Roll lookup load warning:', e);
    }

    this._notifyProgress('Loading comprehensive student dataset...', 80);
    // 3. Load Tier 3 Consolidated Dataset (~6.2 MB)
    try {
      this.allStudents = await this._fetchJsonWithFallbacks([
        './data/narail_all_students.json',
        './data/all_students.json',
        '/data/narail_all_students.json',
        'public/data/narail_all_students.json',
        '../data/narail_all_students.json',
      ]);

      if (Array.isArray(this.allStudents)) {
        for (const s of this.allStudents) {
          const rollStr = String(s.roll).trim();
          this.rollMap.set(rollStr, s);
          this.nameIndex.push({
            roll: rollStr,
            name: (s.name || '').toLowerCase(),
            regno: String(s.reg_no || s.regno || '').toLowerCase(),
            college: s.institute || '',
            eiin: s.eiin,
            stream: s.stream || '',
            gpa: s.gpa || 0.0,
            status: s.status || '',
          });
        }
      }
    } catch (e) {
      console.error('All students dataset failed to load:', e);
    }

    this.isLoaded = true;
    this._notifyProgress('Ready', 100);
  }

  getStudentByRoll(roll) {
    if (!roll) return null;
    const r = String(roll).trim();
    if (this.rollMap.has(r)) {
      return this.rollMap.get(r);
    }
    if (this.rollLookup && this.rollLookup[r]) {
      return this.rollLookup[r];
    }
    return null;
  }

  searchCandidates(query, limit = 8) {
    if (!query) return [];
    const q = String(query).trim().toLowerCase();
    if (!q) return [];

    // Exact or prefix match on roll
    const results = [];
    const seenRolls = new Set();

    // 1. Direct roll prefix match
    for (const [rollStr, s] of this.rollMap.entries()) {
      if (rollStr.includes(q)) {
        results.push(s);
        seenRolls.add(rollStr);
        if (results.length >= limit) return results;
      }
    }

    // 2. Name or Reg match
    for (const item of this.nameIndex) {
      if (!seenRolls.has(item.roll)) {
        if (item.name.includes(q) || (item.regno && item.regno.includes(q))) {
          const s = this.rollMap.get(item.roll);
          if (s) {
            results.push(s);
            seenRolls.add(item.roll);
            if (results.length >= limit) return results;
          }
        }
      }
    }

    return results;
  }

  filterStudents(criteria = {}) {
    if (!this.allStudents) return [];

    const {
      searchTerm = '',
      collegeEiin = 'ALL',
      upazila = 'ALL',
      stream = 'ALL',
      status = 'ALL',
      minGpa = 0.0,
      maxGpa = 5.0,
      sortBy = 'gpa_desc',
    } = criteria;

    const term = searchTerm.trim().toLowerCase();
    const eiinNum = collegeEiin !== 'ALL' ? Number(collegeEiin) : null;
    const cleanStream = stream !== 'ALL' ? stream.toUpperCase() : null;
    const cleanStatus = status !== 'ALL' ? status.toUpperCase() : null;

    let filtered = this.allStudents.filter((s) => {
      // 1. Search Term (roll, reg, name)
      if (term) {
        const rollMatch = String(s.roll || '').includes(term);
        const nameMatch = (s.name || '').toLowerCase().includes(term);
        const regMatch = String(s.reg_no || s.regno || '').toLowerCase().includes(term);
        if (!rollMatch && !nameMatch && !regMatch) {
          return false;
        }
      }

      // 2. College EIIN
      if (eiinNum !== null) {
        const sEiin = Number(s.eiin || 0);
        if (sEiin !== eiinNum) {
          return false;
        }
      }

      // 3. Upazila
      if (upazila !== 'ALL') {
        const col = this.collegeMap.get(Number(s.eiin));
        const colUpazila = (col && col.upazila) || s.upazila || '';
        if (colUpazila !== upazila) {
          return false;
        }
      }

      // 4. Academic Stream
      if (cleanStream) {
        const sStream = (s.stream || s.group || '').toUpperCase();
        if (sStream !== cleanStream) {
          return false;
        }
      }

      // 5. Status
      if (cleanStatus) {
        const sStatus = (s.status || '').toUpperCase();
        if (cleanStatus === 'PASSED') {
          if (!sStatus.includes('PASS') && Number(s.gpa || 0) <= 0) return false;
        } else if (cleanStatus === 'FAILED') {
          if (!sStatus.includes('FAIL') && sStatus !== 'F1' && sStatus !== 'F2') return false;
        } else if (cleanStatus === 'ABSENT') {
          if (!sStatus.includes('ABS')) return false;
        }
      }

      // 6. GPA Range
      const gpa = Number(s.gpa || 0.0);
      if (gpa < minGpa || gpa > maxGpa) {
        return false;
      }

      return true;
    });

    // Sorting
    filtered.sort((a, b) => {
      if (sortBy === 'gpa_desc') {
        return (Number(b.gpa) || 0) - (Number(a.gpa) || 0);
      }
      if (sortBy === 'gpa_asc') {
        return (Number(a.gpa) || 0) - (Number(b.gpa) || 0);
      }
      if (sortBy === 'roll_asc') {
        return Number(a.roll) - Number(b.roll);
      }
      if (sortBy === 'roll_desc') {
        return Number(b.roll) - Number(a.roll);
      }
      if (sortBy === 'name_asc') {
        return (a.name || '').localeCompare(b.name || '');
      }
      return 0;
    });

    return filtered;
  }
}

export const dataLoader = new DataLoader();
