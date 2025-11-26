/**
 * Format a price with specified decimal places
 */
export function formatPrice(price: number | null | undefined, decimals: number = 5): string {
  if (price === null || price === undefined || isNaN(price)) {
    return '--';
  }
  return price.toFixed(decimals);
}

/**
 * Format a percentage value
 */
export function formatPercentage(value: number | null | undefined, decimals: number = 2): string {
  if (value === null || value === undefined || isNaN(value)) {
    return '--';
  }
  return `${value.toFixed(decimals)}%`;
}

/**
 * Format a currency value
 */
export function formatCurrency(value: number | null | undefined, currency: string = 'USD'): string {
  if (value === null || value === undefined || isNaN(value)) {
    return '--';
  }
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
}

/**
 * Format a date/time value
 */
export function formatDate(date: string | Date | null | undefined): string {
  if (!date) return '--';
  try {
    return new Date(date).toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return '--';
  }
}

/**
 * Format a date as short date only
 */
export function formatShortDate(date: string | Date | null | undefined): string {
  if (!date) return '--';
  try {
    return new Date(date).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
    });
  } catch {
    return '--';
  }
}

/**
 * Format time only
 */
export function formatTime(date: string | Date | null | undefined): string {
  if (!date) return '--';
  try {
    return new Date(date).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  } catch {
    return '--';
  }
}

/**
 * Format a number with thousand separators
 */
export function formatNumber(value: number | null | undefined, decimals: number = 0): string {
  if (value === null || value === undefined || isNaN(value)) {
    return '--';
  }
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value);
}

/**
 * Format pips value
 */
export function formatPips(pips: number | null | undefined): string {
  if (pips === null || pips === undefined || isNaN(pips)) {
    return '--';
  }
  return `${pips.toFixed(1)} pips`;
}

/**
 * Format lot size
 */
export function formatLotSize(size: number | null | undefined): string {
  if (size === null || size === undefined || isNaN(size)) {
    return '--';
  }
  return `${size.toFixed(2)} lots`;
}

/**
 * Format duration in milliseconds to human readable
 */
export function formatDuration(ms: number): string {
  const seconds = Math.floor(ms / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);

  if (days > 0) return `${days}d ${hours % 24}h`;
  if (hours > 0) return `${hours}h ${minutes % 60}m`;
  if (minutes > 0) return `${minutes}m ${seconds % 60}s`;
  return `${seconds}s`;
}

/**
 * Format relative time (e.g., "2 hours ago")
 */
export function formatRelativeTime(date: string | Date): string {
  const now = new Date();
  const then = new Date(date);
  const diffMs = now.getTime() - then.getTime();
  const diffSecs = Math.floor(diffMs / 1000);
  const diffMins = Math.floor(diffSecs / 60);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffDays > 0) return `${diffDays}d ago`;
  if (diffHours > 0) return `${diffHours}h ago`;
  if (diffMins > 0) return `${diffMins}m ago`;
  return 'just now';
}
