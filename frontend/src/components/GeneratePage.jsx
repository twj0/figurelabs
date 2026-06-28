import { useState, useRef, useEffect } from 'react'
import styles from './GeneratePage.module.css'
import MessageBubble from './MessageBubble.jsx'

const MODES = [
  {
    key: 'scientific',
    label: 'Scientific Illustration',
    icon: '🔬',
    agentId: 7,
    scene: 'gen-svg',
    outputType: 'png', // Generates PNG bitmap images
    templates: [
      { id: 'general', label: 'General Science', description: 'Multi-domain scientific diagrams' },
      { id: 'biology', label: 'Biology', description: 'Cell structures, DNA, molecules' },
      { id: 'physics', label: 'Physics', description: 'Circuits, forces, optics' },
      { id: 'chemistry', label: 'Chemistry', description: 'Reactions, compounds, lab equipment' },
      { id: 'cs', label: 'Computer Science', description: 'Algorithms, data structures, networks' },
    ]
  },
  {
    key: 'flowchart',
    label: 'Flowcharts & Diagrams',
    icon: '📊',
    agentId: 0,
    scene: 'tech-roadmap',
    outputType: 'svg', // Generates SVG vector code
    templates: [
      { id: 'tech-roadmap', label: 'Tech Roadmap', description: 'Technology roadmap diagrams' },
      { id: 'framework', label: 'Framework', description: 'Framework architecture diagrams' },
      { id: 'research-workflow', label: 'Research Workflow', description: 'Research process flows' },
      { id: 'fishbone', label: 'Fishbone Diagram', description: 'Cause-and-effect analysis' },
      { id: 'consort-flow-diagram', label: 'CONSORT Flow', description: 'Clinical trial flow diagrams' },
      { id: 'prisma-flow-diagram', label: 'PRISMA Flow', description: 'Systematic review flow' },
    ]
  }
]

const MODELS = [
  { id: 7,  label: 'Nano Banana Pro', sub: 'Gemini · ~30s' },
  { id: 12, label: 'GPT Image 2',     sub: 'OpenAI · ~90s' },
  { id: 10, label: 'Nano Banana 2',   sub: 'Fast · ~30s'   },
]
const RATIOS = ['16:9', '1:1', '4:3', '3:2', '2:3', '9:16', '3:4']

