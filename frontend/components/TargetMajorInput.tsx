'use client'
import { useFormContext } from 'react-hook-form'

export default function TargetMajorInput() {
  const { register } = useFormContext<{ targetMajor: string }>()
  return (
    <div>
      <label className="block text-sm font-medium">Desired Major</label>
      <input
        type="text"
        {...register('targetMajor')}
        placeholder="e.g. Computer Science"
        className="mt-1 block w-full rounded border-gray-300 px-2 py-1"
      />
    </div>
  )
}