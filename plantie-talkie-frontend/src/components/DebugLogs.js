import React from 'react';

export default function DebugLogs({ logs = [], className = '' }) {
  return (
    <div className={`debug-logs ${className}`}>
      <h2 className="debug-logs__title">System Logs</h2>
      <div className="debug-logs__content">
        {logs.length === 0 ? (
          <p className="debug-logs__empty">No logs available</p>
        ) : (
          <ul className="debug-logs__list">
            {logs.map((log, index) => (
              <li key={index} className="debug-logs__item">
                <span className="debug-logs__timestamp">{log.timestamp}</span>
                <span className={`debug-logs__level debug-logs__level--${log.level.toLowerCase()}`}>
                  {log.level}
                </span>
                <span className="debug-logs__message">{log.message}</span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}