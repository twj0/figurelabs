import { useState, useEffect } from 'react'
import styles from './MonitorPage.module.css'

export default function MonitorPage() {
  const [health, setHealth] = useState({
    status: 'healthy',
    uptime: 0,
    cpu: 0,
    memory: 0,
    requests: 0,
  })
  const [accounts, setAccounts] = useState([])

  useEffect(() => {
    fetchMonitorData()
    const interval = setInterval(fetchMonitorData, 3000)
    return () => clearInterval(interval)
  }, [])

  async function fetchMonitorData() {
    try {
      // Mock data - replace with actual API calls
      setHealth({
        status: 'healthy',
        uptime: Math.floor(Date.now() / 1000 - 86400),
        cpu: Math.random() * 40 + 10,
        memory: Math.random() * 30 + 40,
        requests: Math.floor(Math.random() * 100 + 50),
      })

      const accountsRes = await fetch('/api/accounts')
      if (accountsRes.ok) {
        setAccounts(await accountsRes.json())
      }
    } catch (err) {
      console.error('Failed to fetch monitor data:', err)
    }
  }

  const formatUptime = (seconds) => {
    const days = Math.floor(seconds / 86400)
    const hours = Math.floor((seconds % 86400) / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    return `${days}d ${hours}h ${minutes}m`
  }

  const activeAccounts = accounts.filter(acc => !acc.disabled).length

  return (
    <div className={styles.monitor}>
      <header className={styles.header}>
        <h1>System Monitor</h1>
        <div className={`${styles.statusBadge} ${styles[health.status]}`}>
          <span className={styles.statusDot} />
          {health.status === 'healthy' ? 'All Systems Operational' : 'Issues Detected'}
        </div>
      </header>

      <div className={styles.grid}>
        <div className={styles.card}>
          <h3>System Health</h3>
          <div className={styles.metrics}>
            <div className={styles.metric}>
              <div className={styles.metricLabel}>Uptime</div>
              <div className={styles.metricValue}>{formatUptime(health.uptime)}</div>
            </div>
            <div className={styles.metric}>
              <div className={styles.metricLabel}>CPU Usage</div>
              <div className={styles.metricValue}>{health.cpu.toFixed(1)}%</div>
              <div className={styles.progressBar}>
                <div
                  className={styles.progressFill}
                  style={{ width: `${health.cpu}%`, backgroundColor: health.cpu > 80 ? '#d73a49' : '#1f6feb' }}
                />
              </div>
            </div>
            <div className={styles.metric}>
              <div className={styles.metricLabel}>Memory Usage</div>
              <div className={styles.metricValue}>{health.memory.toFixed(1)}%</div>
              <div className={styles.progressBar}>
                <div
                  className={styles.progressFill}
                  style={{ width: `${health.memory}%`, backgroundColor: health.memory > 80 ? '#d73a49' : '#1f6feb' }}
                />
              </div>
            </div>
          </div>
        </div>

        <div className={styles.card}>
          <h3>Request Stats</h3>
          <div className={styles.stats}>
            <div className={styles.stat}>
              <div className={styles.statValue}>{health.requests}</div>
              <div className={styles.statLabel}>Requests/min</div>
            </div>
            <div className={styles.stat}>
              <div className={styles.statValue}>{accounts.length}</div>
              <div className={styles.statLabel}>Total Accounts</div>
            </div>
            <div className={styles.stat}>
              <div className={styles.statValue}>{activeAccounts}</div>
              <div className={styles.statLabel}>Active</div>
            </div>
          </div>
        </div>

        <div className={styles.card}>
          <h3>Account Status</h3>
          <div className={styles.accountList}>
            {accounts.slice(0, 5).map((account) => (
              <div key={account.id} className={styles.accountItem}>
                <div className={styles.accountInfo}>
                  <span className={styles.accountLabel}>
                    {account.label || account.email}
                  </span>
                  <span className={styles.accountEmail}>{account.email}</span>
                </div>
                <div className={`${styles.accountStatus} ${account.disabled ? styles.disabled : styles.active}`}>
                  {account.disabled ? 'Disabled' : 'Active'}
                </div>
              </div>
            ))}
            {accounts.length > 5 && (
              <div className={styles.accountMore}>
                +{accounts.length - 5} more accounts
              </div>
            )}
          </div>
        </div>

        <div className={styles.card}>
          <h3>Recent Activity</h3>
          <div className={styles.activity}>
            <div className={styles.activityItem}>
              <span className={styles.activityTime}>2 min ago</span>
              <span className={styles.activityText}>Session created</span>
            </div>
            <div className={styles.activityItem}>
              <span className={styles.activityTime}>5 min ago</span>
              <span className={styles.activityText}>Image generated</span>
            </div>
            <div className={styles.activityItem}>
              <span className={styles.activityTime}>12 min ago</span>
              <span className={styles.activityText}>Account registered</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
