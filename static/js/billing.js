/**
 * ScopeGuard AI - Billing, Subscription Plans & Stripe Simulator
 */
const Billing = {
  selectedPlan: null,

  init() {
    this.bindEvents();
    this.refresh();
  },

  bindEvents() {
    // Plan Select Buttons
    document.querySelectorAll('.btn-select-plan').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const planTier = e.currentTarget.getAttribute('data-plan');
        this.openCheckoutModal(planTier);
      });
    });

    // Close checkout modal
    const closeBtn = document.getElementById('btn-close-checkout');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => {
        this.closeCheckoutModal();
      });
    }

    // Checkout form submit
    const checkoutForm = document.getElementById('stripe-checkout-form');
    if (checkoutForm) {
      checkoutForm.addEventListener('submit', (e) => {
        e.preventDefault();
        this.processCheckout();
      });
    }
  },

  async refresh() {
    try {
      const [usage, invoices] = await Promise.all([
        API.getBillingUsage(),
        API.getInvoices()
      ]);

      this.renderUsage(usage);
      this.renderInvoices(invoices);
      this.updateActivePlanBadges(usage.plan_tier);
    } catch (err) {
      console.error('Failed to load billing details:', err);
    }
  },

  renderUsage(usage) {
    if (!usage) return;

    // Header quota pill
    const pillTokens = document.getElementById('header-quota-tokens');
    if (pillTokens) {
      pillTokens.textContent = `${(usage.monthly_tokens_used / 1000).toFixed(1)}k / ${(usage.monthly_token_quota / 1000).toFixed(0)}k tokens`;
    }

    const pillBar = document.getElementById('header-quota-fill');
    if (pillBar) {
      pillBar.style.width = `${usage.usage_percentage}%`;
    }

    // Billing View Quota Box
    const boxPlan = document.getElementById('billing-plan-name');
    if (boxPlan) boxPlan.textContent = usage.plan_name;

    const boxPercent = document.getElementById('billing-usage-percent');
    if (boxPercent) boxPercent.textContent = `${usage.usage_percentage}%`;

    const boxUsed = document.getElementById('billing-tokens-used');
    if (boxUsed) boxUsed.textContent = `${usage.monthly_tokens_used.toLocaleString()} tokens`;

    const boxRemaining = document.getElementById('billing-tokens-remaining');
    if (boxRemaining) boxRemaining.textContent = `${usage.monthly_tokens_remaining.toLocaleString()} tokens`;

    const boxCost = document.getElementById('billing-alltime-cost');
    if (boxCost) boxCost.textContent = `$${usage.all_time_cost_usd.toFixed(4)} USD`;
  },

  updateActivePlanBadges(activeTier) {
    document.querySelectorAll('.pricing-card').forEach(card => {
      const tier = card.getAttribute('data-tier');
      const actionBtn = card.querySelector('.btn-select-plan');
      if (tier === activeTier) {
        card.classList.add('featured');
        if (actionBtn) {
          actionBtn.textContent = 'Current Active Plan';
          actionBtn.disabled = true;
          actionBtn.className = 'btn btn-secondary btn-select-plan';
        }
      } else {
        card.classList.remove('featured');
        if (actionBtn) {
          actionBtn.textContent = 'Upgrade Plan';
          actionBtn.disabled = false;
          actionBtn.className = 'btn btn-primary btn-select-plan';
        }
      }
    });
  },

  renderInvoices(invoices) {
    const tbody = document.getElementById('billing-invoices-body');
    if (!tbody) return;

    if (!invoices || !invoices.length) {
      tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; color:#64748b; padding:2rem;">No invoices generated yet.</td></tr>`;
      return;
    }

    tbody.innerHTML = invoices.map(inv => `
      <tr>
        <td><strong>${inv.invoice_number}</strong></td>
        <td>${new Date(inv.created_at).toLocaleDateString()}</td>
        <td><span style="text-transform: capitalize;">${inv.plan_tier} Plan</span></td>
        <td><strong>$${inv.amount.toFixed(2)} ${inv.currency}</strong></td>
        <td><span class="badge badge-status approved">PAID</span></td>
      </tr>
    `).join('');
  },

  openCheckoutModal(planTier) {
    this.selectedPlan = planTier;
    const modal = document.getElementById('checkout-modal');
    const titleEl = document.getElementById('checkout-modal-plan-title');
    const amountEl = document.getElementById('checkout-modal-amount');

    const prices = { starter: '$29.00 / month', pro: '$79.00 / month', agency: '$199.00 / month' };
    const names = { starter: 'Freelance Starter', pro: 'Studio Pro', agency: 'Agency Scale' };

    if (titleEl) titleEl.textContent = `Subscribe to ${names[planTier] || planTier}`;
    if (amountEl) amountEl.textContent = prices[planTier] || '$79.00';

    if (modal) modal.classList.add('active');
  },

  closeCheckoutModal() {
    const modal = document.getElementById('checkout-modal');
    if (modal) modal.classList.remove('active');
  },

  async processCheckout() {
    if (!this.selectedPlan) return;

    const payBtn = document.getElementById('btn-submit-payment');
    payBtn.disabled = true;
    payBtn.innerHTML = `<span class="spinner"></span> Processing with Stripe...`;

    try {
      const res = await API.subscribe(this.selectedPlan);
      App.showToast(`Success! Upgraded to ${res.plan.name}. Quota refreshed!`, 'success');
      this.closeCheckoutModal();
      this.refresh();
      App.refreshAllData();
    } catch (err) {
      App.showToast(err.message, 'error');
    } finally {
      payBtn.disabled = false;
      payBtn.innerHTML = `Confirm & Authorize Payment`;
    }
  }
};
