import { useState, useEffect } from 'react'
import styles from './LogsPage.module.css'

export default function LogsPage() {
  const [logs, setLogs] = useState([])
  const [filter, setFilter] = useState('all') // all, error, info, warning
  const [autoRefresh, setAutoRefresh] = useState(true)

  useEffect(() => {
    fetchLogs()

    if (autoRefresh) {
      const interval = setInterval(fetchLogs, 5000)
      return () => clearInterval(interval)
    }
  }, [autoRefresh])

  async function fetchLogs() {
    try {
      // Mock logs - replace with actual API call
      const mockLogs = [
        { id: 1, timestamp: Date.now() - 10000, level: 'info', message: 'Account registration successful', source: 'accounts' },
        { id: 2, timestamp: Date.now() - 20000, level: 'error', message: 'Failed to connect to mail service', source: 'register' },
        { id: 3, timestamp: Date.now() - 30000, level: 'info', message: 'Session created for user abc123', source: 'chat' },
        { id: 4, timestamp: Date.now() - 40000, level: 'warning', message: 'Rate limit approaching for account xyz789', source: 'api' },
        { id: 5, timestamp: Date.now() - 50000, level: 'info', message: 'Image generated successfully', source: 'generate' },
      ]
      setLogs(mockLogs)
    } catch (err) {
      console.error('Failed to fetch logs:', err)
    }
  }

  const filteredLogs = filter === 'all'
    ? logs
    : logs.filter(log => log.level === filter)

  return (
    <div className={styles.logs}>
      <header className={styles.header}>
        <h1>Logs</h1>
        <div className={styles.controls}>
          <div className={styles.filters}>
            {['all', 'info', 'warning', 'error'].map((level) => (
              <button
                key={level}
                className={`${styles.filterBtn} ${filter === level ? styles.active : ''}`}
                onClick={() => setFilter(level)}
              >
                {level.charAt(0).toUpperCase() + level.slice(1)}
              </button>
            ))}
          </div>
          <label className={styles.autoRefresh}>
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
            />
            Auto-refresh
          </label>
          <button className={styles.refreshBtn} onClick={fetchLogs}>
            Refresh
          </button>
        </div>
      </header>

      <div className={styles.logList}>
        {filteredLogs.length === 0 ? (
          <div className={styles.empty}>No logs to display</div>
        ) : (
          filteredLogs.map((log) => (
            <div key={log.id} className={`${styles.logEntry} ${styles[log.level]}`}>
              <span className={styles.timestamp}>
                {new Date(log.timestamp).toLocaleTimeString()}
              </span>
              <span className={`${styles.level} ${styles[log.level]}`}>
                {log.level.toUpperCase()}
              </span>
              <span className={styles.source}>[{log.source}]</span>
              <span className={styles.message}>{log.message}</span>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
