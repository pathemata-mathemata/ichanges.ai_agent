'use client'
import { useFormContext } from 'react-hook-form'

export default function TargetInstitutionInput() {
  const { register } = useFormContext<{ targetInstitution: string }>()
  return (
    <div>
      <label className="block text-sm font-medium">Transfer-To Institution</label>
      <input
        type="text"
        {...register('targetInstitution')}
        placeholder="e.g. UC Berkeley"
        className="mt-1 block w-full rounded border-gray-300 px-2 py-1"
      />
    </div>
  )
}