export default function GeneratePage({ account }) {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [mode, setMode] = useState('scientific')
  const [template, setTemplate] = useState('general')
  const [modelId, setModelId] = useState(7)
  const [ratio, setRatio] = useState('16:9')
  const [sessionId, setSessionId] = useState(null)
  const [busy, setBusy] = useState(false)
  const [expanding, setExpanding] = useState(false)
  const bottomRef = useRef(null)

  const currentMode = MODES.find(m => m.key === mode)

  // Reset session when account changes
  useEffect(() => { setSessionId(null); setMessages([]) }, [account.user_id])

  // Reset template when mode changes
  useEffect(() => {
    const firstTemplate = MODES.find(m => m.key === mode)?.templates[0]?.id
    if (firstTemplate) setTemplate(firstTemplate)
  }, [mode])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  async function ensureSession() {
    if (sessionId) return sessionId
    const r = await fetch('/api/session', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        access_token: account.access_token,
        title: `${currentMode.label} - ${new Date().toLocaleDateString()}`,
        agent_id: currentMode.agentId
      }),
    })
    if (!r.ok) throw new Error('Failed to create session')
    const { session_id } = await r.json()
    setSessionId(session_id)
    return session_id
  }

  async function handleExpand() {
    const text = input.trim()
    if (!text || expanding) return
    setExpanding(true)
    try {
      const r = await fetch('/api/expand', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ access_token: account.access_token, message: text }),
      })
      if (!r.ok) { const d = await r.json(); throw new Error(d.detail) }
      const { expanded } = await r.json()
      setInput(expanded)
    } catch (e) {
      console.error('Expand failed:', e.message)
    } finally { setExpanding(false) }
  }

  async function handleSend() {
    const text = input.trim()
    if (!text || busy) return
    setInput('')
    setBusy(true)

    const pendingId = Date.now()
    setMessages(prev => [
      ...prev,
      { id: pendingId - 1, role: 'user', text },
      { id: pendingId, role: 'assistant', status: 'pending' },
    ])

    try {
      const sid = await ensureSession()
      const r = await fetch('/api/message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          access_token: account.access_token,
          session_id: sid,
          text,
          model_id: modelId,
          ratio,
          scene: currentMode.scene,
        }),
      })
      if (!r.ok) { const d = await r.json(); throw new Error(d.detail) }
      const { message_id } = await r.json()

      const poll = setInterval(async () => {
        try {
          const sr = await fetch(`/api/status/${message_id}?token=${encodeURIComponent(account.access_token)}`)
          const st = await sr.json()
          if (st.status === 1 && st.file_url?.length) {
            clearInterval(poll)
            setMessages(prev => prev.map(m =>
              m.id === pendingId
                ? {
                    ...m,
                    status: 'done',
                    messageId: message_id,
                    file_url: st.file_url[0],
                    outputType: currentMode.outputType
                  }
                : m
            ))
            setBusy(false)
          } else if (st.status === 2) {
            clearInterval(poll)
            setMessages(prev => prev.map(m =>
              m.id === pendingId
                ? { ...m, status: 'error', text: 'Generation failed. Try again.' }
                : m
            ))
            setBusy(false)
          }
        } catch (_) {}
      }, 3000)
    } catch (e) {
      setMessages(prev => prev.map(m =>
        m.id === pendingId ? { ...m, status: 'error', text: e.message } : m
      ))
      setBusy(false)
    }
  }

  function handleKey(e) {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) handleSend()
  }

  return (
    <div className={styles.layout}>
      {/* Sidebar */}
      <aside className={styles.sidebar}>
        <div className={styles.section}>
          <p className={styles.sectionLabel}>Mode</p>
          {MODES.map(m => (
            <button
              key={m.key}
              className={`${styles.modeBtn} ${mode === m.key ? styles.modeActive : ''}`}
              onClick={() => setMode(m.key)}
            >
              <span className={styles.modeIcon}>{m.icon}</span>
              <span className={styles.modeLabel}>{m.label}</span>
            </button>
          ))}
        </div>

        <div className={styles.section}>
          <p className={styles.sectionLabel}>Template</p>
          <div className={styles.templateList}>
            {currentMode?.templates.map(t => (
              <button
                key={t.id}
                className={`${styles.templateBtn} ${template === t.id ? styles.templateActive : ''}`}
                onClick={() => setTemplate(t.id)}
                title={t.description}
              >
                {t.label}
              </button>
            ))}
          </div>
        </div>

        <div className={styles.section}>
          <p className={styles.sectionLabel}>Model</p>
          {MODELS.map(m => (
            <button
              key={m.id}
              className={`${styles.modelBtn} ${modelId === m.id ? styles.modelActive : ''}`}
              onClick={() => setModelId(m.id)}
            >
              <span className={styles.modelLabel}>{m.label}</span>
              <span className={styles.modelSub}>{m.sub}</span>
            </button>
          ))}
        </div>

        <div className={styles.section}>
          <p className={styles.sectionLabel}>Aspect Ratio</p>
          <div className={styles.ratioGrid}>
            {RATIOS.map(r => (
              <button
                key={r}
                className={`${styles.ratioBtn} ${ratio === r ? styles.ratioActive : ''}`}
                onClick={() => setRatio(r)}
              >
                {r}
              </button>
            ))}
          </div>
        </div>

        <div className={styles.sidebarFooter}>
          <p className={styles.sectionLabel}>Active Account</p>
          <p className={styles.accountEmail}>{account.label || account.email}</p>
        </div>
      </aside>

      {/* Main */}
      <main className={styles.main}>
        <div className={styles.messages}>
          {messages.length === 0 && (
            <div className={styles.empty}>
              <p className={styles.emptyTitle}>Describe your diagram</p>
              <p className={styles.emptyHint}>Use "Enhance" to expand a short idea into a detailed prompt</p>
              <div className={styles.examples}>
                {(mode === 'scientific' ? [
                  'Cell membrane transport mechanisms with protein channels',
                  'Neural network deep learning architecture diagram',
                  'Photosynthesis light-dependent reactions in chloroplast',
                ] : [
                  'Software development lifecycle roadmap with milestones',
                  'Root cause analysis fishbone diagram for production issues',
                  'Clinical trial participant flow CONSORT diagram',
                ]).map(ex => (
                  <button key={ex} className={styles.exBtn} onClick={() => setInput(ex)}>{ex}</button>
                ))}
              </div>
            </div>
          )}
          {messages.map(m => (
            <MessageBubble key={m.id} msg={m} token={account.access_token} />
          ))}
          <div ref={bottomRef} />
        </div>

        <div className={styles.inputArea}>
          <textarea
            className={styles.textarea}
            rows={4}
            placeholder="Describe the diagram you want to generate…"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKey}
            disabled={busy}
          />
          <div className={styles.inputActions}>
            <button
              className={styles.btnExpand}
              onClick={handleExpand}
              disabled={!input.trim() || expanding || busy}
              title="Expand prompt with AI"
            >
              {expanding
                ? <><Spinner /> Enhancing…</>
                : <>✨ Enhance</>}
            </button>
            <span className={styles.hint}>Ctrl+Enter to send</span>
            <button
              className={styles.btnSend}
              onClick={handleSend}
              disabled={!input.trim() || busy}
            >
              {busy ? 'Generating…' : 'Generate'}
            </button>
          </div>
        </div>
      </main>
    </div>
  )
}

function Spinner() {
  return (
    <svg width="13" height="13" viewBox="0 0 16 16" fill="none" style={{ animation: 'spin 0.8s linear infinite', display:'inline-block', verticalAlign:'middle' }}>
      <style>{`@keyframes spin{to{transform:rotate(360deg)}}`}</style>
      <circle cx="8" cy="8" r="6" stroke="currentColor" strokeWidth="2" strokeDasharray="28" strokeDashoffset="10" strokeLinecap="round"/>
    </svg>
  )
}
