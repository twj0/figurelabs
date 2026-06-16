import { useState } from 'react'
import styles from './SettingsPage.module.css'

export default function SettingsPage() {
  const [settings, setSettings] = useState({
    proxyUrl: '',
    sessionTimeout: 3600,
    maxRetries: 3,
  })
  const [saved, setSaved] = useState(false)

  function handleChange(key, value) {
    setSettings({ ...settings, [key]: value })
    setSaved(false)
  }

  function handleSave() {
    // TODO: Save to backend
    console.log('Saving settings:', settings)
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  return (
    <div className={styles.settings}>
      <header className={styles.header}>
        <h1>Settings</h1>
        <button
          className={styles.saveButton}
          onClick={handleSave}
        >
          {saved ? '✓ Saved' : 'Save Changes'}
        </button>
      </header>

      <div className={styles.sections}>
        <section className={styles.section}>
          <h2>Network</h2>

          <div className={styles.field}>
            <label>Proxy URL</label>
            <input
              type="text"
              placeholder="http://proxy.example.com:8080"
              value={settings.proxyUrl}
              onChange={(e) => handleChange('proxyUrl', e.target.value)}
            />
            <div className={styles.hint}>Optional HTTP/HTTPS proxy for API requests</div>
          </div>

          <div className={styles.field}>
            <label>Session Timeout (seconds)</label>
            <input
              type="number"
              value={settings.sessionTimeout}
              onChange={(e) => handleChange('sessionTimeout', parseInt(e.target.value))}
            />
            <div className={styles.hint}>How long to keep sessions active</div>
          </div>
        </section>

        <section className={styles.section}>
          <h2>Reliability</h2>

          <div className={styles.field}>
            <label>Max Retries</label>
            <input
              type="number"
              min="0"
              max="10"
              value={settings.maxRetries}
              onChange={(e) => handleChange('maxRetries', parseInt(e.target.value))}
            />
            <div className={styles.hint}>Number of retries for failed requests</div>
          </div>
        </section>

        <section className={styles.section}>
          <h2>Storage</h2>

          <div className={styles.field}>
            <label>Database Backend</label>
            <select disabled>
              <option>SQLite (data/data.db)</option>
            </select>
            <div className={styles.hint}>Set DATABASE_URL environment variable for PostgreSQL</div>
          </div>
        </section>
      </div>
    </div>
  )
}
