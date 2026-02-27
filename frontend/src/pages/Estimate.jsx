import { useState, useCallback } from 'react';
import axios from 'axios';
import { useDropzone } from 'react-dropzone';
import { 
  CloudArrowUpIcon, 
  CheckCircleIcon, 
  ExclamationCircleIcon,
  CurrencyDollarIcon,
  WrenchScrewdriverIcon,
  DocumentTextIcon,
  ArrowPathIcon,
  PhotoIcon,
  PlusIcon,
  XMarkIcon
} from '@heroicons/react/24/outline';
import { Link } from 'react-router-dom';

export default function Estimate() {
  const [files, setFiles] = useState({
    front: null,
    back: null,
    left: null,
    right: null,
    extras: []
  });
  const [previews, setPreviews] = useState({
    front: null,
    back: null,
    left: null,
    right: null,
    extras: []
  });
  
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [config, setConfig] = useState({
    provider: 'mock',
    apiKey: '',
    laborRate: 75
  });

  const onDrop = useCallback((acceptedFiles, type) => {
    const file = acceptedFiles[0];
    if (!file) return;

    if (type === 'extras') {
      setFiles(prev => ({ ...prev, extras: [...prev.extras, ...acceptedFiles] }));
      const newPreviews = acceptedFiles.map(f => URL.createObjectURL(f));
      setPreviews(prev => ({ ...prev, extras: [...prev.extras, ...newPreviews] }));
    } else {
      setFiles(prev => ({ ...prev, [type]: file }));
      setPreviews(prev => ({ ...prev, [type]: URL.createObjectURL(file) }));
    }
    
    // Reset results on new upload
    setResult(null);
    setError(null);
  }, []);

  const removeExtra = (index) => {
    setFiles(prev => ({ ...prev, extras: prev.extras.filter((_, i) => i !== index) }));
    setPreviews(prev => ({ ...prev, extras: prev.extras.filter((_, i) => i !== index) }));
  };

  const analyzeClaim = async () => {
    if (!files.front || !files.back || !files.left || !files.right) {
      setError("Please upload all 4 required angles (Front, Back, Left, Right) before analyzing.");
      return;
    }

    setLoading(true);
    setError(null);
    
    const formData = new FormData();
    formData.append('front', files.front);
    formData.append('back', files.back);
    formData.append('left', files.left);
    formData.append('right', files.right);
    
    files.extras.forEach(file => {
      formData.append('extra', file);
    });

    formData.append('provider', config.provider);
    if (config.apiKey) formData.append('api_key', config.apiKey);
    formData.append('labor_rate', config.laborRate);

    try {
      const response = await axios.post('http://localhost:8000/api/analyze-claim', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      setResult(response.data.data);
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || 'An error occurred during analysis. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const UploadBox = ({ type, label, icon: Icon, required = false }) => {
    const { getRootProps, getInputProps, isDragActive } = useDropzone({
      onDrop: (files) => onDrop(files, type),
      accept: { 'image/*': ['.jpeg', '.jpg', '.png'] },
      maxFiles: type === 'extras' ? 10 : 1,
      multiple: type === 'extras'
    });

    const hasFile = type === 'extras' ? files.extras.length > 0 : !!files[type];
    const previewUrl = type === 'extras' ? null : previews[type];

    return (
      <div className={`relative group ${type === 'extras' ? 'col-span-full' : ''}`}>
        <label className="block text-sm font-semibold text-gray-700 mb-2">
          {label} {required && <span className="text-red-500">*</span>}
        </label>
        
        <div 
          {...getRootProps()} 
          className={`
            border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition-all h-48 flex flex-col items-center justify-center relative overflow-hidden
            ${isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50'}
            ${hasFile && type !== 'extras' ? 'border-green-500 bg-green-50' : ''}
          `}
        >
          <input {...getInputProps()} />
          
          {previewUrl ? (
            <img src={previewUrl} alt={label} className="absolute inset-0 w-full h-full object-cover opacity-80 group-hover:opacity-100 transition-opacity" />
          ) : (
            <div className="space-y-2 z-10">
              <Icon className={`h-10 w-10 mx-auto ${hasFile ? 'text-green-500' : 'text-gray-400'}`} />
              <p className="text-sm text-gray-500 font-medium">
                {isDragActive ? 'Drop here' : 'Click or drag'}
              </p>
            </div>
          )}
          
          {hasFile && type !== 'extras' && (
            <div className="absolute top-2 right-2 bg-white rounded-full p-1 shadow-md">
              <CheckCircleIcon className="h-5 w-5 text-green-600" />
            </div>
          )}
        </div>

        {/* Extra Photos Preview Grid */}
        {type === 'extras' && files.extras.length > 0 && (
          <div className="mt-4 grid grid-cols-4 sm:grid-cols-6 gap-2">
            {previews.extras.map((url, idx) => (
              <div key={idx} className="relative aspect-square rounded-lg overflow-hidden group/item">
                <img src={url} alt={`Extra ${idx}`} className="w-full h-full object-cover" />
                <button 
                  onClick={(e) => { e.stopPropagation(); removeExtra(idx); }}
                  className="absolute top-1 right-1 bg-red-500 text-white rounded-full p-0.5 opacity-0 group-hover/item:opacity-100 transition-opacity"
                >
                  <XMarkIcon className="h-3 w-3" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2 font-bold text-xl text-gray-900">
            <div className="bg-blue-600 p-1.5 rounded-lg">
              <DocumentTextIcon className="h-5 w-5 text-white" />
            </div>
            ClaimEstimator AI
          </Link>
          <div className="text-sm text-gray-500">
            New Estimation
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid lg:grid-cols-3 gap-8">
          
          {/* Left Column: Input Form */}
          <div className="lg:col-span-1 space-y-6">
            
            {/* Configuration Card */}
            <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
              <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <WrenchScrewdriverIcon className="h-5 w-5 text-blue-600" />
                Configuration
              </h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">AI Provider</label>
                  <select 
                    className="w-full rounded-lg border-gray-300 border p-2.5 bg-gray-50 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-shadow"
                    value={config.provider}
                    onChange={(e) => setConfig({...config, provider: e.target.value})}
                  >
                    <option value="mock">Mock (Demo Mode)</option>
                    <option value="openai">OpenAI GPT-4o</option>
                    <option value="gemini">Gemini 1.5 Pro</option>
                  </select>
                </div>

                {config.provider !== 'mock' && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">API Key</label>
                    <input 
                      type="password"
                      className="w-full rounded-lg border-gray-300 border p-2.5 focus:ring-2 focus:ring-blue-500"
                      placeholder={`Enter ${config.provider} API Key`}
                      value={config.apiKey}
                      onChange={(e) => setConfig({...config, apiKey: e.target.value})}
                    />
                  </div>
                )}
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Labor Rate ($/hr)</label>
                  <div className="relative">
                    <span className="absolute left-3 top-2.5 text-gray-500">$</span>
                    <input 
                      type="number"
                      className="w-full rounded-lg border-gray-300 border p-2.5 pl-7 focus:ring-2 focus:ring-blue-500"
                      value={config.laborRate}
                      onChange={(e) => setConfig({...config, laborRate: parseFloat(e.target.value)})}
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* Upload Instructions */}
            <div className="bg-blue-50 p-6 rounded-2xl border border-blue-100">
              <h3 className="text-blue-900 font-semibold mb-2 flex items-center gap-2">
                <PhotoIcon className="h-5 w-5" />
                Photo Guidelines
              </h3>
              <ul className="text-sm text-blue-800 space-y-2 list-disc pl-4">
                <li>Ensure good lighting and clear focus.</li>
                <li>Capture the entire vehicle from 4 angles.</li>
                <li>Add close-ups of specific damage in "Extra Photos".</li>
                <li>Avoid blurry or extremely dark images.</li>
              </ul>
            </div>
          </div>

          {/* Middle/Right Column: Upload Grid & Results */}
          <div className="lg:col-span-2 space-y-8">
            
            {/* Upload Grid */}
            <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100">
              <h2 className="text-xl font-bold text-gray-900 mb-6">Vehicle Photos</h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                <UploadBox type="front" label="Front View" icon={PhotoIcon} required />
                <UploadBox type="back" label="Back View" icon={PhotoIcon} required />
                <UploadBox type="left" label="Left Side" icon={PhotoIcon} required />
                <UploadBox type="right" label="Right Side" icon={PhotoIcon} required />
                
                <UploadBox type="extras" label="Extra Photos (Optional close-ups)" icon={PlusIcon} />
              </div>

              <div className="flex flex-col items-center">
                {error && (
                  <div className="mb-4 p-4 bg-red-50 text-red-700 rounded-xl text-sm flex items-center gap-2 w-full border border-red-100">
                    <ExclamationCircleIcon className="h-5 w-5 flex-shrink-0" />
                    {error}
                  </div>
                )}
                
                <button
                  onClick={analyzeClaim}
                  disabled={loading}
                  className={`
                    w-full md:w-auto min-w-[200px] py-4 px-8 rounded-xl font-bold text-lg shadow-lg transition-all flex items-center justify-center gap-2
                    ${loading 
                      ? 'bg-gray-100 text-gray-400 cursor-not-allowed shadow-none' 
                      : 'bg-blue-600 text-white hover:bg-blue-700 hover:shadow-blue-200 hover:-translate-y-0.5'}
                  `}
                >
                  {loading ? (
                    <>
                      <ArrowPathIcon className="h-5 w-5 animate-spin" />
                      Analyzing Damage...
                    </>
                  ) : (
                    <>
                      Generate Estimate
                      <CurrencyDollarIcon className="h-5 w-5" />
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Results Section */}
            {result && (
              <div className="animate-fade-in space-y-6">
                {/* Status Banner */}
                <div className={`p-6 rounded-2xl border ${
                  result.status === 'Pre-Approved' 
                    ? 'bg-green-50 border-green-200 text-green-800' 
                    : 'bg-yellow-50 border-yellow-200 text-yellow-800'
                }`}>
                  <div className="flex items-start md:items-center gap-4">
                    <div className={`p-3 rounded-full ${
                      result.status === 'Pre-Approved' ? 'bg-green-100' : 'bg-yellow-100'
                    }`}>
                      {result.status === 'Pre-Approved' ? (
                        <CheckCircleIcon className="h-8 w-8" />
                      ) : (
                        <ExclamationCircleIcon className="h-8 w-8" />
                      )}
                    </div>
                    <div>
                      <h2 className="text-2xl font-bold">{result.status}</h2>
                      <p className="opacity-90 mt-1">
                        {result.status === 'Pre-Approved' 
                          ? 'This estimate falls within automatic approval limits. Instant payout available.' 
                          : 'This estimate requires manual review by an adjuster due to high value or complexity.'}
                      </p>
                    </div>
                  </div>
                </div>

                <div className="grid md:grid-cols-2 gap-6">
                  {/* Damage List */}
                  <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
                    <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                      <DocumentTextIcon className="h-5 w-5 text-blue-600" />
                      Identified Damages
                    </h3>
                    <div className="space-y-3 max-h-[400px] overflow-y-auto pr-2 custom-scrollbar">
                      {result.damage_assessment.damages.map((damage, idx) => (
                        <div key={idx} className="p-4 bg-gray-50 rounded-xl border border-gray-100 hover:border-blue-200 transition-colors">
                          <div className="flex justify-between items-start mb-2">
                            <span className="font-bold text-gray-900 capitalize">
                              {damage.part.replace(/_/g, ' ')}
                            </span>
                            <span className={`px-2.5 py-1 text-xs font-bold rounded-full capitalize ${
                              damage.severity === 'severe' ? 'bg-red-100 text-red-700' :
                              damage.severity === 'moderate' ? 'bg-orange-100 text-orange-700' :
                              'bg-green-100 text-green-700'
                            }`}>
                              {damage.severity}
                            </span>
                          </div>
                          <p className="text-sm text-gray-600 leading-relaxed">{damage.description}</p>
                        </div>
                      ))}
                      {result.damage_assessment.damages.length === 0 && (
                        <p className="text-gray-500 italic text-center py-8">No significant damages detected.</p>
                      )}
                    </div>
                  </div>

                  {/* Cost Breakdown */}
                  <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
                    <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                      <CurrencyDollarIcon className="h-5 w-5 text-blue-600" />
                      Cost Summary
                    </h3>
                    
                    <div className="space-y-4">
                      <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                        <span className="text-gray-600">Parts Total</span>
                        <span className="font-semibold text-gray-900">${result.cost_estimate.summary.total_parts_cost.toFixed(2)}</span>
                      </div>
                      <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                        <span className="text-gray-600">
                          Labor ({result.cost_estimate.summary.total_labor_hours} hrs)
                        </span>
                        <span className="font-semibold text-gray-900">${result.cost_estimate.summary.total_labor_cost.toFixed(2)}</span>
                      </div>
                      <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                        <span className="text-gray-600">Tax (10%)</span>
                        <span className="font-semibold text-gray-900">${result.cost_estimate.summary.tax.toFixed(2)}</span>
                      </div>
                      
                      <div className="pt-4 mt-4 border-t border-gray-100">
                        <div className="flex justify-between items-end">
                          <span className="text-gray-500 font-medium">Grand Total</span>
                          <span className="text-3xl font-bold text-blue-600">
                            ${result.cost_estimate.summary.total_cost.toFixed(2)}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Line Items Table */}
                <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
                  <div className="px-6 py-5 border-b border-gray-100 bg-gray-50/50">
                    <h3 className="font-bold text-gray-900">Detailed Line Items</h3>
                  </div>
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm text-left">
                      <thead className="bg-gray-50 text-gray-700 font-semibold uppercase text-xs tracking-wider">
                        <tr>
                          <th className="px-6 py-4">Part</th>
                          <th className="px-6 py-4">Severity</th>
                          <th className="px-6 py-4 text-right">Part Cost</th>
                          <th className="px-6 py-4 text-right">Labor</th>
                          <th className="px-6 py-4 text-right">Total</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-100">
                        {result.cost_estimate.line_items.map((item, idx) => (
                          <tr key={idx} className="hover:bg-blue-50/30 transition-colors">
                            <td className="px-6 py-4 font-medium capitalize text-gray-900">
                              {item.part.replace(/_/g, ' ')}
                            </td>
                            <td className="px-6 py-4">
                              <span className={`px-2 py-1 rounded text-xs font-semibold capitalize ${
                                item.severity === 'severe' ? 'bg-red-50 text-red-700' :
                                item.severity === 'moderate' ? 'bg-orange-50 text-orange-700' :
                                'bg-green-50 text-green-700'
                              }`}>
                                {item.severity}
                              </span>
                            </td>
                            <td className="px-6 py-4 text-right text-gray-600">${item.part_cost.toFixed(2)}</td>
                            <td className="px-6 py-4 text-right text-gray-600">${item.labor_cost.toFixed(2)}</td>
                            <td className="px-6 py-4 text-right font-bold text-gray-900">${item.total.toFixed(2)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
