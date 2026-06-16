import { useState, useEffect } from 'react'
import styles from './AccountsPage.module.css'

export default function AccountsPage({ activeAccount, onSelectAccount }) {
  const [accounts, setAccounts] = useState([])
  const [loading, setLoading] = useState(true)
  const [registering, setRegistering] = useState(false)
  const [mailSvc, setMailSvc] = useState('mailtm')
  const [error, setError] = useState('')
  // DuckMail pending flow
  const [duck, setDuck] = useState(null)   // {pending_id, email, inbox_url}
  const [duckCode, setDuckCode] = useState('')
  const [duckLoading, setDuckLoading] = useState(false)
  const [editingId, setEditingId] = useState(null)
  const [editLabel, setEditLabel] = useState('')

  useEffect(() => { fetchAccounts() }, [])

  async function fetchAccounts() {
    setLoading(true)
    try {
      const r = await fetch('/api/accounts')
      setAccounts(await r.json())
    } finally { setLoading(false) }
  }

  async function handleRegister() {
    setRegistering(true)
    setError('')
    setDuck(null)
    try {
      const r = await fetch('/api/accounts/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mail_service: mailSvc }),
      })
      const data = await r.json()
      if (!r.ok) throw new Error(data.detail || 'Failed')

      if (data.done) {
        setAccounts(prev => [data.account, ...prev])
      } else {
        // DuckMail: needs manual code
        setDuck({ pending_id: data.pending_id, email: data.email, inbox_url: data.inbox_url })
      }
    } catch (e) { setError(e.message) }
    finally { setRegistering(false) }
  }

  async function handleDuckVerify() {
    setDuckLoading(true)
    setError('')
    try {
      const r = await fetch('/api/accounts/verify-duckmail', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ pending_id: duck.pending_id, code: duckCode }),
      })
      const data = await r.json()
      if (!r.ok) throw new Error(data.detail || 'Verification failed')
      setAccounts(prev => [data.account, ...prev])
      setDuck(null)
      setDuckCode('')
    } catch (e) { setError(e.message) }
    finally { setDuckLoading(false) }
  }

  async function handleDelete(userId) {
    if (!confirm('Remove this account from the database?')) return
    await fetch(`/api/accounts/${userId}`, { method: 'DELETE' })
    setAccounts(prev => prev.filter(a => a.user_id !== userId))
  }

  async function saveLabel(userId) {
    await fetch(`/api/accounts/${userId}/label`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ label: editLabel }),
    })
    setAccounts(prev => prev.map(a => a.user_id === userId ? { ...a, label: editLabel } : a))
    setEditingId(null)
  }

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <div>
          <h1 className={styles.title}>Account Manager</h1>
          <p className={styles.subtitle}>{accounts.length} account{accounts.length !== 1 ? 's' : ''} saved</p>
        </div>
        <div className={styles.registerBar}>
          <div className={styles.svcToggle}>
            {['mailtm', 'duckmail'].map(s => (
              <button
                key={s}
                className={`${styles.svcBtn} ${mailSvc === s ? styles.svcBtnActive : ''}`}
                onClick={() => { setMailSvc(s); setDuck(null); setError('') }}
                disabled={registering}
              >
                {s === 'mailtm' ? 'Mail.tm' : 'DuckMail'}
              </button>
            ))}
          </div>
          <button className={styles.btnRegister} onClick={handleRegister} disabled={registering}>
            {registering
              ? <><Spinner /> Registering…</>
              : mailSvc === 'mailtm' ? 'Auto Register' : 'Create Address'}
          </button>
        </div>
      </div>

      {error && <div className={styles.error}>{error}</div>}

      {/* DuckMail manual verification panel */}
      {duck && (
        <div className={styles.duckPanel}>
          <p className={styles.duckTitle}>Manual verification required</p>
          <p className={styles.duckInfo}>
            Email: <strong>{duck.email}</strong>
          </p>
          <a className={styles.duckLink} href={duck.inbox_url} target="_blank" rel="noreferrer">
            Open Inbox ↗
          </a>
          <div className={styles.duckRow}>
            <input
              className={styles.codeInput}
              placeholder="Enter 6-digit code"
              value={duckCode}
              onChange={e => setDuckCode(e.target.value)}
              maxLength={6}
            />
            <button
              className={styles.btnVerify}
              onClick={handleDuckVerify}
              disabled={duckCode.length < 6 || duckLoading}
            >
              {duckLoading ? 'Verifying…' : 'Verify'}
            </button>
            <button className={styles.btnCancel} onClick={() => setDuck(null)}>Cancel</button>
          </div>
        </div>
      )}

      {loading
        ? <div className={styles.loading}>Loading…</div>
        : accounts.length === 0
          ? <div className={styles.empty}>No accounts yet. Register one above.</div>
          : (
          <div className={styles.table}>
            <div className={styles.thead}>
              <div className={styles.col}>Label / Email</div>
              <div className={styles.col}>Service</div>
              <div className={styles.col}>User ID</div>
              <div className={styles.col}>Expires</div>
              <div className={styles.colActions}>Actions</div>
            </div>
            {accounts.map(acc => (
              <div
                key={acc.user_id}
                className={`${styles.row} ${activeAccount?.user_id === acc.user_id ? styles.rowActive : ''}`}
              >
                <div className={styles.col}>
                  {editingId === acc.user_id
                    ? <input
                        className={styles.labelInput}
                        value={editLabel}
                        onChange={e => setEditLabel(e.target.value)}
                        onKeyDown={e => { if (e.key === 'Enter') saveLabel(acc.user_id); if (e.key === 'Escape') setEditingId(null) }}
                        autoFocus
                      />
                    : <>
                        <span
                          className={styles.label}
                          onClick={() => { setEditingId(acc.user_id); setEditLabel(acc.label || '') }}
                          title="Click to edit label"
                        >
                          {acc.label || acc.email}
                        </span>
                        {acc.label && <span className={styles.emailSub}>{acc.email}</span>}
                      </>
                  }
                </div>
                <div className={styles.col}>
                  <span className={`${styles.badge} ${acc.mail_service === 'mailtm' ? styles.badgeBlue : styles.badgeGreen}`}>
                    {acc.mail_service === 'mailtm' ? 'Mail.tm' : 'DuckMail'}
                  </span>
                </div>
                <div className={styles.col}>
                  <span className={styles.uid}>{acc.user_id}</span>
                </div>
                <div className={styles.col}>
                  <span className={styles.expires}>
                    {acc.expires_time ? new Date(acc.expires_time).toLocaleDateString() : '—'}
                  </span>
                </div>
                <div className={styles.colActions}>
                  <button
                    className={styles.btnUse}
                    onClick={() => onSelectAccount(acc)}
                  >
                    Use
                  </button>
                  <button
                    className={styles.btnDel}
                    onClick={() => handleDelete(acc.user_id)}
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )
      }
    </div>
  )
}

function Spinner() {
  return (
    <svg width="14" height="14" viewBox="0 0 16 16" fill="none" style={{ animation: 'spin 0.8s linear infinite', display: 'inline-block' }}>
      <style>{`@keyframes spin{to{transform:rotate(360deg)}}`}</style>
      <circle cx="8" cy="8" r="6" stroke="white" strokeWidth="2" strokeDasharray="28" strokeDashoffset="10" strokeLinecap="round"/>
    </svg>
  )
}
