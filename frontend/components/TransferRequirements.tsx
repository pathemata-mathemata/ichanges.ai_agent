import { useState } from 'react';

type Course = {
  code: string;
  title: string;
  units: number | null;
};

type TransferRequirementsProps = {
  sourceInstitution: string;
  targetInstitution: string;
  targetMajor: string;
};

const TransferRequirements = ({
  sourceInstitution,
  targetInstitution,
  targetMajor,
}: TransferRequirementsProps) => {
  const [loading, setLoading] = useState(false);
  const [requirements, setRequirements] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const fetchRequirements = async () => {
    if (!sourceInstitution || !targetInstitution || !targetMajor) {
      setError('Please fill in all fields');
      return;
    }

    setLoading(true);
    setError(null);
    
    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';
      const response = await fetch(
        `${API_URL}/transfers/requirements?source_institution=${encodeURIComponent(
          sourceInstitution
        )}&target_institution=${encodeURIComponent(
          targetInstitution
        )}&major=${encodeURIComponent(targetMajor)}`
      );

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText || 'Failed to fetch transfer requirements');
      }

      const data = await response.json();
      setRequirements(data);
    } catch (err: any) {
      console.error('Error fetching transfer requirements:', err);
      setError(err.message || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mt-4">
      <button
        onClick={fetchRequirements}
        disabled={loading || !sourceInstitution || !targetInstitution || !targetMajor}
        className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loading ? 'Loading...' : 'Show Transfer Requirements'}
      </button>

      {error && (
        <div className="mt-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      )}

      {requirements && (
        <div className="mt-6">
          <h3 className="text-xl font-bold mb-2">
            Transfer Requirements
          </h3>
          <div className="flex items-center">
            <div className="text-sm">
              <p>
                <strong>From:</strong> {requirements.source_institution}
              </p>
              <p>
                <strong>To:</strong> {requirements.target_institution}
              </p>
              <p>
                <strong>Major:</strong> {requirements.major}
              </p>
            </div>
            {requirements.is_default && (
              <div className="ml-auto bg-yellow-100 text-yellow-800 px-3 py-1 rounded text-sm">
                Default Requirements
              </div>
            )}
          </div>

          {requirements.note && (
            <div className="my-3 p-3 bg-yellow-50 border border-yellow-200 text-yellow-800 rounded text-sm">
              {requirements.note}
            </div>
          )}

          {/* Required Courses */}
          {requirements.required_courses && requirements.required_courses.length > 0 && (
            <div className="mt-4">
              <h4 className="font-semibold mb-2">Required Courses</h4>
              <div className="overflow-x-auto">
                <table className="min-w-full border border-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-2 border text-left">Course Code</th>
                      <th className="px-4 py-2 border text-left">Title</th>
                      <th className="px-4 py-2 border text-left">Units</th>
                    </tr>
                  </thead>
                  <tbody>
                    {requirements.required_courses.map((course: Course, index: number) => (
                      <tr key={`req-${index}`} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                        <td className="px-4 py-2 border">{course.code}</td>
                        <td className="px-4 py-2 border">{course.title}</td>
                        <td className="px-4 py-2 border">{course.units}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Recommended Courses */}
          {requirements.recommended_courses && requirements.recommended_courses.length > 0 && (
            <div className="mt-4">
              <h4 className="font-semibold mb-2">Recommended Courses</h4>
              <div className="overflow-x-auto">
                <table className="min-w-full border border-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-2 border text-left">Course Code</th>
                      <th className="px-4 py-2 border text-left">Title</th>
                      <th className="px-4 py-2 border text-left">Units</th>
                    </tr>
                  </thead>
                  <tbody>
                    {requirements.recommended_courses.map((course: Course, index: number) => (
                      <tr key={`rec-${index}`} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                        <td className="px-4 py-2 border">{course.code}</td>
                        <td className="px-4 py-2 border">{course.title}</td>
                        <td className="px-4 py-2 border">{course.units}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {requirements.url && (
            <div className="mt-4 text-sm">
              <p>
                <strong>Source:</strong>{' '}
                {requirements.url.startsWith('http') ? (
                  <a 
                    href={requirements.url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:underline"
                  >
                    {requirements.url}
                  </a>
                ) : (
                  requirements.url
                )}
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default TransferRequirements; 