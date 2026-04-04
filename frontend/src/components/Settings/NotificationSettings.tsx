import React, { useState, useEffect } from 'react';
import { signalsApi } from '../../services/api';
import { SettingsStatus, NotificationSettingsData } from '../../types';

// ── Model lists ────────────────────────────────────────────────────────────────

const ANTHROPIC_MODELS = [
  { value: 'claude-opus-4-6',           label: 'Claude Opus 4.6 (most capable)' },
  { value: 'claude-sonnet-4-6',         label: 'Claude Sonnet 4.6 (recommended)' },
  { value: 'claude-haiku-4-5-20251001', label: 'Claude Haiku 4.5 (fast & cheap)' },
];

const OPENAI_MODELS = [
  { value: 'gpt-4o',       label: 'GPT-4o (most capable)' },
  { value: 'gpt-4o-mini',  label: 'GPT-4o Mini (fast & cheap)' },
  { value: 'gpt-3.5-turbo',label: 'GPT-3.5 Turbo (cheapest)' },
];

const OPENROUTER_MODELS = [
  // Free models
  { value: 'meta-llama/llama-3.3-70b-instruct:free', label: '🆓 Llama 3.3 70B (free)' },
  { value: 'meta-llama/llama-3.1-8b-instruct:free',  label: '🆓 Llama 3.1 8B (free, fast)' },
  { value: 'mistralai/mistral-7b-instruct:free',      label: '🆓 Mistral 7B (free)' },
  { value: 'google/gemma-2-9b-it:free',               label: '🆓 Gemma 2 9B (free)' },
  { value: 'qwen/qwen-2.5-7b-instruct:free',          label: '🆓 Qwen 2.5 7B (free)' },
  // Paid — cheap
  { value: 'anthropic/claude-3-haiku',                label: 'Claude 3 Haiku (cheap)' },
  { value: 'anthropic/claude-3.5-haiku',              label: 'Claude 3.5 Haiku' },
  { value: 'anthropic/claude-sonnet-4-5',             label: 'Claude Sonnet 4.5' },
  { value: 'openai/gpt-4o-mini',                      label: 'GPT-4o Mini' },
  { value: 'google/gemini-flash-1.5',                 label: 'Gemini Flash 1.5' },
  { value: 'google/gemini-2.0-flash-001',             label: 'Gemini 2.0 Flash' },
  { value: 'mistralai/mistral-small',                 label: 'Mistral Small' },
  // Powerful
  { value: 'anthropic/claude-opus-4',                 label: 'Claude Opus 4 (powerful)' },
  { value: 'openai/gpt-4o',                           label: 'GPT-4o (powerful)' },
];

const STRATEGIES = [
  'asian_range_breakout', 'session_breakout', 'triple_screen',
  'fair_value_gap', 'vwap_bounce', 'mean_reversion', 'bollinger_breakout',
  'macd_signal', 'rsi_divergence', 'breakout',
];

const DEFAULT_MODELS: Record<string, string> = {
  anthropic:  'claude-sonnet-4-6',
  openai:     'gpt-4o-mini',
  openrouter: 'meta-llama/llama-3.1-8b-instruct:free',
};

// ── Component ──────────────────────────────────────────────────────────────────

