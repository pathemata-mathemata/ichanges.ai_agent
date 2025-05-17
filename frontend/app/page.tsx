// app/page.tsx
'use client'

import { useState } from 'react'
import { useForm, FormProvider } from 'react-hook-form'
import CourseInput            from '../components/CourseInput'
import OriginInstitutionInput from '../components/OriginInstitutionInput'
import TargetInstitutionInput from '../components/TargetInstitutionInput'
import TargetMajorInput       from '../components/TargetMajorInput'
import TargetYearInput        from '../components/TargetYearInput'
import WaitingOverlay         from '../components/WaitingOverlay'
import ChatBoxPlaceholder     from '../components/ChatBoxPlaceholder'

type FormValues = {
  courses:                string
  originInstitution:      string
  academicYear:           string
  currentGPA:             string
  desiredUnitsPerQuarter: string
  targetInstitution:      string
  targetMajor:            string
  targetYear:             string
}

export default function Page() {
  const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

  const methods = useForm<FormValues>({
    defaultValues: {
      courses:               '',
      originInstitution:     '',
      academicYear:          '',
      currentGPA:            '',
      desiredUnitsPerQuarter:'',
      targetInstitution:     '',
      targetMajor:           '',
      targetYear:            '',
    },
  })
  const { handleSubmit, register } = methods

  const [loading, setLoading] = useState(false)
  const [result,  setResult]  = useState<any>(null)
  const [error,   setError]   = useState<string | null>(null)

  const onSubmit = async (vals: FormValues) => {
    setLoading(true)
    setError(null)
    setResult(null)

    const payload = {
      completed_courses:         vals.courses.split(',').map(s => s.trim()),
      origin_institution:        vals.originInstitution.trim(),
      academic_year:             vals.academicYear,
      current_gpa:               parseFloat(vals.currentGPA),
      desired_units_per_quarter: parseInt(vals.desiredUnitsPerQuarter, 10),
      target_institution:        vals.targetInstitution.trim(),
      target_major:              vals.targetMajor.trim(),
      target_year:               vals.targetYear.trim(),
    }

    try {
      const res = await fetch(`${API_URL}/sonar/schedule`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
      if (!res.ok) {
        const text = await res.text()
        throw new Error(text || 'Unknown error')
      }
      setResult(await res.json())
    } catch (err: any) {
      console.error(err)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <div className="flex justify-center px-4">
        <div style={{ width: '100%', maxWidth: 400 }}>
          <FormProvider {...methods}>
            <form
              onSubmit={handleSubmit(onSubmit)}
              style={{
                backgroundColor: '#fff',
                padding: '2rem',
                borderRadius: '1rem',
                boxShadow: '0 10px 15px rgba(0,0,0,0.1)',
              }}
            >
              <h2 className="text-center text-2xl font-bold mb-6">
                Next-Quarter Scheduler
              </h2>

              <CourseInput {...register('courses', { required: true })}/>
              <OriginInstitutionInput {...register('originInstitution', { required: true })}/>

              <div className="mb-4">
                <label className="block mb-1 font-medium">
                  Which quarter are you planning?
                </label>
                <select
                  {...register('academicYear', { required: true })}
                  className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-black"
                  defaultValue=""
                >
                  <option value="" disabled>Select a quarter…</option>
                  <option>Winter 2025</option>
                  <option>Spring 2025</option>
                  <option>Summer 2025</option>
                  <option>Fall 2025</option>
                </select>
              </div>

              <div className="mb-4">
                <label className="block mb-1 font-medium">Current GPA</label>
                <input
                  {...register('currentGPA', { required: true })}
                  type="number" step="0.01" min="0" max="4"
                  placeholder="e.g. 3.75"
                  className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-black"
                />
              </div>

              <div className="mb-4">
                <label className="block mb-1 font-medium">
                  Desired Units/Quarter
                </label>
                <input
                  {...register('desiredUnitsPerQuarter', { required: true })}
                  type="number" min="1" max="25"
                  placeholder="e.g. 15"
                  className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-black"
                />
              </div>

              <TargetInstitutionInput {...register('targetInstitution', { required: true })}/>
              <TargetMajorInput       {...register('targetMajor',       { required: true })}/>
              <TargetYearInput        {...register('targetYear',        { required: true })}/>

              <div className="text-center mt-6">
                <button
                  type="submit"
                  disabled={loading}
                  className="bg-gradient-to-r from-blue-500 to-indigo-500 text-white font-semibold px-6 py-2 rounded-lg disabled:opacity-50"
                >
                  {loading ? 'Scheduling…' : 'Generate Schedule'}
                </button>
              </div>
            </form>
          </FormProvider>

          {error && <p className="text-red-600 text-center mt-4">{error}</p>}
        </div>
      </div>

      {/* table-card sits below the form-card */}
      {result?.schedule && (
        <div className="flex justify-center px-4 mt-8">
          <div
            style={{
              backgroundColor: '#fff',
              padding: '2rem',
              borderRadius: '1rem',
              boxShadow: '0 10px 15px rgba(0,0,0,0.1)',
              width: '100%',
              maxWidth: 400,
            }}
          >
            <table className="min-w-full border border-gray-200 border-collapse">
              <thead className="bg-gray-100">
                <tr>
                  {['Term','Course Code','Title','Units'].map(h => (
                    <th
                      key={h}
                      className="px-4 py-2 border border-gray-200 text-left font-medium"
                    >
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {result.schedule.map((entry: any) =>
                  entry.courses.map((course: any, idx: number) => (
                    <tr key={`${entry.term}-${course.code}-${idx}`}>
                      <td className="px-4 py-2 border border-gray-200">{entry.term}</td>
                      <td className="px-4 py-2 border border-gray-200">{course.code}</td>
                      <td className="px-4 py-2 border border-gray-200">{course.title}</td>
                      <td className="px-4 py-2 border border-gray-200">{course.units}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>

            <div className="mt-4">
              <ChatBoxPlaceholder />
            </div>
          </div>
        </div>
      )}

      <WaitingOverlay isLoading={loading} />
    </>
  )
}