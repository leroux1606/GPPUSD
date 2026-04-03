import React, { useState, useEffect } from 'react';
import { signalsApi } from '../../services/api';
import { SettingsStatus, NotificationSettingsData } from '../../types';

const MODELS = [
  { value: 'anthropic/claude-3-haiku', label: 'Claude 3 Haiku (fast, cheap)' },
  { value: 'anthropic/claude-3-sonnet', label: 'Claude 3 Sonnet (balanced)' },
  { value: 'openai/gpt-4o-mini', label: 'GPT-4o Mini (fast)' },
  { value: 'google/gemini-flash-1.5', label: 'Gemini Flash 1.5' },
];

const STRATEGIES = [
  'asian_range_breakout', 'session_breakout', 'triple_screen',
  'fair_value_gap', 'vwap_bounce', 'mean_reversion', 'bollinger_breakout',
  'macd_signal', 'rsi_divergence', 'breakout',
];

export function NotificationSettings() {
  const [status, setStatus] = useState<SettingsStatus | null>(null);
  const [form, setForm] = useState<NotificationSettingsData>({});
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    signalsApi.getSettings().then((r) => {
      setStatus(r.data);
      setForm({
        telegram_chat_id: r.data.telegram_chat_id,
        telegram_min_priority: r.data.telegram_min_priority,
        openrouter_model: r.data.openrouter_model,
        active_strategies: r.data.active_strategies,
        signal_scan_interval: r.data.signal_scan_interval,
        risk_per_trade_pct: r.data.risk_per_trade_pct,
      });
    }).catch(() => {});
  }, []);

  const set = (k: keyof NotificationSettingsData, v: unknown) =>
    setForm((f) => ({ ...f, [k]: v }));

  const handleSave = async () => {
    setSaving(true);
    setMessage(null);
    try {
      await signalsApi.updateSettings(form as Record<string, unknown>);
      setMessage({ type: 'success', text: 'Settings saved for this session. Add to .env for permanence.' });
      const r = await signalsApi.getSettings();
      setStatus(r.data);
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
      setMessage({ type: 'success', text: 'Test message sent to Telegram! Check your phone.' });
    } catch (e: unknown) {
      const err = e as { message?: string };
      setMessage({ type: 'error', text: err.message || 'Failed — check token and chat ID.' });
    } finally {
      setTesting(false);
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
            <li>Message your bot once, then message <strong>@userinfobot</strong> to get your Chat ID</li>
          </ol>
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
          disabled={testing || !status?.telegram_configured}
        >
          {testing ? 'Sending...' : 'Send Test Message'}
        </button>
      </section>

      {/* ── AI Advisor ── */}
      <section className="settings-section">
        <div className="section-header">
          <h3>AI Advisor (OpenRouter)</h3>
          <span className={`status-badge ${status?.ai_configured ? 'badge-green' : 'badge-gray'}`}>
            {status?.ai_configured ? '● Connected' : '○ Not configured'}
          </span>
        </div>

        <div className="settings-hint">
          Get a free API key at <strong>openrouter.ai</strong> — add it to <code>.env</code> as{' '}
          <code>OPENROUTER_API_KEY=sk-or-...</code>
        </div>

        <div className="form-row">
          <label>Model</label>
          <select
            className="form-select"
            value={form.openrouter_model || 'anthropic/claude-3-haiku'}
            onChange={(e) => set('openrouter_model', e.target.value)}
          >
            {MODELS.map((m) => (
              <option key={m.value} value={m.value}>{m.label}</option>
            ))}
          </select>
        </div>
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
            type="number"
            min={10}
            max={300}
            value={form.signal_scan_interval ?? 30}
            onChange={(e) => set('signal_scan_interval', parseInt(e.target.value))}
          />
        </div>

        <div className="form-row">
          <label>Risk per trade (%)</label>
          <input
            className="form-input form-input-sm"
            type="number"
            min={0.1}
            max={5}
            step={0.1}
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