export function NotificationSettings() {
  const [status, setStatus]   = useState<SettingsStatus | null>(null);
  const [form, setForm]       = useState<NotificationSettingsData>({});
  const [saving, setSaving]   = useState(false);
  const [testing, setTesting] = useState(false);
  const [testingAI, setTestingAI] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const loadStatus = () => {
    signalsApi.getSettings().then((r) => {
      const d = r.data as SettingsStatus & { openrouter_api_key?: string; anthropic_api_key?: string; openai_api_key?: string };
      setStatus(d);
      setForm((prev) => ({
        telegram_chat_id:      d.telegram_chat_id,
        telegram_min_priority: d.telegram_min_priority,
        ai_provider:           d.ai_provider || 'openrouter',
        ai_model:              d.ai_model || DEFAULT_MODELS[d.ai_provider || 'openrouter'],
        active_strategies:     d.active_strategies,
        signal_scan_interval:  d.signal_scan_interval,
        risk_per_trade_pct:    d.risk_per_trade_pct,
        // keep any unsaved key values the user typed
        telegram_bot_token:    prev.telegram_bot_token,
        openrouter_api_key:    prev.openrouter_api_key,
        anthropic_api_key:     prev.anthropic_api_key,
        openai_api_key:        prev.openai_api_key,
      }));
    }).catch(() => {});
  };

  useEffect(() => { loadStatus(); }, []);

  const set = (k: keyof NotificationSettingsData, v: unknown) =>
    setForm((f) => ({ ...f, [k]: v }));

  // When provider changes, reset model to its default
  const handleProviderChange = (provider: string) => {
    set('ai_provider', provider);
    set('ai_model', DEFAULT_MODELS[provider] || '');
  };

  const provider = form.ai_provider || 'openrouter';

  const modelOptions =
    provider === 'anthropic' ? ANTHROPIC_MODELS :
    provider === 'openai'    ? OPENAI_MODELS :
    OPENROUTER_MODELS;

  // Check if the current model value is in the list (otherwise treat as custom)
  const isCustomModel = form.ai_model
    ? !modelOptions.some((m) => m.value === form.ai_model)
    : false;

  const handleSave = async () => {
    setSaving(true);
    setMessage(null);
    try {
      await signalsApi.updateSettings(form as Record<string, unknown>);
      setMessage({ type: 'success', text: 'Settings saved. Add keys to .env for permanence.' });
      loadStatus();
    } catch {
      setMessage({ type: 'error', text: 'Failed to save settings.' });
    } finally {
      setSaving(false);
    }
  };

  const handleTestTelegram = async () => {
    setTesting(true);
    setMessage(null);
    try {
      await signalsApi.testTelegram();
      setMessage({ type: 'success', text: 'Test message sent! Check your phone.' });
    } catch (e: unknown) {
      const err = e as { message?: string };
      setMessage({ type: 'error', text: err.message || 'Failed — check token and chat ID.' });
    } finally {
      setTesting(false);
    }
  };

  const handleTestAI = async () => {
    setTestingAI(true);
    setMessage(null);
    try {
      // Save current form first, then test
      await signalsApi.updateSettings(form as Record<string, unknown>);
      const r = await signalsApi.testAI();
      setMessage({ type: 'success', text: `AI connected: ${r.data.provider}/${r.data.model}` });
    } catch (e: unknown) {
      const err = e as { response?: { data?: { detail?: string } }; message?: string };
      setMessage({ type: 'error', text: err.response?.data?.detail || err.message || 'AI test failed.' });
    } finally {
      setTestingAI(false);
    }
  };

  return (
    <div className="settings-panel">
      <h2 className="settings-title">Notifications & AI Settings</h2>

      {message && (
        <div className={`settings-msg ${message.type}`}>{message.text}</div>
      )}

      {/* ── Telegram ── */}
      <section className="settings-section">
        <div className="section-header">
          <h3>Telegram Alerts</h3>
          <span className={`status-badge ${status?.telegram_configured ? 'badge-green' : 'badge-gray'}`}>
            {status?.telegram_configured ? '● Connected' : '○ Not configured'}
          </span>
        </div>
        <div className="settings-hint">
          <ol>
            <li>Message <strong>@BotFather</strong> on Telegram → create bot → copy token</li>
            <li>Add <code>TELEGRAM_BOT_TOKEN=your_token</code> to your <code>.env</code> file</li>
            <li>Message <strong>@userinfobot</strong> to get your Chat ID</li>
          </ol>
        </div>
        <div className="form-row">
          <label>Bot Token</label>
          <input
            className="form-input"
            type="password"
            onChange={(e) => set('telegram_bot_token', e.target.value)}
            placeholder="1234567890:ABCdef...  (leave blank to keep existing)"
            autoComplete="off"
          />
        </div>
        <div className="form-row">
          <label>Chat ID</label>
          <input
            className="form-input"
            value={form.telegram_chat_id || ''}
            onChange={(e) => set('telegram_chat_id', e.target.value)}
            placeholder="e.g. 123456789"
          />
        </div>
        <div className="form-row">
          <label>Minimum alert level</label>
          <select
            className="form-select"
            value={form.telegram_min_priority || 'opportunity'}
            onChange={(e) => set('telegram_min_priority', e.target.value)}
          >
            <option value="info">All (info, opportunities, warnings)</option>
            <option value="opportunity">Opportunities + warnings only</option>
            <option value="warning">Warnings + danger only</option>
            <option value="danger">Danger only</option>
          </select>
        </div>
        <button
          className="btn-secondary btn-sm"
          onClick={handleTestTelegram}
          disabled={testing}
        >
          {testing ? 'Sending...' : 'Send Test Message'}
        </button>
      </section>

      {/* ── AI Advisor ── */}
      <section className="settings-section">
        <div className="section-header">
          <h3>AI Advisor</h3>
          <span className={`status-badge ${status?.ai_configured ? 'badge-green' : 'badge-gray'}`}>
            {status?.ai_configured ? `● ${status.ai_provider}` : '○ Not configured'}
          </span>
        </div>

        {/* Provider selector */}
        <div className="form-row">
          <label>Provider</label>
          <div className="provider-tabs">
            {(['openrouter', 'anthropic', 'openai'] as const).map((p) => (
              <button
                key={p}
                className={`provider-tab ${provider === p ? 'active' : ''}`}
                onClick={() => handleProviderChange(p)}
              >
                {p === 'openrouter' ? 'OpenRouter' : p === 'anthropic' ? 'Anthropic' : 'OpenAI'}
              </button>
            ))}
          </div>
        </div>

        {/* API key for the selected provider */}
        {provider === 'openrouter' && (
          <div className="form-row">
            <label>OpenRouter API key</label>
            <input
              className="form-input"
              type="password"
              onChange={(e) => set('openrouter_api_key', e.target.value)}
              placeholder="sk-or-...  (leave blank to keep existing)"
              autoComplete="off"
            />
            <span className="form-hint">
              Free at <strong>openrouter.ai</strong> — gives access to 200+ models including free ones
            </span>
          </div>
        )}
        {provider === 'anthropic' && (
          <div className="form-row">
            <label>Anthropic API key</label>
            <input
              className="form-input"
              type="password"
              onChange={(e) => set('anthropic_api_key', e.target.value)}
              placeholder="sk-ant-...  (leave blank to keep existing)"
              autoComplete="off"
            />
            <span className="form-hint">From <strong>console.anthropic.com</strong></span>
          </div>
        )}
        {provider === 'openai' && (
          <div className="form-row">
            <label>OpenAI API key</label>
            <input
              className="form-input"
              type="password"
              onChange={(e) => set('openai_api_key', e.target.value)}
              placeholder="sk-...  (leave blank to keep existing)"
              autoComplete="off"
            />
            <span className="form-hint">From <strong>platform.openai.com</strong></span>
          </div>
        )}

        {/* Model selector */}
        <div className="form-row">
          <label>Model</label>
          <select
            className="form-select"
            value={isCustomModel ? '__custom__' : (form.ai_model || '')}
            onChange={(e) => {
              if (e.target.value !== '__custom__') set('ai_model', e.target.value);
            }}
          >
            {modelOptions.map((m) => (
              <option key={m.value} value={m.value}>{m.label}</option>
            ))}
            <option value="__custom__">Custom model ID…</option>
          </select>
        </div>

        {/* Custom model input */}
        {(isCustomModel || form.ai_model === '__custom__') && (
          <div className="form-row">
            <label>Custom model ID</label>
            <input
              className="form-input"
              value={form.ai_model === '__custom__' ? '' : (form.ai_model || '')}
              onChange={(e) => set('ai_model', e.target.value)}
              placeholder={provider === 'openrouter' ? 'e.g. mistralai/mistral-small' : 'e.g. gpt-4-turbo'}
            />
          </div>
        )}

        <button
          className="btn-secondary btn-sm"
          onClick={handleTestAI}
          disabled={testingAI}
        >
          {testingAI ? 'Testing...' : 'Test AI Connection'}
        </button>
      </section>

      {/* ── Signal Engine ── */}
      <section className="settings-section">
        <h3>Signal Engine</h3>
        <div className="form-row">
          <label>Active strategies</label>
          <div className="strategy-checkboxes">
            {STRATEGIES.map((s) => {
              const active = (form.active_strategies || '').split(',').map((x) => x.trim());
              const checked = active.includes(s);
              return (
                <label key={s} className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={checked}
                    onChange={(e) => {
                      const next = e.target.checked
                        ? [...active.filter(Boolean), s]
                        : active.filter((x) => x !== s);
                      set('active_strategies', next.join(','));
                    }}
                  />
                  {s.replace(/_/g, ' ')}
                </label>
              );
            })}
          </div>
        </div>
        <div className="form-row">
          <label>Scan interval (seconds)</label>
          <input
            className="form-input form-input-sm"
            type="number" min={10} max={300}
            value={form.signal_scan_interval ?? 30}
            onChange={(e) => set('signal_scan_interval', parseInt(e.target.value))}
          />
        </div>
        <div className="form-row">
          <label>Risk per trade (%)</label>
          <input
            className="form-input form-input-sm"
            type="number" min={0.1} max={5} step={0.1}
            value={form.risk_per_trade_pct ?? 1.0}
            onChange={(e) => set('risk_per_trade_pct', parseFloat(e.target.value))}
          />
        </div>
      </section>

      <button className="btn-primary" onClick={handleSave} disabled={saving}>
        {saving ? 'Saving...' : 'Save Settings'}
      </button>
    </div>
  );
}
