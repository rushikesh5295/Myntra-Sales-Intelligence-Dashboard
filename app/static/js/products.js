/* Product Analysis page: KPIs and charts are filled from /api/products. */
(() => {
  const { colors, palette } = Dashboard;

  async function load() {
    try {
      const data = await Dashboard.getJSON(`/api/products?${Dashboard.getParams()}`);
      const k = data.kpis;
      Dashboard.setText('totalProductsKpi', Dashboard.number(k.total_products));
      Dashboard.setText('productRevenueKpi', Dashboard.compactCurrency(k.product_revenue));
      Dashboard.setText('productUnitsKpi', Dashboard.number(k.units_sold));
      Dashboard.setText('averagePriceKpi', Dashboard.currency(k.average_selling_price));

      Dashboard.draw('categoryRevenueChart', {
        type: 'bar',
        data: {
          labels: data.category_revenue.map(x => x.label),
          datasets: [{ label: 'Revenue', data: data.category_revenue.map(x => x.revenue), backgroundColor: palette, borderRadius: 8 }]
        },
        options: Dashboard.chartOptions({ currencyAxis: true })
      });

      Dashboard.draw('brandRevenueChart', {
        type: 'bar',
        data: {
          labels: data.top_brands.map(x => x.label),
          datasets: [{ label: 'Revenue', data: data.top_brands.map(x => x.revenue), backgroundColor: colors.pink, borderRadius: 8, barThickness: 22 }]
        },
        options: Dashboard.chartOptions({ horizontal: true, currencyAxis: true })
      });

      Dashboard.draw('topProductsChart', {
        type: 'bar',
        data: {
          labels: data.top_products.map(x => x.label),
          datasets: [{ label: 'Units sold', data: data.top_products.map(x => x.units_sold), backgroundColor: colors.orange, borderRadius: 8, barThickness: 22 }]
        },
        options: Dashboard.chartOptions({ horizontal: true })
      });

      Dashboard.setStatus('Data updated');
    } catch (error) { Dashboard.showError(error); }
  }

  Dashboard.setupFilters(load).catch(Dashboard.showError);
})();
