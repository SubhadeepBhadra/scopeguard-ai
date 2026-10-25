/**
 * ScopeGuard AI - Scope Studio & Change Order Generator
 */
const Analyzer = {
  currentResult: null,

  // Realistic sample presets for instant evaluation
  presets: [
    {
      label: '💳 Stripe & Crypto Payment',
      request: 'Hey Subhadeep! Can we quickly allow users to deposit funds directly via Stripe in USD and EUR? Should just take an afternoon right? Also let us know if Bitcoin deposits are easy to toggle.'
    },
    {
      label: '📹 WebRTC In-App Video Room',
      request: 'Our doctors want to conduct patient consultations directly inside the web browser via HIPAA encrypted video calling instead of external Zoom links. We need it live before next Friday!'
    },
    {
      label: '🎨 Dark Mode & Framer Overhaul',
      request: 'Could you re-skin the entire 5 dashboard screens with a custom dark mode, fluid glassmorphic cards, and silky spring micro-animations like Linear and Vercel? Want it to look stunning for our investor demo.'
    },
    {
      label: '🎁 VIP Loyalty Points Engine',
      request: 'We want our top shoppers to automatically earn 5% loyalty points on every purchase, unlock bronze/silver/gold tier badges, and apply points directly at checkout as instant discount vouchers.'
    },
    {
      label: '⚡ Urgent Mobile Push Alerts',
      request: 'Urgent request from our CEO: We need native mobile push notification triggers sent to iOS and Android whenever a doctor cancels an appointment or updates their prescription.'
    }
  ],

  init() {
    this.renderPresets();
    this.bindEvents();
  },

  renderPresets() {
    const container = document.getElementById('presets-container');
    if (!container) return;

    container.innerHTML = this.presets.map((p, idx) => `
      <button type="button" class="preset-chip" data-idx="${idx}">
        ${p.label}
      </button>
    `).join('');

    container.querySelectorAll('.preset-chip').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const idx = parseInt(e.currentTarget.getAttribute('data-idx'));
        const preset = this.presets[idx];
        const reqInput = document.getElementById('analyzer-request');
        if (reqInput) {
          reqInput.value = preset.request;
          reqInput.focus();
        }
      });
    });
  },

  bindEvents() {
    const form = document.getElementById('scope-analyzer-form');
    if (form) {
      form.addEventListener('submit', (e) => {
        e.preventDefault();
        this.runAnalysis();
      });
    }

    // Tone tabs switcher
    document.querySelectorAll('.tab-btn[data-tone]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const tone = e.currentTarget.getAttribute('data-tone');
        this.switchToneTab(tone);
      });
    });

    // Copy Response button
    const copyBtn = document.getElementById('btn-copy-response');
    if (copyBtn) {
      copyBtn.addEventListener('click', () => {
        const text = document.getElementById('response-preview-text')?.innerText;
        if (text) {
          navigator.clipboard.writeText(text);
          App.showToast('Diplomatic response copied to clipboard!', 'success');
        }
      });
    }

    // Copy Agreement button
    const copyAgreeBtn = document.getElementById('btn-copy-agreement');
    if (copyAgreeBtn) {
      copyAgreeBtn.addEventListener('click', () => {
        if (this.currentResult && this.currentResult.agreement_markdown) {
          navigator.clipboard.writeText(this.currentResult.agreement_markdown);
          App.showToast('Change order markdown copied to clipboard!', 'success');
        }
      });
    }

    // Download Markdown button
    const downloadBtn = document.getElementById('btn-download-md');
    if (downloadBtn) {
      downloadBtn.addEventListener('click', () => {
        if (!this.currentResult) return;
        const blob = new Blob([this.currentResult.agreement_markdown], { type: 'text/markdown' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `Change_Order_Addendum_${this.currentResult.change_order_id || 'Draft'}.md`;
        a.click();
        URL.revokeObjectURL(url);
        App.showToast('Change Order Markdown file downloaded.', 'info');
      });
    }

    // Print / PDF button
    const printBtn = document.getElementById('btn-print-agreement');
    if (printBtn) {
      printBtn.addEventListener('click', () => {
        window.print();
      });
    }

    // Approve button
    const approveBtn = document.getElementById('btn-approve-analysis');
    if (approveBtn) {
      approveBtn.addEventListener('click', async () => {
        if (!this.currentResult?.change_order_id) return;
        try {
          await API.updateChangeOrderStatus(this.currentResult.change_order_id, 'approved');
          App.showToast('Change Order marked as APPROVED! Revenue added to dashboard.', 'success');
          App.refreshAllData();
        } catch (err) {
          App.showToast(err.message, 'error');
        }
      });
    }
  },

  async runAnalysis() {
    const projectSelect = document.getElementById('analyzer-project-select');
    const reqInput = document.getElementById('analyzer-request');
    const rateInput = document.getElementById('analyzer-hourly-rate');
    const submitBtn = document.getElementById('btn-run-analysis');

    const clientRequest = reqInput?.value.trim();
    if (!clientRequest) {
      App.showToast('Please enter or select a client request to analyze.', 'error');
      return;
    }

    const projectId = projectSelect?.value ? parseInt(projectSelect.value) : null;
    const hourlyRate = rateInput?.value ? parseFloat(rateInput.value) : 150.0;

    // Show loading state
    submitBtn.disabled = true;
    submitBtn.innerHTML = `<span class="spinner"></span> Analyzing Scope Delta & Estimating Risk...`;

    try {
      const response = await API.analyzeScope({
        project_id: projectId,
        client_request_raw: clientRequest,
        hourly_rate: hourlyRate
      });

      this.currentResult = {
        change_order_id: response.change_order_id,
        ...response.analysis,
        finops: response.finops
      };

      this.renderResults(this.currentResult);
      App.showToast('Scope analysis completed successfully!', 'success');
      App.refreshAllData();

      // Scroll to results
      const resultsContainer = document.getElementById('analysis-results-section');
      if (resultsContainer) {
        resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    } catch (err) {
      App.showToast(err.message, 'error');
    } finally {
      submitBtn.disabled = false;
      submitBtn.innerHTML = `<span>⚡ Analyze Scope & Generate Addendum</span>`;
    }
  },

  renderResults(data) {
    const resultsContainer = document.getElementById('analysis-results-section');
    if (!resultsContainer) return;

    resultsContainer.style.display = 'block';

    // Populate KPIs
    document.getElementById('res-category').textContent = data.category;
    document.getElementById('res-category').className = `badge badge-${data.risk_level.toLowerCase()}`;

    document.getElementById('res-risk-score').textContent = `${data.risk_score}/100 (${data.risk_level} Risk)`;
    document.getElementById('res-hours').textContent = `${data.estimated_hours} hrs`;
    document.getElementById('res-amount').textContent = `$${data.billable_amount.toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
    document.getElementById('res-schedule').textContent = `+${data.delivery_days_impact} Business Days`;

    // FinOps Accounting Pill
    const finops = data.finops;
    if (finops) {
      document.getElementById('finops-tokens').textContent = `${finops.total_tokens.toLocaleString()} tokens`;
      document.getElementById('finops-cost').textContent = `$${finops.ai_cost_usd.toFixed(5)} USD`;
      document.getElementById('finops-model').textContent = finops.model_used;
    }

    // Delta explanation
    document.getElementById('res-delta-summary').textContent = data.scope_delta_summary;

    // Hours Breakdown Table
    const breakdown = data.analysis_details?.hours_breakdown || {};
    const tableBody = document.getElementById('hours-breakdown-body');
    if (tableBody) {
      tableBody.innerHTML = `
        <tr><td>Frontend UI & Interactions</td><td><strong>${breakdown.frontend || 0} hrs</strong></td></tr>
        <tr><td>Backend Architecture & APIs</td><td><strong>${breakdown.backend || 0} hrs</strong></td></tr>
        <tr><td>UI/UX Prototyping & Specs</td><td><strong>${breakdown.design || 0} hrs</strong></td></tr>
        <tr><td>Quality Assurance & Security Testing</td><td><strong>${breakdown.qa || 0} hrs</strong></td></tr>
        <tr><td>Project Management & Deployment</td><td><strong>${breakdown.pm || 0} hrs</strong></td></tr>
        <tr style="background: rgba(255,255,255,0.04); font-weight:700;">
          <td>Total Estimated Scope Delta</td>
          <td style="color:#34d399;">${breakdown.total || data.estimated_hours} hrs ($${data.billable_amount.toLocaleString()})</td>
        </tr>
      `;
    }

    // Set Default Tone (Accommodating)
    this.switchToneTab('accommodating');

    // Agreement Markdown View
    const mdContainer = document.getElementById('agreement-markdown-content');
    if (mdContainer) {
      mdContainer.innerHTML = this.renderMarkdownHtml(data.agreement_markdown);
    }
  },

  switchToneTab(tone) {
    document.querySelectorAll('.tab-btn[data-tone]').forEach(btn => {
      btn.classList.toggle('active', btn.getAttribute('data-tone') === tone);
    });

    const responses = this.currentResult?.diplomatic_responses || {};
    const responseText = responses[tone] || 'No response generated for this tone.';
    const previewEl = document.getElementById('response-preview-text');
    if (previewEl) {
      previewEl.innerText = responseText;
    }
  },

  renderMarkdownHtml(md) {
    if (!md) return '';
    // Clean, lightweight markdown-to-HTML parser for addendum preview
    let html = md
      .replace(/^# (.*$)/gim, '<h1>$1</h1>')
      .replace(/^## (.*$)/gim, '<h2>$1</h2>')
      .replace(/^### (.*$)/gim, '<h3>$1</h3>')
      .replace(/^\*\*([^*]+)\*\*/gim, '<strong>$1</strong>')
      .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
      .replace(/---/g, '<hr/>')
      .replace(/^\- (.*$)/gim, '<li>$1</li>')
      .replace(/\n\n/g, '<p></p>');

    return html;
  }
};
