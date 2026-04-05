import React, { useEffect, useRef } from 'react';
import { useNotificationStore } from '../../store/notificationStore';
import { AppNotification } from '../../types';

const PRIORITY_COLORS: Record<string, string> = {
  info: 'notif-info',
  opportunity: 'notif-opportunity',
  warning: 'notif-warning',
  danger: 'notif-danger',
};

const PRIORITY_ICONS: Record<string, string> = {
  info: 'ℹ',
  opportunity: '⊕',
  warning: '⚠',
  danger: '⛔',
};

const AUTO_DISMISS_MS: Record<string, number> = {
  info: 6000,
  opportunity: 12000,
  warning: 10000,
  danger: 0, // never auto-dismiss danger
};

function Toast({ n, onDismiss }: { n: AppNotification; onDismiss: (id: string) => void }) {
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const delay = AUTO_DISMISS_MS[n.type] ?? 8000;

  useEffect(() => {
    if (delay > 0) {
      timerRef.current = setTimeout(() => onDismiss(n.id), delay);
    }
    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [n.id, delay, onDismiss]);

  return (
    <div className={`toast ${PRIORITY_COLORS[n.type] || 'notif-info'}`}>
      <span className="toast-icon">{PRIORITY_ICONS[n.type] || 'ℹ'}</span>
      <div className="toast-body">
        <p className="toast-message">{n.message}</p>
        {n.signal && (
          <div className="toast-signal-meta">
            <span>SL {n.signal.stop_loss.toFixed(5)}</span>
            <span className="separator">·</span>
            <span>TP {n.signal.take_profit.toFixed(5)}</span>
            <span className="separator">·</span>
            <span>R/R 1:{n.signal.rr_ratio.toFixed(2)}</span>
          </div>
        )}
      </div>
      <button className="toast-close" onClick={() => onDismiss(n.id)}>✕</button>
    </div>
  );
}

export function NotificationOverlay() {
  const { notifications, dismissNotification } = useNotificationStore();
  // Only show opportunity/warning/danger as toasts — info goes to bell only. Max 3.
  const visible = notifications
    .filter((n) => !n.read && n.type !== 'info')
    .slice(0, 3);

  return (
    <div className="notification-overlay" aria-live="polite">
      {visible.map((n) => (
        <Toast key={n.id} n={n} onDismiss={dismissNotification} />
      ))}
    </div>
  );
}

// ── Notification Bell (for Navbar) ──────────────────────────────────────────

export function NotificationBell() {
  const { notifications, unreadCount, markAllRead } = useNotificationStore();
  const [open, setOpen] = React.useState(false);

  const hasDanger = notifications.some((n) => !n.read && n.type === 'danger');
  const hasWarning = notifications.some((n) => !n.read && n.type === 'warning');

  const bellClass = hasDanger ? 'bell-danger' : hasWarning ? 'bell-warning' : unreadCount > 0 ? 'bell-active' : '';

  return (
    <div className="notification-bell-wrapper">
      <button
        className={`notification-bell ${bellClass}`}
        onClick={() => { setOpen((o) => !o); if (unreadCount > 0) markAllRead(); }}
        title="Notifications"
      >
        🔔
        {unreadCount > 0 && <span className="bell-badge">{unreadCount > 99 ? '99+' : unreadCount}</span>}
      </button>

      {open && (
        <div className="notification-dropdown">
          <div className="notif-dropdown-header">
            <span>Notifications</span>
            <button className="btn-xs" onClick={() => setOpen(false)}>✕</button>
          </div>
          <div className="notif-dropdown-list">
            {notifications.length === 0 ? (
              <p className="text-muted p-2">No notifications yet</p>
            ) : (
              notifications.slice(0, 30).map((n) => (
                <div key={n.id} className={`notif-item ${PRIORITY_COLORS[n.type]}`}>
                  <span className="notif-item-icon">{PRIORITY_ICONS[n.type]}</span>
                  <div className="notif-item-body">
                    <p className="notif-item-msg">{n.message}</p>
                    <span className="notif-item-time">
                      {new Date(n.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}
