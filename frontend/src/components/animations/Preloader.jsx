import React, { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useNoteStore } from '../../store/noteStore'
import LogoIcon from '../layout/LogoIcon'

const STAGES = [
  { msg: 'Initializing NLP engine…',   pct: 15 },
  { msg: 'Loading BART transformer…',  pct: 35 },
  { msg: 'Calibrating spaCy pipeline…', pct: 57 },
  { msg: 'Warming LSA & TF-IDF…',      pct: 78 },
  { msg: 'Preparing your workspace…',  pct: 100 },
]

export default function Preloader() {
  const { preloaderDone, setPreloaderDone } = useNoteStore()
  const [stage, setStage] = useState(0)
  const [visible, setVisible] = useState(true)

  useEffect(() => {
    const ts = STAGES.map((_, i) => setTimeout(() => setStage(i), i * 600))
    ts.push(setTimeout(() => {
      setVisible(false)
      setTimeout(() => setPreloaderDone(true), 800)
    }, STAGES.length * 600 + 200))
    return () => ts.forEach(clearTimeout)
  }, [])

  return (
    <AnimatePresence>
      {visible && (
        <motion.div
          initial={{ opacity: 1 }}
          exit={{ opacity: 0, scale: 1.02 }}
          transition={{ duration: 0.8, ease: [0.4, 0, 0.2, 1] }}
          style={{
            position: 'fixed', inset: 0, zIndex: 9999,
            background: '#120E0B',
            display: 'flex', flexDirection: 'column',
            alignItems: 'center', justifyContent: 'center',
            overflow: 'hidden',
          }}
        >
          {/* ── Ambient background ── */}
          <div style={{ position: 'absolute', inset: 0, pointerEvents: 'none' }}>
            {/* Antique gold subtle glow */}
            <motion.div
              animate={{ scale: [1, 1.2, 1], opacity: [0.25, 0.45, 0.25] }}
              transition={{ duration: 6, repeat: Infinity, ease: 'easeInOut' }}
              style={{
                position: 'absolute', top: '50%', left: '50%',
                transform: 'translate(-50%,-50%)',
                width: 600, height: 600, borderRadius: '50%',
                background: 'radial-gradient(circle, rgba(201,161,91,0.12) 0%, transparent 65%)',
                filter: 'blur(70px)',
              }}
            />
            {/* Fine academic grid */}
            <div style={{
              position: 'absolute', inset: 0, opacity: 0.03,
              backgroundImage: `
                linear-gradient(rgba(241,229,200,0.6) 1px, transparent 1px),
                linear-gradient(90deg, rgba(241,229,200,0.6) 1px, transparent 1px)
              `,
              backgroundSize: '48px 48px',
            }}/>
          </div>

          {/* ── Center Emblem ── */}
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
            style={{
              position: 'relative',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              marginBottom: 32,
            }}
          >
            {/* Refined gold frame */}
            <div style={{
              width: 92, height: 92, borderRadius: 24,
              background: '#1C1612',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              position: 'relative',
              border: '1px solid rgba(201,161,91,0.4)',
              boxShadow: '0 8px 32px rgba(0,0,0,0.45)',
            }}>
              <div style={{
                position: 'absolute', inset: 3, borderRadius: 20,
                border: '1px solid rgba(241,229,200,0.08)',
              }}/>
              <LogoIcon size={56} />
            </div>
          </motion.div>

          {/* ── Brand ── */}
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.25, ease: [0.16, 1, 0.3, 1] }}
            style={{ textAlign: 'center', marginBottom: 44 }}
          >
            <h1 style={{
              fontFamily: "'Newsreader', Georgia, serif",
              fontSize: 48,
              fontWeight: 500,
              letterSpacing: '-0.03em',
              lineHeight: 1,
              marginBottom: 8,
              color: '#F1E5C8',
            }}>NoteBot</h1>
            <p style={{
              fontFamily: "'IBM Plex Sans', sans-serif",
              fontSize: 12,
              letterSpacing: '0.18em',
              textTransform: 'uppercase',
              color: '#C9A15B',
              fontWeight: 500,
            }}>AI Study Intelligence</p>
          </motion.div>

          {/* ── Progress ── */}
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            style={{ width: 280 }}
          >
            {/* Track */}
            <div style={{
              height: 2, borderRadius: 99, overflow: 'hidden', marginBottom: 12,
              background: 'rgba(241,229,200,0.1)',
            }}>
              <motion.div
                style={{
                  height: '100%', borderRadius: 99,
                  background: 'linear-gradient(90deg, #8C6F3B, #C9A15B, #F1E5C8)',
                }}
                animate={{ width: `${STAGES[stage].pct}%` }}
                transition={{ duration: 0.5, ease: 'easeOut' }}
              />
            </div>
            {/* Label row */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <motion.span
                key={stage}
                initial={{ opacity: 0, y: 3 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.25 }}
                style={{
                  fontFamily: "'IBM Plex Mono', monospace",
                  fontSize: 11,
                  color: 'rgba(241,229,200,0.65)',
                  letterSpacing: '0.02em',
                }}
              >
                {STAGES[stage].msg}
              </motion.span>
              <span style={{
                fontFamily: "'IBM Plex Mono', monospace",
                fontSize: 11,
                color: '#C9A15B',
                fontWeight: 600,
              }}>{STAGES[stage].pct}%</span>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
