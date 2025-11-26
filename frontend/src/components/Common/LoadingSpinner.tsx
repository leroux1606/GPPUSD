import React from 'react';

interface LoadingSpinnerProps {
  message?: string;
  size?: 'small' | 'medium' | 'large';
}

export function LoadingSpinner({ message = 'Loading...', size = 'medium' }: LoadingSpinnerProps) {
  const sizeClasses = {
    small: 'spinner-small',
    medium: 'spinner-medium',
    large: 'spinner-large',
  };

  return (
    <div className="loading-spinner">
      <div className={`spinner ${sizeClasses[size]}`}></div>
      {message && <p className="spinner-message">{message}</p>}
    </div>
  );
}

// Inline loading indicator for buttons or small areas
export function InlineSpinner({ size = 16 }: { size?: number }) {
  return (
    <span
      className="inline-spinner"
      style={{
        width: size,
        height: size,
        borderWidth: Math.max(2, size / 8),
      }}
    />
  );
}
