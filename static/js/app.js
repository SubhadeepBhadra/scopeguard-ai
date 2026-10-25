/**
 * ScopeGuard AI - Main Application Controller
 */
const App = {
  currentUser: null,
  currentView: 'dashboard',
  projects: [],
  changeOrders: [],

  async init() {
    this.bindNavigation();
    this.bindModals();
    this.bindSettings();
    this.bindDemoSwitcher();

    // Check auth or initialize demo session
    try {
      this.currentUser = await API.getMe();
    } catch {
      const demoRes = await API.demoLogin('director');
      this.currentUser = demoRes.user;
    }

    this.updateUserUI(this.currentUser);
    await this.refreshAllData();

    // Initialize submodules
    Analyzer.init();
    Analytics.init();
    Billing.init();

    // Handle hash route or default
    const hash = window.location.hash.replace('#', '') || 'dashboard';
    this.navigate(hash);
  },

  bindNavigation() {
    document.querySelectorAll('.nav-link-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const view = e.currentTarget.getAttribute('data-view');
        this.navigate(view);
      });
    });

    // Quick Trigger buttons (e.g. "+ New Analysis")
    document.querySelectorAll('[data-action="new-analysis"]').forEach(btn => {
      btn.addEventListener('click', () => {
        this.navigate('analyzer');
        const reqEl = document.getElementById('analyzer-request');
        if (reqEl) reqEl.focus();
      });
    });

    // Hash change listener
    window.addEventListener('hashchange', () => {
      const hash = window.location.hash.replace('#', '');
      if (hash && hash !== this.currentView) {
        this.navigate(hash);
      }
    });
  },

  navigate(viewName) {
    this.currentView = viewName;
    window.location.hash = viewName;

    // Update Nav buttons
    document.querySelectorAll('.nav-link-btn').forEach(btn => {
      btn.classList.toggle('active', btn.getAttribute('data-view') === viewName);
    });

    // Show corresponding section
    document.querySelectorAll('.view-section').forEach(sec => {
      sec.classList.remove('active');
    });

    const activeSec = document.getElementById(`view-${viewName}`);
    if (activeSec) {
      activeSec.classList.add('active');
    }

    // Trigger view-specific refreshes
    if (viewName === 'analytics') {
      Analytics.refresh();
    } else if (viewName === 'billing') {
      Billing.refresh();
    } else if (viewName === 'dashboard') {
      this.renderDashboard();
    } else if (viewName === 'change-orders') {
      this.renderChangeOrdersTable();
    }
  },

  bindDemoSwitcher() {
    const roleSelect = document.getElementById('demo-role-selector');
    if (roleSelect) {
      roleSelect.addEventListener('change', async (e) => {
        const role = e.target.value;
        this.showToast(`Switching to ${role === 'director' ? 'Agency Director (Elena)' : 'Solo Freelancer (Marcus)'}...`, 'info');
        try {
          const res = await API.demoLogin(role);
          this.currentUser = res.user;
          this.updateUserUI(this.currentUser);
          await this.refreshAllData();
          Analytics.refresh();
          Billing.refresh();
          this.showToast('Workspace switched successfully!', 'success');
        } catch (err) {
          this.showToast(err.message, 'error');
        }
      });
    }
  },

  updateUserUI(user) {
    if (!user) return;
    const nameEl = document.getElementById('header-user-name');
    const roleEl = document.getElementById('header-user-role');
    const avatarEl = document.getElementById('header-user-avatar');

    if (nameEl) nameEl.textContent = user.full_name;
    if (roleEl) roleEl.textContent = `${user.company_name} (${user.role})`;
    if (avatarEl) {
      const initials = user.full_name.split(' ').map(n => n[0]).join('').substring(0, 2);
      avatarEl.textContent = initials;
    }

    // Update settings form fields
    const setCompany = document.getElementById('setting-company-name');
    const setRate = document.getElementById('setting-hourly-rate');
    const setCurrency = document.getElementById('setting-currency');

    if (setCompany) setCompany.value = user.company_name || '';
    if (setRate) setRate.value = user.default_hourly_rate || 125;
    if (setCurrency) setCurrency.value = user.currency || 'USD';
  },

  async refreshAllData() {
    try {
      const [projects, changeOrders] = await Promise.all([
        API.getProjects(),
        API.getChangeOrders()
      ]);

      this.projects = projects;
      this.changeOrders = changeOrders;

      this.populateProjectDropdowns();
      this.renderDashboard();
      this.renderChangeOrdersTable();
      Billing.refresh();
    } catch (err) {
      console.error('Error refreshing app data:', err);
    }
  },

  populateProjectDropdowns() {
    const select = document.getElementById('analyzer-project-select');
    if (!select) return;

    select.innerHTML = `
      <option value="">-- Choose Existing Client SOW or Enter Below --</option>
      ${this.projects.map(p => `
        <option value="${p.id}">${p.project_name} (${p.client_name})</option>
      `).join('')}
    `;

    select.addEventListener('change', (e) => {
      const pId = parseInt(e.target.value);
      const proj = this.projects.find(p => p.id === pId);
      const sowPreview = document.getElementById('analyzer-sow-preview');
      const rateInput = document.getElementById('analyzer-hourly-rate');

      if (proj) {
        if (sowPreview) sowPreview.value = proj.baseline_sow;
        if (rateInput) rateInput.value = proj.hourly_rate;
      } else {
        if (sowPreview) sowPreview.value = '';
      }
    });
  },

  renderDashboard() {
    // 1. Calculate KPIs
    const approvedCOs = this.changeOrders.filter(co => ['approved', 'invoiced'].includes(co.status));
    const totalRecovered = approvedCOs.reduce((sum, co) => sum + co.billable_amount, 0);
    const totalCreepHours = this.changeOrders.reduce((sum, co) => sum + co.estimated_hours, 0);
    const approvalRate = this.changeOrders.length ? Math.round((approvedCOs.length / this.changeOrders.length) * 100) : 0;

    // Update Stat Cards
    const elRev = document.getElementById('dash-stat-revenue');
    if (elRev) elRev.textContent = `$${totalRecovered.toLocaleString('en-US', { minimumFractionDigits: 2 })}`;

    const elHours = document.getElementById('dash-stat-hours');
    if (elHours) elHours.textContent = `${totalCreepHours} hrs`;

    const elApp = document.getElementById('dash-stat-approval');
    if (elApp) elApp.textContent = `${approvalRate}%`;

    const elRoi = document.getElementById('dash-stat-roi');
    if (elRoi) elRoi.textContent = `80,450x`;

    // 2. Render Active Projects Grid
    const projContainer = document.getElementById('dash-projects-list');
    if (projContainer) {
      if (!this.projects.length) {
        projContainer.innerHTML = `<p style="color:#64748b;">No client projects yet. Create your first project to track scope creep.</p>`;
      } else {
        projContainer.innerHTML = this.projects.map(p => `
          <div class="card" style="margin-bottom: 1rem; padding: 1.1rem;">
            <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:0.5rem;">
              <div>
                <h4 style="font-size:1.05rem; margin-bottom:0.2rem;">${p.project_name}</h4>
                <span style="font-size:0.8rem; color:#94a3b8;">${p.client_name} • $${p.hourly_rate}/hr</span>
              </div>
              <span class="badge" style="background:rgba(99,102,241,0.15); color:#a5b4fc;">
                ${p.change_orders_count || 0} Scope Changes
              </span>
            </div>
            <p style="font-size:0.82rem; color:#cbd5e1; margin-bottom:0.85rem; line-height:1.4;">
              ${p.baseline_sow.substring(0, 120)}...
            </p>
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <span style="font-size:0.8rem; color:#10b981; font-weight:700;">
                +$${(p.recovered_revenue || 0).toLocaleString()} Recovered
              </span>
              <button class="btn btn-secondary btn-sm" onclick="App.quickAnalyze(${p.id})">
                + Analyze Request
              </button>
            </div>
          </div>
        `).join('');
      }
    }

    // 3. Render Recent Change Orders
    const recentContainer = document.getElementById('dash-recent-cos');
    if (recentContainer) {
      const recent = this.changeOrders.slice(0, 5);
      if (!recent.length) {
        recentContainer.innerHTML = `<p style="color:#64748b;">No change orders recorded yet.</p>`;
      } else {
        recentContainer.innerHTML = recent.map(co => `
          <div style="display:flex; align-items:center; justify-content:space-between; padding:0.85rem 0; border-bottom:1px solid rgba(255,255,255,0.06);">
            <div>
              <div style="font-weight:600; font-size:0.9rem; margin-bottom:0.2rem;">${co.title}</div>
              <div style="font-size:0.75rem; color:#94a3b8;">${co.client_name} • ${co.estimated_hours} hrs • ${new Date(co.created_at).toLocaleDateString()}</div>
            </div>
            <div style="text-align:right;">
              <div style="font-weight:700; color:#34d399; font-size:0.95rem;">+$${co.billable_amount.toLocaleString()}</div>
              <span class="badge badge-status ${co.status}">${co.status}</span>
            </div>
          </div>
        `).join('');
      }
    }
  },

  quickAnalyze(projectId) {
    this.navigate('analyzer');
    const select = document.getElementById('analyzer-project-select');
    if (select) {
      select.value = projectId;
      select.dispatchEvent(new Event('change'));
    }
    const reqInput = document.getElementById('analyzer-request');
    if (reqInput) reqInput.focus();
  },

  renderChangeOrdersTable() {
    const tbody = document.getElementById('change-orders-table-body');
    if (!tbody) return;

    if (!this.changeOrders.length) {
      tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; color:#64748b; padding:2.5rem;">No change orders generated yet. Use the Scope Analyzer to detect creep!</td></tr>`;
      return;
    }

    tbody.innerHTML = this.changeOrders.map(co => `
      <tr>
        <td><strong>#CO-${co.id}</strong></td>
        <td>
          <div style="font-weight:600;">${co.title}</div>
          <div style="font-size:0.75rem; color:#94a3b8;">${co.project_name} (${co.client_name})</div>
        </td>
        <td>
          <span class="badge badge-${co.risk_level.toLowerCase()}">${co.risk_level} (${co.risk_score})</span>
        </td>
        <td>${co.estimated_hours} hrs</td>
        <td><strong style="color:#34d399;">$${co.billable_amount.toLocaleString()}</strong></td>
        <td>
          <select class="form-control" style="padding:0.25rem 0.5rem; font-size:0.75rem; width:auto;" onchange="App.handleStatusChange(${co.id}, this.value)">
            <option value="draft" ${co.status === 'draft' ? 'selected' : ''}>Draft</option>
            <option value="sent" ${co.status === 'sent' ? 'selected' : ''}>Sent</option>
            <option value="approved" ${co.status === 'approved' ? 'selected' : ''}>Approved</option>
            <option value="invoiced" ${co.status === 'invoiced' ? 'selected' : ''}>Invoiced</option>
            <option value="rejected" ${co.status === 'rejected' ? 'selected' : ''}>Rejected</option>
          </select>
        </td>
        <td>
          <button class="btn btn-secondary btn-sm" onclick="App.viewChangeOrderModal(${co.id})">
            View Addendum
          </button>
        </td>
      </tr>
    `).join('');
  },

  async handleStatusChange(coId, newStatus) {
    try {
      await API.updateChangeOrderStatus(coId, newStatus);
      this.showToast(`Change order status updated to ${newStatus}.`, 'success');
      await this.refreshAllData();
      Analytics.refresh();
    } catch (err) {
      this.showToast(err.message, 'error');
    }
  },

  async viewChangeOrderModal(coId) {
    try {
      const co = await API.getChangeOrder(coId);
      const modal = document.getElementById('change-order-detail-modal');
      const titleEl = document.getElementById('modal-co-title');
      const contentEl = document.getElementById('modal-co-markdown');

      if (titleEl) titleEl.textContent = co.title;
      if (contentEl) {
        contentEl.innerHTML = Analyzer.renderMarkdownHtml(co.agreement_markdown);
      }

      if (modal) modal.classList.add('active');
    } catch (err) {
      this.showToast(err.message, 'error');
    }
  },

  bindModals() {
    // New Project Modal
    const openProjBtn = document.getElementById('btn-open-new-project');
    const projModal = document.getElementById('new-project-modal');
    const closeProjBtn = document.getElementById('btn-close-new-project');

    if (openProjBtn) {
      openProjBtn.addEventListener('click', () => {
        if (projModal) projModal.classList.add('active');
      });
    }

    if (closeProjBtn) {
      closeProjBtn.addEventListener('click', () => {
        if (projModal) projModal.classList.remove('active');
      });
    }

    const projForm = document.getElementById('new-project-form');
    if (projForm) {
      projForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const pName = document.getElementById('new-proj-name').value.trim();
        const cName = document.getElementById('new-proj-client').value.trim();
        const sow = document.getElementById('new-proj-sow').value.trim();
        const rate = parseFloat(document.getElementById('new-proj-rate').value) || 150.0;

        if (!pName || !cName || !sow) {
          this.showToast('Please fill in all project fields.', 'error');
          return;
        }

        try {
          await API.createProject({
            project_name: pName,
            client_name: cName,
            baseline_sow: sow,
            hourly_rate: rate
          });

          this.showToast(`Project "${pName}" created successfully!`, 'success');
          projModal.classList.remove('active');
          projForm.reset();
          await this.refreshAllData();
        } catch (err) {
          this.showToast(err.message, 'error');
        }
      });
    }

    // Detail modal close
    const closeCoModal = document.getElementById('btn-close-co-modal');
    if (closeCoModal) {
      closeCoModal.addEventListener('click', () => {
        const modal = document.getElementById('change-order-detail-modal');
        if (modal) modal.classList.remove('active');
      });
    }
  },

  bindSettings() {
    const form = document.getElementById('settings-form');
    if (form) {
      form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const company = document.getElementById('setting-company-name').value.trim();
        const rate = parseFloat(document.getElementById('setting-hourly-rate').value) || 125.0;
        const currency = document.getElementById('setting-currency').value;
        const groq = document.getElementById('setting-groq-key').value.trim();
        const openai = document.getElementById('setting-openai-key').value.trim();

        try {
          await API.updateProfile({
            company_name: company,
            default_hourly_rate: rate,
            currency: currency,
            custom_groq_key: groq || null,
            custom_openai_key: openai || null
          });

          this.showToast('Settings & custom API keys saved!', 'success');
          this.currentUser = await API.getMe();
          this.updateUserUI(this.currentUser);
        } catch (err) {
          this.showToast(err.message, 'error');
        }
      });
    }
  },

  showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
      <span>${type === 'success' ? '✓' : (type === 'error' ? '⚠' : 'ℹ')}</span>
      <div>${message}</div>
    `;

    container.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transition = 'opacity 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, 4000);
  }
};

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  App.init();
});
