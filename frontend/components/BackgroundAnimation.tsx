'use client'

import { useRef, useEffect } from 'react'
import * as THREE from 'three'
import NET from 'vanta/dist/vanta.net.min'

export default function BackgroundAnimation() {
  const containerRef = useRef<HTMLDivElement>(null)
  const vantaRef = useRef<any>(null)

  useEffect(() => {
    // Only run in the browser
    if (typeof window === 'undefined' || !containerRef.current) return

    // Test for WebGL support
    const canvas = document.createElement('canvas')
    const gl =
      (canvas.getContext('webgl') ||
       canvas.getContext('experimental-webgl'))
    if (!gl) {
      console.warn('WebGL not supported — skipping background animation')
      return
    }

    // Try to initialize Vanta
    try {
      vantaRef.current = NET({
        el: containerRef.current,
        THREE,
        mouseControls: true,
        touchControls: true,
        backgroundAlpha: 0,
        color: 0x20232a,
        scale: 1.0,
        scaleMobile: 1.0,
      })
    } catch (err) {
      console.warn('Vanta initialization failed:', err)
    }

    // Cleanup on unmount
    return () => {
      if (vantaRef.current && typeof vantaRef.current.destroy === 'function') {
        vantaRef.current.destroy()
      }
    }
  }, [])

  // Fixed full-screen container behind everything
  return (
    <div
      ref={containerRef}
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100vw',
        height: '100vh',
        zIndex: -1,
        pointerEvents: 'none',
      }}
    />
  )
}