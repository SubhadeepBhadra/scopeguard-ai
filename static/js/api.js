/**
 * ScopeGuard AI - Centralized HTTP Client
 */
const API = {
  token: localStorage.getItem('sg_token') || null,

  setToken(token) {
    this.token = token;
    if (token) {
      localStorage.setItem('sg_token', token);
    } else {
      localStorage.removeItem('sg_token');
    }
  },

  async request(endpoint, options = {}) {
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    try {
      const res = await fetch(endpoint, {
        ...options,
        headers
      });

      if (res.status === 401 && !endpoint.includes('/login') && !endpoint.includes('/demo-login')) {
        // Auto-switch to demo if session expired or unauthenticated
        console.warn('Session expired, auto-refreshing demo session...');
        await this.demoLogin('director');
        return this.request(endpoint, options);
      }

      if (!res.ok) {
        let errorData;
        try {
          errorData = await res.json();
        } catch {
          errorData = { message: res.statusText || 'Request failed' };
        }
        const message = errorData.detail || errorData.message || 'Operation failed';
        throw new Error(message);
      }

      return await res.json();
    } catch (err) {
      console.error(`[API Error] ${endpoint}:`, err);
      throw err;
    }
  },

  // Auth Endpoints
  async getMe() {
    return this.request('/api/auth/me');
  },

  async login(email, password) {
    const res = await this.request('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    });
    this.setToken(res.token);
    return res;
  },

  async demoLogin(role = 'director') {
    const res = await this.request('/api/auth/demo-login', {
      method: 'POST',
      body: JSON.stringify({ role })
    });
    this.setToken(res.token);
    return res;
  },

  async updateProfile(data) {
    return this.request('/api/auth/profile', {
      method: 'PUT',
      body: JSON.stringify(data)
    });
  },

  async logout() {
    await this.request('/api/auth/logout', { method: 'POST' }).catch(() => {});
    this.setToken(null);
  },

  // Projects Endpoints
  async getProjects() {
    return this.request('/api/projects');
  },

  async createProject(data) {
    return this.request('/api/projects', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },

  // Scope Analysis Endpoints
  async analyzeScope(data) {
    return this.request('/api/scope/analyze', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },

  async getChangeOrders(projectId = null, statusFilter = null) {
    let url = '/api/scope/change-orders';
    const params = new URLSearchParams();
    if (projectId) params.append('project_id', projectId);
    if (statusFilter) params.append('status_filter', statusFilter);
    const queryString = params.toString();
    if (queryString) url += `?${queryString}`;
    return this.request(url);
  },

  async getChangeOrder(id) {
    return this.request(`/api/scope/change-orders/${id}`);
  },

  async updateChangeOrderStatus(id, status) {
    return this.request(`/api/scope/change-orders/${id}/status`, {
      method: 'PATCH',
      body: JSON.stringify({ status })
    });
  },

  // Billing Endpoints
  async getPlans() {
    return this.request('/api/billing/plans');
  },

  async getBillingUsage() {
    return this.request('/api/billing/usage');
  },

  async getInvoices() {
    return this.request('/api/billing/invoices');
  },

  async subscribe(planTier, paymentMethod = 'Visa ending in 4242') {
    return this.request('/api/billing/subscribe', {
      method: 'POST',
      body: JSON.stringify({ plan_tier: planTier, payment_method: paymentMethod })
    });
  },

  // Analytics Endpoints
  async getAnalyticsOverview() {
    return this.request('/api/analytics/overview');
  }
};
