/**
 * ScopeGuard AI - FinOps & SaaS Revenue Analytics
 */
const Analytics = {
  charts: {},

  init() {
    this.refresh();
  },

  async refresh() {
    try {
      const data = await API.getAnalyticsOverview();
      this.renderSummary(data.summary);
      this.renderCharts(data);
    } catch (err) {
      console.error('Failed to load analytics data:', err);
    }
  },

  renderSummary(summary) {
    if (!summary) return;

    const elRec = document.getElementById('analytics-kpi-recovered');
    if (elRec) elRec.textContent = `$${summary.recovered_revenue.toLocaleString('en-US', { minimumFractionDigits: 2 })}`;

    const elHours = document.getElementById('analytics-kpi-hours');
    if (elHours) elHours.textContent = `${summary.total_creep_hours} hrs`;

    const elRoi = document.getElementById('analytics-kpi-roi');
    if (elRoi) elRoi.textContent = `${summary.roi_multiplier.toLocaleString()}x`;

    const elRate = document.getElementById('analytics-kpi-approval');
    if (elRate) elRate.textContent = `${summary.approval_rate_percent}%`;
  },

  renderCharts(data) {
    if (typeof Chart === 'undefined') return;

    // Destroy previous charts if re-rendering
    if (this.charts.revenue) this.charts.revenue.destroy();
    if (this.charts.categories) this.charts.categories.destroy();
    if (this.charts.clients) this.charts.clients.destroy();

    const trend = data.monthly_trend || [];
    const labels = trend.map(t => t.month);
    const revenues = trend.map(t => t.recovered_revenue);

    // Chart 1: Revenue Timeline (Recovered Scope Dollars)
    const ctxRevenue = document.getElementById('chart-revenue-trend')?.getContext('2d');
    if (ctxRevenue) {
      this.charts.revenue = new Chart(ctxRevenue, {
        type: 'line',
        data: {
          labels: labels,
          datasets: [{
            label: 'Recovered Revenue ($)',
            data: revenues,
            borderColor: '#6366f1',
            backgroundColor: 'rgba(99, 102, 241, 0.15)',
            fill: true,
            tension: 0.4,
            borderWidth: 3,
            pointBackgroundColor: '#8b5cf6',
            pointRadius: 4
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
            tooltip: {
              backgroundColor: '#0f172a',
              titleColor: '#fff',
              bodyColor: '#a5b4fc',
              borderColor: 'rgba(255,255,255,0.1)',
              borderWidth: 1
            }
          },
          scales: {
            x: {
              grid: { color: 'rgba(255, 255, 255, 0.05)' },
              ticks: { color: '#94a3b8' }
            },
            y: {
              grid: { color: 'rgba(255, 255, 255, 0.05)' },
              ticks: {
                color: '#94a3b8',
                callback: (val) => `$${val.toLocaleString()}`
              }
            }
          }
        }
      });
    }

    // Chart 2: Categories Doughnut
    const ctxCat = document.getElementById('chart-categories')?.getContext('2d');
    const catDist = data.category_distribution || {};
    const catLabels = Object.keys(catDist);
    const catValues = Object.values(catDist);

    if (ctxCat) {
      this.charts.categories = new Chart(ctxCat, {
        type: 'doughnut',
        data: {
          labels: catLabels.length ? catLabels : ['Scope Expansion', 'Architectural Pivot', 'Minor Revision'],
          datasets: [{
            data: catValues.length ? catValues : [4, 2, 1],
            backgroundColor: ['#6366f1', '#f43f5e', '#10b981'],
            borderColor: '#0f1627',
            borderWidth: 3
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'bottom',
              labels: { color: '#94a3b8', font: { size: 12 } }
            }
          }
        }
      });
    }

    // Chart 3: Top Clients Bar
    const ctxClients = document.getElementById('chart-clients')?.getContext('2d');
    const topClients = data.top_clients || [];
    if (ctxClients && topClients.length) {
      this.charts.clients = new Chart(ctxClients, {
        type: 'bar',
        data: {
          labels: topClients.map(c => c.client.length > 18 ? c.client.substring(0, 18) + '...' : c.client),
          datasets: [{
            label: 'Creep Hours',
            data: topClients.map(c => c.hours),
            backgroundColor: '#06b6d4',
            borderRadius: 6
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          indexAxis: 'y',
          plugins: {
            legend: { display: false }
          },
          scales: {
            x: {
              grid: { color: 'rgba(255, 255, 255, 0.05)' },
              ticks: { color: '#94a3b8' }
            },
            y: {
              grid: { display: false },
              ticks: { color: '#94a3b8' }
            }
          }
        }
      });
    }
  }
};
