'use client'

import React from 'react'

interface WaitingOverlayProps {
  isLoading: boolean
}

export default function WaitingOverlay({ isLoading }: WaitingOverlayProps) {
  if (!isLoading) return null

  return (
    <div className="fixed inset-x-0 bottom-0 bg-black bg-opacity-75 text-white py-2 text-center z-50">
      Generating your schedule… Approx. 2s remaining
    </div>
  )
}