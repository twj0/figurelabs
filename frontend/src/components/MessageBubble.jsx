import { useState } from 'react'
import styles from './MessageBubble.module.css'

const FORMATS = [
  { key: 'png', label: 'PNG' },
  { key: 'svg', label: 'SVG' },
  { key: 'pptx', label: 'PPTX' },
]

export default function MessageBubble({ msg, token }) {
  const [downloading, setDownloading] = useState(null)

  async function handleDownload(fmt) {
    setDownloading(fmt)
    try {
      const url = `/api/download/${msg.messageId}?token=${encodeURIComponent(token)}&fmt=${fmt}`
      const res = await fetch(url)
      if (!res.ok) throw new Error('Download failed')
      const blob = await res.blob()
      const a = document.createElement('a')
      a.href = URL.createObjectURL(blob)
      a.download = `figure.${fmt}`
      a.click()
      URL.revokeObjectURL(a.href)
    } catch (_) {}
    finally { setDownloading(null) }
  }

  if (msg.role === 'user') {
    return (
      <div className={styles.userRow}>
        <div className={styles.userBubble}>{msg.text}</div>
      </div>
    )
  }

  // Assistant message
  return (
    <div className={styles.assistantRow}>
      <div className={styles.avatar}>
        <svg width="18" height="18" viewBox="0 0 40 40" fill="none">
          <rect width="40" height="40" rx="10" fill="#1f6feb"/>
          <path d="M10 20 L20 10 L30 20 L20 30 Z" fill="#58a6ff" opacity="0.8"/>
          <circle cx="20" cy="20" r="4" fill="white"/>
        </svg>
      </div>

      <div className={styles.assistantContent}>
        {msg.status === 'pending' && (
          <div className={styles.pending}>
            <PulsingDots />
            <span>{msg.text}</span>
          </div>
        )}

        {msg.status === 'error' && (
          <div className={styles.error}>{msg.text}</div>
        )}

        {msg.status === 'done' && (
          <div className={styles.doneCard}>
            <div className={styles.imageWrap}>
              <img
                src={`/api/download/${msg.messageId}?token=${encodeURIComponent(token)}&fmt=png`}
                alt="Generated diagram"
                className={styles.image}
              />
            </div>
            <div className={styles.exportRow}>
              <span className={styles.exportLabel}>Export as:</span>
              {FORMATS.map(f => (
                <button
                  key={f.key}
                  className={styles.exportBtn}
                  onClick={() => handleDownload(f.key)}
                  disabled={downloading === f.key}
                >
                  {downloading === f.key ? '…' : f.label}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

function PulsingDots() {
  return (
    <span className={styles.dots}>
      <span/><span/><span/>
    </span>
  )
}
