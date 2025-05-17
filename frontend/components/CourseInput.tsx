// CourseInput.tsx
'use client'
import { useFormContext } from 'react-hook-form'

export default function CourseInput() {
  const { register } = useFormContext<{ courses: string }>()
  return (
    <div>
      <label className="block text-sm font-medium">Completed Courses</label>
      <input
        type="text"
        {...register('courses')}
        placeholder="e.g. CS101, MATH20"
        className="mt-1 block w-full rounded border-gray-300 px-2 py-1"
      />
    </div>
  )
}