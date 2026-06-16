import { useState } from 'react'
import AccountsPage from './components/AccountsPage.jsx'
import GeneratePage from './components/GeneratePage.jsx'
import styles from './App.module.css'

export default function App() {
  const [tab, setTab] = useState('accounts')
  const [activeAccount, setActiveAccount] = useState(null)

  return (
    <div className={styles.shell}>
      <nav className={styles.nav}>
        <div className={styles.navLogo}>
          <Logo />
          <span>FigureLabs AI</span>
        </div>
        <div className={styles.navTabs}>
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
        {tab === 'accounts' && (
          <AccountsPage
            activeAccount={activeAccount}
            onSelectAccount={(acc) => { setActiveAccount(acc); setTab('generate') }}
          />
        )}
        {tab === 'generate' && activeAccount && (
          <GeneratePage account={activeAccount} />
        )}
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
