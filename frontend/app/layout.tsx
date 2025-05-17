// app/layout.tsx
import React from 'react'
import BackgroundAnimation from '../components/BackgroundAnimation'
import './globals.css'   // if you’re using Tailwind or global CSS

export const metadata = {
  title: 'AI Agent Club',
  description: 'Auto-schedule your next quarter classes with AI Agent Club',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <head />
      <body
        suppressHydrationWarning
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          minHeight: '100vh',
          margin: 0,
          backgroundColor: '#f3f4f6',  // gray-100
          overflowX: 'hidden',
          position: 'relative',
        }}
      >
        {/* Animated background */}
        <BackgroundAnimation />

        {/* Header */}
        <header
          style={{
            width: '100%',
            backgroundColor: 'rgba(255,255,255,0.9)',
            backdropFilter: 'blur(4px)',
            boxShadow: '0 1px 2px rgba(0,0,0,0.1)',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            padding: '1rem 0',
            zIndex: 10,
          }}
        >
          <h1 style={{ margin: 0, fontSize: '2.25rem', fontWeight: 800 }}>
            AI Agent Club
          </h1>
        </header>

        {/* Main (centers the page content) */}
        <main
          style={{
            flex: 1,
            display: 'flex',
            justifyContent: 'center',
            width: '100%',
            maxWidth: '768px',
            padding: '2rem 1rem',
            boxSizing: 'border-box',
          }}
        >
          {children}
        </main>

        {/* Footer */}
        <footer
          style={{
            width: '100%',
            backgroundColor: 'rgba(255,255,255,0.9)',
            textAlign: 'center',
            padding: '0.5rem 0',
            fontSize: '0.875rem',
            color: '#6b7280', // gray-500
          }}
        >
          &copy; {new Date().getFullYear()}
        </footer>
      </body>
    </html>
  )
}