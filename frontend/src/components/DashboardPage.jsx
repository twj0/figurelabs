import { useState, useEffect } from 'react'
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import styles from './DashboardPage.module.css'

export default function DashboardPage() {
  const [stats, setStats] = useState(null)
  const [totals, setTotals] = useState({ success: 0, failed: 0 })
  const [accounts, setAccounts] = useState([])
  const [timeRange, setTimeRange] = useState('24h')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchData()
  }, [timeRange])

  async function fetchData() {
    setLoading(true)
    try {
      const [statsRes, totalsRes, accountsRes] = await Promise.all([
        fetch(`/api/stats?time_range=${timeRange}`),
        fetch('/api/stats/totals'),
        fetch('/api/accounts'),
      ])

      setStats(await statsRes.json())
      setTotals(await totalsRes.json())
      setAccounts(await accountsRes.json())
    } catch (err) {
      console.error('Failed to fetch dashboard data:', err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className={styles.loading}>Loading dashboard...</div>
  }

  const successRate = totals.success + totals.failed > 0
    ? ((totals.success / (totals.success + totals.failed)) * 100).toFixed(1)
    : 0

  // Transform data for Recharts
  const chartData = stats ? stats.labels.map((label, i) => ({
    time: label,
    total: stats.total_requests[i],
    failed: stats.failed_requests[i],
    success: stats.total_requests[i] - stats.failed_requests[i],
  })) : []

  return (
    <div className={styles.dashboard}>
      <header className={styles.header}>
        <h1>Dashboard</h1>
        <div className={styles.timeSelector}>
          {['24h', '7d', '30d'].map((range) => (
            <button
              key={range}
              className={timeRange === range ? styles.active : ''}
              onClick={() => setTimeRange(range)}
            >
              {range}
            </button>
          ))}
        </div>
      </header>

      <div className={styles.cards}>
        <div className={styles.card}>
          <div className={styles.cardLabel}>Total Accounts</div>
          <div className={styles.cardValue}>{accounts.length}</div>
        </div>

        <div className={styles.card}>
          <div className={styles.cardLabel}>Success Rate</div>
          <div className={styles.cardValue}>{successRate}%</div>
        </div>

        <div className={styles.card}>
          <div className={styles.cardLabel}>Total Requests</div>
          <div className={styles.cardValue}>{totals.success + totals.failed}</div>
        </div>

        <div className={styles.card}>
          <div className={styles.cardLabel}>Failed Requests</div>
          <div className={styles.cardValue}>{totals.failed}</div>
        </div>
      </div>

      {stats && chartData.length > 0 && (
        <div className={styles.charts}>
          <div className={styles.chartCard}>
            <h3>Request Volume Over Time</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="total" stroke="#1f6feb" strokeWidth={2} name="Total Requests" />
                <Line type="monotone" dataKey="success" stroke="#1a7f64" strokeWidth={2} name="Success" />
                <Line type="monotone" dataKey="failed" stroke="#d73a49" strokeWidth={2} name="Failed" />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <div className={styles.chartCard}>
            <h3>Request Distribution</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="success" fill="#1a7f64" name="Success" />
                <Bar dataKey="failed" fill="#d73a49" name="Failed" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  )
}
