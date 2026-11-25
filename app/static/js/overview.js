/* Sales Overview page: KPIs and charts are filled from /api/overview. */
(() => {
  const { colors, palette } = Dashboard;
  const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  const monthLabel = ym => { const [y, m] = ym.split('-'); return `${MONTHS[Number(m) - 1]} ${y}`; };

  const STATUS_CLASS = { Delivered: 'ok', Returned: 'warn', Cancelled: 'bad', 'In Transit': 'info' };

  function renderStatus(items) {
    const root = document.getElementById('orderStatusSummary');
    root.innerHTML = '';
    items.forEach(item => {
      const div = document.createElement('div');
      div.className = `status-item ${STATUS_CLASS[item.status] || ''}`;
      const name = document.createElement('span'); name.textContent = item.status;
      const count = document.createElement('strong'); count.textContent = Dashboard.number(item.orders);
      div.append(name, count);
      root.appendChild(div);
    });
  }

  async function load() {
    try {
      const data = await Dashboard.getJSON(`/api/overview?${Dashboard.getParams()}`);
      const k = data.kpis;
      Dashboard.setText('revenueKpi', Dashboard.compactCurrency(k.revenue));
      Dashboard.setText('ordersKpi', Dashboard.number(k.orders));
      Dashboard.setText('customersKpi', Dashboard.number(k.customers));
      Dashboard.setText('aovKpi', Dashboard.currency(k.average_order_value));
      Dashboard.setText('unitsKpi', Dashboard.number(k.units_sold));

      // Line chart with a soft pink gradient fill
      const ctx = document.getElementById('revenueChart').getContext('2d');
      const gradient = ctx.createLinearGradient(0, 0, 0, 300);
      gradient.addColorStop(0, 'rgba(255,63,108,.28)');
      gradient.addColorStop(1, 'rgba(255,144,90,0)');
      Dashboard.draw('revenueChart', {
        type: 'line',
        data: {
          labels: data.monthly_revenue.map(x => monthLabel(x.month)),
          datasets: [{
            label: 'Revenue', data: data.monthly_revenue.map(x => x.revenue),
            borderColor: colors.pink, backgroundColor: gradient, fill: true,
            tension: .35, borderWidth: 3, pointRadius: 3, pointBackgroundColor: '#fff',
            pointBorderColor: colors.pink, pointBorderWidth: 2
          }]
        },
        options: Dashboard.chartOptions({ currencyAxis: true })
      });

      Dashboard.draw('categoryChart', {
        type: 'doughnut',
        data: {
          labels: data.category_revenue.map(x => x.label),
          datasets: [{ data: data.category_revenue.map(x => x.revenue), backgroundColor: palette, borderColor: '#fff', borderWidth: 3 }]
        },
        options: {
          responsive: true, maintainAspectRatio: false, cutout: '62%',
          plugins: {
            legend: { position: 'bottom', labels: { usePointStyle: true, padding: 16 } },
            tooltip: { callbacks: { label: c => `${c.label}: ${Dashboard.currency(c.raw)}` } }
          }
        }
      });

      Dashboard.setText('geoSubtitle', `Top 5 ${data.geography_label === 'City' ? 'cities' : 'states'} by delivered revenue`);
      Dashboard.draw('geographyChart', {
        type: 'bar',
        data: {
          labels: data.top_geography.map(x => x.label),
          datasets: [{ label: 'Revenue', data: data.top_geography.map(x => x.revenue), backgroundColor: colors.pink, borderRadius: 8, barThickness: 22 }]
        },
        options: Dashboard.chartOptions({ horizontal: true, currencyAxis: true })
      });

      renderStatus(data.order_status);
      Dashboard.setStatus('Data updated');
    } catch (error) { Dashboard.showError(error); }
  }

  Dashboard.setupFilters(load).catch(Dashboard.showError);
})();