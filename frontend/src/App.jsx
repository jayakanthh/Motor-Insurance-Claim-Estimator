import { useState } from 'react'
import axios from 'axios'
import { useDropzone } from 'react-dropzone'
import { 
  CloudArrowUpIcon, 
  CheckCircleIcon, 
  ExclamationCircleIcon,
  CurrencyDollarIcon,
  WrenchScrewdriverIcon,
  DocumentTextIcon
} from '@heroicons/react/24/outline'

function App() {
  const [file, setFile] = useState(null)
  const [preview, setPreview] = useState(null)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [config, setConfig] = useState({
    provider: 'mock',
    apiKey: '',
    laborRate: 75
  })

  const onDrop = (acceptedFiles) => {
    const file = acceptedFiles[0]
    setFile(file)
    setPreview(URL.createObjectURL(file))
    setResult(null)
    setError(null)
  }

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png']
    },
    maxFiles: 1
  })

  const analyzeClaim = async () => {
    if (!file) return

    setLoading(true)
    setError(null)
    
    const formData = new FormData()
    formData.append('image', file)
    formData.append('provider', config.provider)
    if (config.apiKey) formData.append('api_key', config.apiKey)
    formData.append('labor_rate', config.laborRate)

    try {
      const response = await axios.post('http://localhost:8000/api/analyze-claim', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      setResult(response.data.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'An error occurred during analysis')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <header className="mb-10 text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">🚗 Instant Motor Claim Estimator</h1>
          <p className="text-lg text-gray-600">AI-Powered Damage Assessment & Cost Estimation</p>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column: Configuration & Upload */}
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
              <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <WrenchScrewdriverIcon className="h-5 w-5 text-blue-600" />
                Configuration
              </h2>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">AI Model</label>
                  <select 
                    className="w-full rounded-lg border-gray-300 border p-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    value={config.provider}
                    onChange={(e) => setConfig({...config, provider: e.target.value})}
                  >
                    <option value="mock">Mock (Demo)</option>
                    <option value="openai">GPT-4o</option>
                    <option value="gemini">Gemini 1.5 Pro</option>
                  </select>
                </div>

                {config.provider !== 'mock' && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">API Key</label>
                    <input 
                      type="password"
                      className="w-full rounded-lg border-gray-300 border p-2 focus:ring-2 focus:ring-blue-500"
                      placeholder={`Enter ${config.provider} API Key`}
                      value={config.apiKey}
                      onChange={(e) => setConfig({...config, apiKey: e.target.value})}
                    />
                  </div>
                )}

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Labor Rate ($/hr)</label>
                  <input 
                    type="number"
                    className="w-full rounded-lg border-gray-300 border p-2 focus:ring-2 focus:ring-blue-500"
                    value={config.laborRate}
                    onChange={(e) => setConfig({...config, laborRate: parseFloat(e.target.value)})}
                  />
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
              <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <CloudArrowUpIcon className="h-5 w-5 text-blue-600" />
                Upload Image
              </h2>
              
              <div 
                {...getRootProps()} 
                className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors
                  ${isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-blue-400'}`}
              >
                <input {...getInputProps()} />
                {preview ? (
                  <img src={preview} alt="Preview" className="max-h-48 mx-auto rounded-lg object-contain" />
                ) : (
                  <div className="space-y-2">
                    <CloudArrowUpIcon className="h-12 w-12 mx-auto text-gray-400" />
                    <p className="text-gray-500">Drag & drop or click to upload</p>
                    <p className="text-xs text-gray-400">JPG, PNG up to 10MB</p>
                  </div>
                )}
              </div>

              {file && (
                <button
                  onClick={analyzeClaim}
                  disabled={loading}
                  className={`w-full mt-4 py-3 px-4 rounded-lg font-medium text-white transition-colors
                    ${loading ? 'bg-blue-400 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700'}`}
                >
                  {loading ? 'Analyzing...' : 'Analyze Damage'}
                </button>
              )}
              
              {error && (
                <div className="mt-4 p-3 bg-red-50 text-red-700 rounded-lg text-sm flex items-center gap-2">
                  <ExclamationCircleIcon className="h-5 w-5" />
                  {error}
                </div>
              )}
            </div>
          </div>

          {/* Right Column: Results */}
          <div className="lg:col-span-2 space-y-6">
            {result ? (
              <>
                {/* Status Card */}
                <div className={`p-6 rounded-xl border ${
                  result.status === 'Pre-Approved' 
                    ? 'bg-green-50 border-green-200 text-green-800' 
                    : 'bg-yellow-50 border-yellow-200 text-yellow-800'
                }`}>
                  <div className="flex items-center gap-3">
                    {result.status === 'Pre-Approved' ? (
                      <CheckCircleIcon className="h-8 w-8" />
                    ) : (
                      <ExclamationCircleIcon className="h-8 w-8" />
                    )}
                    <div>
                      <h2 className="text-xl font-bold">{result.status}</h2>
                      <p className="text-sm opacity-90">
                        {result.status === 'Pre-Approved' 
                          ? 'Estimate is within automatic approval limits.' 
                          : 'Estimate exceeds threshold. Manual review required.'}
                      </p>
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Damage Assessment */}
                  <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                    <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                      <DocumentTextIcon className="h-5 w-5 text-blue-600" />
                      Damage Assessment
                    </h3>
                    <div className="space-y-3">
                      {result.damage_assessment.damages.map((damage, idx) => (
                        <div key={idx} className="p-3 bg-gray-50 rounded-lg border border-gray-100">
                          <div className="flex justify-between items-start mb-1">
                            <span className="font-medium text-gray-900 capitalize">
                              {damage.part.replace(/_/g, ' ')}
                            </span>
                            <span className={`px-2 py-0.5 text-xs rounded-full capitalize ${
                              damage.severity === 'severe' ? 'bg-red-100 text-red-700' :
                              damage.severity === 'moderate' ? 'bg-yellow-100 text-yellow-700' :
                              'bg-green-100 text-green-700'
                            }`}>
                              {damage.severity}
                            </span>
                          </div>
                          <p className="text-sm text-gray-600">{damage.description}</p>
                        </div>
                      ))}
                      {result.damage_assessment.damages.length === 0 && (
                        <p className="text-gray-500 italic">No significant damages detected.</p>
                      )}
                    </div>
                  </div>

                  {/* Cost Summary */}
                  <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                    <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                      <CurrencyDollarIcon className="h-5 w-5 text-blue-600" />
                      Cost Estimate
                    </h3>
                    
                    <div className="space-y-3 text-sm">
                      <div className="flex justify-between py-2 border-b border-gray-100">
                        <span className="text-gray-600">Parts Total</span>
                        <span className="font-medium">${result.cost_estimate.summary.total_parts_cost.toFixed(2)}</span>
                      </div>
                      <div className="flex justify-between py-2 border-b border-gray-100">
                        <span className="text-gray-600">
                          Labor ({result.cost_estimate.summary.total_labor_hours} hrs)
                        </span>
                        <span className="font-medium">${result.cost_estimate.summary.total_labor_cost.toFixed(2)}</span>
                      </div>
                      <div className="flex justify-between py-2 border-b border-gray-100">
                        <span className="text-gray-600">Tax (10%)</span>
                        <span className="font-medium">${result.cost_estimate.summary.tax.toFixed(2)}</span>
                      </div>
                      <div className="flex justify-between pt-2 text-lg font-bold text-gray-900">
                        <span>Total Estimate</span>
                        <span>${result.cost_estimate.summary.total_cost.toFixed(2)}</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Line Items Table */}
                <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
                  <div className="px-6 py-4 border-b border-gray-100">
                    <h3 className="font-semibold text-gray-900">Detailed Breakdown</h3>
                  </div>
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm text-left">
                      <thead className="bg-gray-50 text-gray-700 font-medium">
                        <tr>
                          <th className="px-6 py-3">Part</th>
                          <th className="px-6 py-3">Severity</th>
                          <th className="px-6 py-3 text-right">Part Cost</th>
                          <th className="px-6 py-3 text-right">Labor Cost</th>
                          <th className="px-6 py-3 text-right">Total</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-100">
                        {result.cost_estimate.line_items.map((item, idx) => (
                          <tr key={idx} className="hover:bg-gray-50">
                            <td className="px-6 py-3 font-medium capitalize">
                              {item.part.replace(/_/g, ' ')}
                            </td>
                            <td className="px-6 py-3 capitalize text-gray-600">{item.severity}</td>
                            <td className="px-6 py-3 text-right">${item.part_cost.toFixed(2)}</td>
                            <td className="px-6 py-3 text-right">${item.labor_cost.toFixed(2)}</td>
                            <td className="px-6 py-3 text-right font-medium">${item.total.toFixed(2)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </>
            ) : (
              <div className="h-full min-h-[400px] flex flex-col items-center justify-center bg-white rounded-xl border border-dashed border-gray-300 text-gray-400">
                <DocumentTextIcon className="h-16 w-16 mb-4 opacity-50" />
                <p className="text-lg font-medium">No analysis results yet</p>
                <p className="text-sm">Upload an image and click "Analyze Damage" to see details.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
