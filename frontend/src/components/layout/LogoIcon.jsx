import React from 'react'

/**
 * NoteBot Primary Logo Icon — Design A: Refined Folio & Crown Sparkle
 * Flat vector artwork: Antique Gold (#C9A15B) & Warm Cream (#F1E5C8)
 * Transparent background, preserves aspect ratio
 */
export default function LogoIcon({ size = 28, className = '', style = {} }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 512 512"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      style={{ display: 'block', flexShrink: 0, ...style }}
      aria-label="NoteBot Logo"
    >
      {/* 4-point AI sparkle (antique gold with warm cream core) */}
      <path
        d="M 256 70 C 256 122 288 148 334 148 C 288 148 256 174 256 226 C 256 174 224 148 178 148 C 224 148 256 122 256 70 Z"
        fill="#C9A15B"
      />
      <path
        d="M 256 102 C 256 132 274 148 300 148 C 274 148 256 164 256 194 C 256 164 238 148 212 148 C 238 148 256 132 256 102 Z"
        fill="#F1E5C8"
      />

      {/* Open Book - Base Spine & Outer Binding */}
      <path
        d="M 256 384 C 208 398 148 390 80 354 V 288 C 148 322 208 330 256 318 C 304 330 364 322 432 288 V 354 C 364 390 304 398 256 384 Z"
        fill="none"
        stroke="#C9A15B"
        strokeWidth="16"
        strokeLinecap="round"
        strokeLinejoin="round"
      />

      {/* Open Book - Main Pages Spread (Warm Cream) */}
      {/* Left Page */}
      <path
        d="M 256 318 C 206 304 150 292 92 256 C 150 228 206 238 256 256"
        stroke="#F1E5C8"
        strokeWidth="16"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      {/* Right Page */}
      <path
        d="M 256 318 C 306 304 362 292 420 256 C 362 228 306 238 256 256"
        stroke="#F1E5C8"
        strokeWidth="16"
        strokeLinecap="round"
        strokeLinejoin="round"
      />

      {/* Center Spine Pillar */}
      <line
        x1="256"
        y1="256"
        x2="256"
        y2="384"
        stroke="#C9A15B"
        strokeWidth="16"
        strokeLinecap="round"
      />
    </svg>
  )
}
