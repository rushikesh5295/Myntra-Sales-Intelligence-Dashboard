/* Customer Behaviour page: KPIs and charts are filled from /api/customers. */
(() => {
  const { colors, palette } = Dashboard;

  const doughnut = (labels, values, colorList) => ({
    type: 'doughnut',
    data: { labels, datasets: [{ data: values, backgroundColor: colorList, borderColor: '#fff', borderWidth: 3 }] },
    options: { ...Dashboard.chartOptions({ legend: true }), cutout: '65%', scales: {} }
  });

  async function load() {
    try {
      const data = await Dashboard.getJSON(`/api/customers?${Dashboard.getParams()}`);
      const k = data.kpis;
      Dashboard.setText('totalCustomersKpi', Dashboard.number(k.total_customers));
      Dashboard.setText('newCustomersKpi', Dashboard.number(k.new_customers));
      Dashboard.setText('repeatCustomersKpi', Dashboard.number(k.repeat_customers));
      Dashboard.setText('averageSpendKpi', Dashboard.currency(k.average_customer_spend));

      Dashboard.draw('genderChart', doughnut(
        data.gender.map(x => x.label), data.gender.map(x => x.customers), palette));

      Dashboard.draw('frequencyChart', {
        type: 'bar',
        data: {
          labels: data.purchase_frequency.map(x => x.label),
          datasets: [{ label: 'Customers', data: data.purchase_frequency.map(x => x.customers), backgroundColor: colors.pink, borderRadius: 8 }]
        },
        options: Dashboard.chartOptions()
      });

      Dashboard.draw('segmentsChart', doughnut(
        data.segments.map(x => x.label), data.segments.map(x => x.customers),
        [colors.maroon, colors.orange, colors.pink]));

      Dashboard.setStatus('Data updated');
    } catch (error) { Dashboard.showError(error); }
  }

  Dashboard.setupFilters(load).catch(Dashboard.showError);
})();
