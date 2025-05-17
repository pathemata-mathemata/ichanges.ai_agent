// components/OriginInstitutionInput.tsx
'use client'
import { useFormContext } from 'react-hook-form'

export default function OriginInstitutionInput() {
  const { register } = useFormContext<{ originInstitution: string }>()
  return (
    <div>
      <label className="block text-sm font-medium mb-1">Current Institution</label>
      <input
        {...register('originInstitution')}
        type="text"
        placeholder="e.g. De Anza College"
        className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-black transition"
      />
    </div>
  )
}