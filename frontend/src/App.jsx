import { useState } from 'react'
import AccountsPage from './components/AccountsPage.jsx'
import GeneratePage from './components/GeneratePage.jsx'
import DashboardPage from './components/DashboardPage.jsx'
import SettingsPage from './components/SettingsPage.jsx'
import LogsPage from './components/LogsPage.jsx'
import MonitorPage from './components/MonitorPage.jsx'
import styles from './App.module.css'
import { useStore } from './store.js'

export default function App() {
  const [tab, setTab] = useState('dashboard')
  const { activeAccount, setActiveAccount } = useStore()

  return (
    <div className={styles.shell}>
      <nav className={styles.nav}>
        <div className={styles.navLogo}>
          <Logo />
          <span>FigureLabs AI</span>
        </div>
        <div className={styles.navTabs}>
          <button
            className={`${styles.navTab} ${tab === 'dashboard' ? styles.active : ''}`}
            onClick={() => setTab('dashboard')}
          >
            Dashboard
          </button>
          <button
            className={`${styles.navTab} ${tab === 'monitor' ? styles.active : ''}`}
            onClick={() => setTab('monitor')}
          >
            Monitor
          </button>
          <button
            className={`${styles.navTab} ${tab === 'accounts' ? styles.active : ''}`}
            onClick={() => setTab('accounts')}
          >
            Accounts
          </button>
          <button
            className={`${styles.navTab} ${tab === 'generate' ? styles.active : ''}`}
            onClick={() => setTab('generate')}
            disabled={!activeAccount}
            title={!activeAccount ? 'Select an account first' : ''}
          >
            Generate
          </button>
          <button
            className={`${styles.navTab} ${tab === 'logs' ? styles.active : ''}`}
            onClick={() => setTab('logs')}
          >
            Logs
          </button>
          <button
            className={`${styles.navTab} ${tab === 'settings' ? styles.active : ''}`}
            onClick={() => setTab('settings')}
          >
            Settings
          </button>
        </div>
        {activeAccount && (
          <div className={styles.navAccount}>
            <span className={styles.navDot} />
            <span className={styles.navAccountLabel}>
              {activeAccount.label || activeAccount.email}
            </span>
          </div>
        )}
      </nav>

      <main className={styles.content}>
        {tab === 'dashboard' && <DashboardPage />}
        {tab === 'monitor' && <MonitorPage />}
        {tab === 'accounts' && (
          <AccountsPage
            activeAccount={activeAccount}
            onSelectAccount={(acc) => { setActiveAccount(acc); setTab('generate') }}
          />
        )}
        {tab === 'generate' && activeAccount && (
          <GeneratePage account={activeAccount} />
        )}
        {tab === 'logs' && <LogsPage />}
        {tab === 'settings' && <SettingsPage />}
      </main>
    </div>
  )
}

function Logo() {
  return (
    <svg width="28" height="28" viewBox="0 0 40 40" fill="none">
      <rect width="40" height="40" rx="10" fill="#1f6feb"/>
      <path d="M10 20 L20 10 L30 20 L20 30 Z" fill="#58a6ff" opacity="0.85"/>
      <circle cx="20" cy="20" r="4" fill="white"/>
    </svg>
  )
}
