'use client'
import { useFormContext } from 'react-hook-form'

export default function CurrentYearInput() {
  const { register } = useFormContext<{ currentYear: string }>()
  return (
    <div>
      <label className="block text-sm font-medium">Current Year</label>
      <input
        type="text"
        {...register('currentYear')}
        placeholder="e.g. 2025"
        className="mt-1 block w-full rounded border-gray-300 px-2 py-1"
      />
    </div>
  )
}