'use client'
import { useFormContext } from 'react-hook-form'

export default function TargetYearInput() {
  const { register } = useFormContext<{ targetYear: string }>()
  return (
    <div>
      <label className="block text-sm font-medium">Planned Transfer Year</label>
      <input
        type="text"
        {...register('targetYear')}
        placeholder="e.g. 2026"
        className="mt-1 block w-full rounded border-gray-300 px-2 py-1"
      />
    </div>
  )
}