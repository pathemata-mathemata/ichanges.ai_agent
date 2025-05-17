'use client'

import { useFormContext } from 'react-hook-form'

const QUARTERS = [
  'Winter 2025',
  'Spring 2025',
  'Summer 2025',
  'Fall 2025',
  'Winter 2026',
  'Spring 2026',
  'Summer 2026',
  'Fall 2026',
]

export default function QuarterPlanSelect() {
  const { register } = useFormContext<{ quarterToPlan: string }>()

  return (
    <div>
      <label className="block text-sm font-medium mb-1">
        Which quarter are you planning?
      </label>
      <select
        {...register('quarterToPlan', { required: true })}
        className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-black transition"
        defaultValue=""
      >
        <option value="" disabled>
          Select a quarter…
        </option>
        {QUARTERS.map(q => (
          <option key={q} value={q}>
            {q}
          </option>
        ))}
      </select>
    </div>
  )
}