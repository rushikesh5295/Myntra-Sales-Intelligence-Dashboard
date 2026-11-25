/* Shared helpers for all dashboard pages: API calls, filters, formatting, chart theme. */
(() => {
  // Myntra brand palette (taken from the logo)
  const colors = {
    pink: '#FF3F6C', orange: '#FF905A', magenta: '#F51CB0',
    maroon: '#A0242F', red: '#F15412', ink: '#282C3F', grey: '#94969F'
  };
  const palette = [colors.pink, colors.orange, colors.magenta, colors.maroon, colors.red];

  const currency = value => new Intl.NumberFormat('en-IN', {
    style: 'currency', currency: 'INR', maximumFractionDigits: 0
  }).format(Number(value || 0));
  const number = value => new Intl.NumberFormat('en-IN').format(Number(value || 0));
  const compactCurrency = value => {
    const n = Number(value || 0);
    if (n >= 10000000) return `₹${(n / 10000000).toFixed(2)} Cr`;
    if (n >= 100000) return `₹${(n / 100000).toFixed(2)} L`;
    return currency(n);
  };

  async function getJSON(url) {
    const response = await fetch(url);
    if (!response.ok) {
      const detail = await response.json().catch(() => ({}));
      throw new Error(detail.message || `Request failed (${response.status})`);
    }
    return response.json();
  }

  function getParams() {
    const params = new URLSearchParams();
    ['state', 'category', 'brand'].forEach(key => {
      const value = document.getElementById(`${key}Filter`)?.value || 'All';
      if (value !== 'All') params.set(key, value);
    });
    const start = document.getElementById('startDateFilter')?.value;
    const end = document.getElementById('endDateFilter')?.value;
    if (start) params.set('start_date', start);
    if (end) params.set('end_date', end);
    return params;
  }

  function populateSelect(id, values, defaultLabel) {
    const select = document.getElementById(id);
    if (!select) return;
    select.innerHTML = '';
    const all = document.createElement('option');
    all.value = 'All'; all.textContent = defaultLabel; select.appendChild(all);
    values.forEach(value => {
      const option = document.createElement('option');
      option.value = value; option.textContent = value; select.appendChild(option);
    });
  }

  function setStatus(text) {
    const status = document.getElementById('filterStatus');
    if (status) status.textContent = text;
  }

  /* Loads the filter options from the API, restores saved filters and wires the buttons. */
  async function setupFilters(onApply) {
    const filterData = await getJSON('/api/filters');
    populateSelect('stateFilter', filterData.states, 'All States');
    populateSelect('categoryFilter', filterData.categories, 'All Categories');
    populateSelect('brandFilter', filterData.brands, 'All Brands');

    const start = document.getElementById('startDateFilter');
    const end = document.getElementById('endDateFilter');
    [start, end].forEach(el => {
      if (!el) return;
      if (filterData.date_range.min_date) el.min = filterData.date_range.min_date;
      if (filterData.date_range.max_date) el.max = filterData.date_range.max_date;
    });

    // Keep the same filters while moving between the three pages.
    try {
      const saved = JSON.parse(localStorage.getItem('myntraDashboardFilters') || '{}');
      ['state', 'category', 'brand'].forEach(key => {
        const el = document.getElementById(`${key}Filter`);
        if (el && saved[key] && [...el.options].some(o => o.value === saved[key])) el.value = saved[key];
      });
      if (start && saved.start_date) start.value = saved.start_date;
      if (end && saved.end_date) end.value = saved.end_date;
    } catch (_) { /* ignore unavailable or malformed local storage */ }

    const apply = () => {
      const selected = Object.fromEntries(getParams().entries());
      try { localStorage.setItem('myntraDashboardFilters', JSON.stringify(selected)); } catch (_) {}
      setStatus('Updating…');
      onApply();
    };

    document.getElementById('applyFilters')?.addEventListener('click', () => {
      if (start?.value && end?.value && start.value > end.value) {
        setStatus('“From” date must be before “To” date');
        return;
      }
      apply();
    });
    document.getElementById('resetFilters')?.addEventListener('click', () => {
      ['state', 'category', 'brand'].forEach(key => {
        const el = document.getElementById(`${key}Filter`); if (el) el.value = 'All';
      });
      if (start) start.value = '';
      if (end) end.value = '';
      try { localStorage.removeItem('myntraDashboardFilters'); } catch (_) {}
      apply();
    });
    apply();
  }

  /* Chart.js options shared by every chart. */
  function chartOptions({ horizontal = false, currencyAxis = false, legend = false } = {}) {
    const axis = currencyAxis
      ? { ticks: { callback: value => compactCurrency(value) }, grid: { color: '#F1F2F4' }, border: { display: false } }
      : { ticks: { precision: 0 }, grid: { color: '#F1F2F4' }, border: { display: false } };
    return {
      responsive: true,
      maintainAspectRatio: false,
      indexAxis: horizontal ? 'y' : 'x',
      plugins: {
        legend: { display: legend, position: 'bottom', labels: { usePointStyle: true, padding: 18 } },
        tooltip: {
          backgroundColor: colors.ink, padding: 10, cornerRadius: 8,
          callbacks: { label: c => `${c.dataset.label || c.label}: ${currencyAxis ? currency(c.raw) : number(c.raw)}` }
        }
      },
      scales: horizontal
        ? { x: axis, y: { grid: { display: false }, border: { display: false } } }
        : { x: { grid: { display: false }, border: { display: false } }, y: axis }
    };
  }

  const charts = {};
  function draw(id, config) {
    if (charts[id]) charts[id].destroy();
    const canvas = document.getElementById(id);
    if (canvas) charts[id] = new Chart(canvas, config);
  }
  function setText(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = value;
  }

  function showError(error) {
    const el = document.getElementById('pageError');
    if (el) el.textContent = `Unable to load dashboard data: ${error.message}`;
    setStatus('Could not load data');
    console.error(error);
  }

  if (window.Chart) {
    Chart.defaults.font.family = "'Inter', 'Segoe UI', sans-serif";
    Chart.defaults.color = '#696B79';
  }

  window.Dashboard = {
    colors, palette, getJSON, getParams, setupFilters, setStatus,
    currency, number, compactCurrency, chartOptions, draw, setText, showError
  };
})();
