import { useState, useCallback, useEffect } from 'react';
import axios from 'axios';
import { useDropzone } from 'react-dropzone';
import { motion } from 'framer-motion';
import { 
  CheckCircleIcon, 
  ExclamationCircleIcon,
  CurrencyDollarIcon,
  WrenchScrewdriverIcon,
  DocumentTextIcon,
  ArrowPathIcon,
  PhotoIcon,
  PlusIcon,
  XMarkIcon,
  TruckIcon,
  MoonIcon,
  SunIcon
} from '@heroicons/react/24/outline';
import { Link } from 'react-router-dom';

export default function Estimate() {
  const envApiBaseUrl = (import.meta.env.VITE_API_BASE_URL || '').trim();
  const inferredProdBase =
    (typeof window !== 'undefined' && /\.vercel\.app$/.test(window.location.hostname))
      ? 'https://backend-swart-rho-74.vercel.app'
      : '';
  const API_BASE_URL = (envApiBaseUrl || inferredProdBase)
    ? (envApiBaseUrl || inferredProdBase).replace(/\/$/, '')
    : (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
      ? `${window.location.protocol}//${window.location.hostname}:8000`
      : '';
  const [isDark, setIsDark] = useState(document.documentElement.classList.contains('dark'));

  const toggleTheme = () => {
    const next = !document.documentElement.classList.contains('dark');
    document.documentElement.classList.toggle('dark', next);
    localStorage.setItem('theme', next ? 'dark' : 'light');
    setIsDark(next);
  };

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
  const [apiKeyInvalid, setApiKeyInvalid] = useState(false);
  const [rememberApiKey, setRememberApiKey] = useState(false);
  const [config, setConfig] = useState({
    provider: 'mock',
    apiKey: '',
    registrationNumber: '',
    laborRate: 500
  });

  const providerRequiresKey = config.provider === 'openai' || config.provider === 'gemini';
  const providerUsesApiKeyField = providerRequiresKey;
  const cookieNameForProvider = (provider) => {
    if (provider === 'openai') return 'auto_audit_openai_api_key';
    if (provider === 'gemini') return 'auto_audit_gemini_api_key';
    return null;
  };

  const getCookie = (name) => {
    const all = document.cookie ? document.cookie.split('; ') : [];
    for (const entry of all) {
      const idx = entry.indexOf('=');
      if (idx === -1) continue;
      const k = entry.slice(0, idx);
      if (k === name) {
        return decodeURIComponent(entry.slice(idx + 1));
      }
    }
    return '';
  };

  const setCookie = (name, value, days) => {
    const maxAge = Math.floor((days ?? 30) * 24 * 60 * 60);
    document.cookie = `${name}=${encodeURIComponent(value)}; Max-Age=${maxAge}; Path=/; SameSite=Lax`;
  };

  const deleteCookie = (name) => {
    document.cookie = `${name}=; Max-Age=0; Path=/; SameSite=Lax`;
  };

  const normalizeApiError = (err) => {
    const status = err?.response?.status;
    const detail = err?.response?.data?.detail;

    if (detail && typeof detail === 'object') {
      return {
        status,
        message: detail.message || 'Request failed. Please try again.',
        errorType: detail.error_type || null,
      };
    }

    if (typeof detail === 'string' && detail.trim()) {
      return { status, message: detail, errorType: null };
    }

    if (typeof err?.message === 'string' && err.message.trim()) {
      return { status, message: err.message, errorType: null };
    }

    return { status, message: 'Request failed. Please try again.', errorType: null };
  };
  const [availableProviders, setAvailableProviders] = useState([
    { id: 'mock', name: 'Mock (Demo Mode)' },
    { id: 'openai', name: 'OpenAI GPT-4o' },
    { id: 'gemini', name: 'Gemini 1.5 Pro' }
  ]);
  const [providersLoading, setProvidersLoading] = useState(false);
  const [providersError, setProvidersError] = useState(null);
  const [backendHealth, setBackendHealth] = useState({ status: 'checking', message: '' });

  useEffect(() => {
    const checkHealth = async () => {
      setBackendHealth({ status: 'checking', message: '' });
      try {
        await axios.get(`${API_BASE_URL}/api/health`, { timeout: 2500 });
        setBackendHealth({ status: 'up', message: '' });
      } catch (err) {
        const parsed = normalizeApiError(err);
        setBackendHealth({ status: 'down', message: parsed?.message || 'Not reachable' });
      }
    };
    checkHealth();
  }, [API_BASE_URL]);

  // Fetch available providers on mount
  useEffect(() => {
    const fetchProviders = async () => {
      setProvidersLoading(true);
      setProvidersError(null);
      try {
        const response = await axios.get(`${API_BASE_URL}/api/providers`, { timeout: 2500 });
        if (response.data.providers) {
          setAvailableProviders(response.data.providers);
        }
      } catch (err) {
        console.error("Failed to fetch providers:", err);
        setProvidersError('Could not load providers. Backend may be offline.');
      } finally {
        setProvidersLoading(false);
      }
    };
    fetchProviders();
  }, [API_BASE_URL]);

  useEffect(() => {
    setApiKeyInvalid(false);
    if (!providerUsesApiKeyField) {
      setRememberApiKey(false);
      return;
    }

    const cookieName = cookieNameForProvider(config.provider);
    if (!cookieName) return;
    const saved = getCookie(cookieName);
    if (saved) {
      setConfig((prev) => ({ ...prev, apiKey: prev.apiKey || saved }));
      setRememberApiKey(true);
    } else {
      setRememberApiKey(false);
    }
  }, [config.provider, providerUsesApiKeyField]);

  const resetEstimation = () => {
    setFiles({ front: null, back: null, left: null, right: null, extras: [] });
    setPreviews({ front: null, back: null, left: null, right: null, extras: [] });
    setResult(null);
    setError(null);
    setApiKeyInvalid(false);
    setConfig(prev => ({ ...prev, apiKey: rememberApiKey ? prev.apiKey : '', registrationNumber: '', laborRate: 500 }));
  };

  const exportPdf = async () => {
    if (!result) return;
    try {
      const response = await axios.post(`${API_BASE_URL}/api/export-pdf`, { report: result }, {
        responseType: 'blob',
        timeout: 15000
      });
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `estimate-${(result?.damage_assessment?.registration_number || 'unknown').replace(/\W+/g, '')}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error(err);
      const parsed = normalizeApiError(err);
      setError(parsed.message || 'Failed to export PDF. Please try again.');
    }
  };

  const formatCurrency = (amount) => {
    if (amount === undefined || amount === null || Number.isNaN(amount)) return '₹0.00';
    try {
      return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        maximumFractionDigits: 2
      }).format(amount);
    } catch (e) {
      console.error("Currency format error:", e);
      return '₹0.00';
    }
  };

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

    if (providerRequiresKey && !config.apiKey) {
      setApiKeyInvalid(true);
      setError('API key is required for the selected provider.');
      return;
    }

    setApiKeyInvalid(false);

    setLoading(true);
    setError(null);
    
    // Helper to compress images client-side for faster/safer uploads on Vercel
    const compressImage = async (file, { maxDim = 1600, quality = 0.75 } = {}) => {
      try {
        if (!file || !(file instanceof Blob)) return file;
        // Skip compression for very small files
        if (file.size <= 300 * 1024) return file;
        const createImage = (src) =>
          new Promise((resolve, reject) => {
            const img = new Image();
            img.onload = () => resolve(img);
            img.onerror = reject;
            img.src = src;
          });
        const src = URL.createObjectURL(file);
        const img = await createImage(src);
        URL.revokeObjectURL(src);
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        const { naturalWidth: w, naturalHeight: h } = img;
        const scale = Math.min(1, maxDim / Math.max(w, h));
        const tw = Math.max(1, Math.round(w * scale));
        const th = Math.max(1, Math.round(h * scale));
        canvas.width = tw;
        canvas.height = th;
        ctx.drawImage(img, 0, 0, tw, th);
        const blob = await new Promise((resolve) =>
          canvas.toBlob(
            (b) => resolve(b || file),
            'image/jpeg',
            quality
          )
        );
        return blob || file;
      } catch {
        return file;
      }
    };

    const formData = new FormData();
    // Compress required images
    const [cFront, cBack, cLeft, cRight] = await Promise.all([
      compressImage(files.front),
      compressImage(files.back),
      compressImage(files.left),
      compressImage(files.right),
    ]);
    formData.append('front', new File([cFront], files.front.name, { type: 'image/jpeg' }));
    formData.append('back', new File([cBack], files.back.name, { type: 'image/jpeg' }));
    formData.append('left', new File([cLeft], files.left.name, { type: 'image/jpeg' }));
    formData.append('right', new File([cRight], files.right.name, { type: 'image/jpeg' }));
    
    // Compress extras (limit to 6 to keep payload small)
    const extraFiles = files.extras.slice(0, 6);
    for (const f of extraFiles) {
      const c = await compressImage(f);
      formData.append('extra', new File([c], f.name, { type: 'image/jpeg' }));
    }

    formData.append('provider', config.provider);
    if (config.apiKey) formData.append('api_key', config.apiKey);
    if (config.registrationNumber) formData.append('registration_number', config.registrationNumber);
    formData.append('labor_rate', config.laborRate);

    try {
      const response = await axios.post(`${API_BASE_URL}/api/analyze-claim`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        timeout: 120000
      });
      setResult(response.data.data);
    } catch (err) {
      console.error(err);
      const parsed = normalizeApiError(err);
      if (err?.response?.status === 413) {
        setError('Images are too large for the server. Please upload smaller photos or let us compress them automatically.');
      } else if (parsed?.message) {
        setError(parsed.message);
      } else {
        setError('An error occurred during analysis. Please try again.');
      }
      if (parsed.status === 401 || parsed.errorType === 'invalid_api_key') {
        setApiKeyInvalid(true);
      }
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
        <label className="block text-sm font-semibold text-gray-700 dark:text-slate-300 mb-2">
          {label} {required && <span className="text-red-500">*</span>}
        </label>
        
        <div 
          {...getRootProps()} 
          className={`
            border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition-all h-48 flex flex-col items-center justify-center relative overflow-hidden
            ${isDragActive ? 'border-blue-500 bg-blue-50 dark:bg-slate-900/60' : 'border-gray-300 dark:border-slate-700 hover:border-blue-400 hover:bg-gray-50 dark:hover:bg-slate-900/50'}
            ${hasFile && type !== 'extras' ? 'border-green-500 bg-green-50 dark:bg-slate-900/40' : ''}
          `}
        >
          <input {...getInputProps()} />
          
          {previewUrl ? (
            <img src={previewUrl} alt={label} className="absolute inset-0 w-full h-full object-cover opacity-80 group-hover:opacity-100 transition-opacity" />
          ) : (
            <div className="space-y-2 z-10">
              <Icon className={`h-10 w-10 mx-auto ${hasFile ? 'text-green-500' : 'text-gray-400'}`} />
              <p className="text-sm text-gray-500 dark:text-slate-300 font-medium">
                {isDragActive ? 'Drop here' : 'Click or drag'}
              </p>
            </div>
          )}
          
          {hasFile && type !== 'extras' && (
            <div className="absolute top-2 right-2 bg-white dark:bg-slate-950 rounded-full p-1 shadow-md border border-transparent dark:border-slate-800">
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
    <div className="min-h-screen bg-gray-50 dark:bg-slate-950 text-gray-900 dark:text-slate-100 pb-20">
      {/* Header */}
      <header className="fixed top-0 inset-x-0 z-50 pointer-events-none">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-4 pointer-events-auto">
          <div className="rounded-full bg-white/20 dark:bg-slate-950/20 backdrop-blur-2xl backdrop-saturate-150 bg-gradient-to-r from-blue-200/55 via-indigo-100/55 to-violet-100/55 dark:from-slate-900/45 dark:via-slate-900/40 dark:to-slate-800/40 border border-white/55 dark:border-slate-700/50 shadow-[0_18px_40px_-26px_rgba(2,6,23,0.6)]">
            <div className="flex items-center justify-between px-4 py-3">
              <Link to="/" className="flex items-center gap-2">
                <div className="h-9 w-9 rounded-full bg-gradient-to-br from-blue-600 to-indigo-600 flex items-center justify-center shadow-sm">
                  <EqualizerMark className="h-5 w-5 text-white" />
                </div>
                <div className="text-lg font-semibold tracking-tight">
                  <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-700 to-indigo-700">Claim</span>{' '}
                  <span className="text-gray-900 dark:text-white">ex</span>
                </div>
              </Link>

              <div className="hidden md:flex items-center gap-8 text-gray-700 dark:text-slate-200 font-medium">
                <a href="/#features" className="hover:text-blue-800 dark:hover:text-blue-300 transition-colors">Features</a>
                <a href="/#how-it-works" className="hover:text-blue-800 dark:hover:text-blue-300 transition-colors">How it Works</a>
                <a href="/#support" className="hover:text-blue-800 dark:hover:text-blue-300 transition-colors">Contact</a>
              </div>

              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={toggleTheme}
                  className="h-10 w-10 rounded-full bg-white/70 dark:bg-slate-900 border border-blue-300/60 dark:border-slate-700 text-gray-800 dark:text-slate-200 hover:bg-white dark:hover:bg-slate-800 transition-colors flex items-center justify-center"
                  aria-label="Toggle theme"
                >
                  {isDark ? <SunIcon className="h-5 w-5" /> : <MoonIcon className="h-5 w-5" />}
                </button>
                <button
                  type="button"
                  onClick={resetEstimation}
                  className="px-5 py-2 rounded-full bg-white/70 dark:bg-slate-950 border border-blue-500/60 dark:border-slate-700 text-gray-900 dark:text-white font-semibold hover:bg-white dark:hover:bg-slate-900 transition-colors"
                >
                  New Estimation
                </button>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-24 pb-8">
        <div className="grid lg:grid-cols-3 gap-8">
          
          {/* Left Column: Input Form */}
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.35 }}
            className="lg:col-span-1 space-y-6"
          >
            
            {/* Configuration Card */}
            <motion.div
              whileHover={{ y: -2 }}
              transition={{ type: 'spring', stiffness: 300, damping: 25 }}
              className="bg-white dark:bg-slate-900 p-6 rounded-2xl shadow-sm border border-gray-100 dark:border-slate-800"
            >
              <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <WrenchScrewdriverIcon className="h-5 w-5 text-blue-600" />
                <span className="text-gray-900 dark:text-white">Configuration</span>
              </h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-slate-300 mb-1">AI Provider</label>
                  <select 
                    className="w-full rounded-lg border-gray-300 dark:border-slate-700 border p-2.5 bg-gray-50 dark:bg-slate-950 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-shadow dark:[color-scheme:dark]"
                    value={config.provider}
                    onChange={(e) => setConfig({...config, provider: e.target.value})}
                    disabled={providersLoading}
                  >
                    {availableProviders.map(p => (
                      <option key={p.id} value={p.id}>{p.name}</option>
                    ))}
                  </select>
                  {providersError && (
                    <div className="mt-2 text-xs text-red-600">{providersError}</div>
                  )}
                  <div className={`mt-2 text-xs ${
                    backendHealth.status === 'up'
                      ? 'text-green-700 dark:text-green-400'
                      : backendHealth.status === 'down'
                        ? 'text-red-700 dark:text-red-400'
                        : 'text-gray-600 dark:text-slate-400'
                  }`}>
                    {backendHealth.status === 'up'
                      ? `API: Connected (${API_BASE_URL || window.location.origin})`
                      : backendHealth.status === 'down'
                        ? `API: Not reachable (${API_BASE_URL || window.location.origin})`
                        : `API: Checking... (${API_BASE_URL || window.location.origin})`}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-slate-300 mb-1">Registration Number (if plate not readable)</label>
                  <input
                    type="text"
                    className="w-full rounded-lg border-gray-300 dark:border-slate-700 border p-2.5 bg-white dark:bg-slate-950 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-slate-500 focus:ring-2 focus:ring-blue-500"
                    placeholder="e.g. KA01AB1234"
                    value={config.registrationNumber}
                    onChange={(e) => setConfig({ ...config, registrationNumber: e.target.value })}
                  />
                </div>


                {providerUsesApiKeyField && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-slate-300 mb-1">API Key</label>
                    <input
                      type="password"
                      className={`w-full rounded-lg border border-gray-300 dark:border-slate-700 p-2.5 bg-white dark:bg-slate-950 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-slate-500 focus:ring-2 ${
                        apiKeyInvalid ? 'border-red-400 dark:border-red-500 focus:ring-red-500' : 'focus:ring-blue-500'
                      }`}
                      placeholder={`Enter ${config.provider.toUpperCase()} API Key`}
                      value={config.apiKey}
                      onChange={(e) => {
                        const v = e.target.value;
                        setApiKeyInvalid(false);
                        setConfig({ ...config, apiKey: v });
                        if (rememberApiKey) {
                          const cookieName = cookieNameForProvider(config.provider);
                          if (cookieName) {
                            if (v) setCookie(cookieName, v, 30);
                            else deleteCookie(cookieName);
                          }
                        }
                      }}
                    />
                    <div className="mt-2 flex items-start gap-2">
                      <input
                        id="remember-api-key"
                        type="checkbox"
                        checked={rememberApiKey}
                        onChange={(e) => {
                          const checked = e.target.checked;
                          setRememberApiKey(checked);
                          const cookieName = cookieNameForProvider(config.provider);
                          if (!cookieName) return;
                          if (checked) {
                            if (config.apiKey) setCookie(cookieName, config.apiKey, 30);
                          } else {
                            deleteCookie(cookieName);
                          }
                        }}
                        className="mt-0.5 h-4 w-4 rounded border-gray-300 dark:border-slate-700 bg-white dark:bg-slate-950"
                      />
                      <label htmlFor="remember-api-key" className="text-xs text-gray-600 dark:text-slate-400 leading-relaxed">
                        Remember API key on this browser (stored in a cookie).
                      </label>
                    </div>
                  </div>
                )}
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-slate-300 mb-1">Labor Rate (₹/hr)</label>
                  <div className="relative">
                    <span className="absolute left-3 top-2.5 text-gray-500 dark:text-slate-400">₹</span>
                    <input 
                      type="number"
                      className="w-full rounded-lg border-gray-300 dark:border-slate-700 border p-2.5 pl-8 bg-white dark:bg-slate-950 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
                      value={config.laborRate}
                      onChange={(e) => setConfig({...config, laborRate: parseFloat(e.target.value)})}
                    />
                  </div>
                </div>
              </div>
            </motion.div>

            {/* Upload Instructions */}
            <div className="bg-blue-50 dark:bg-slate-900/60 p-6 rounded-2xl border border-blue-100 dark:border-slate-800">
              <h3 className="text-blue-900 dark:text-slate-100 font-semibold mb-2 flex items-center gap-2">
                <PhotoIcon className="h-5 w-5" />
                Photo Guidelines
              </h3>
              <ul className="text-sm text-blue-800 dark:text-slate-300 space-y-2 list-disc pl-4">
                <li>Ensure good lighting and clear focus.</li>
                <li>Capture the entire vehicle from 4 angles.</li>
                <li>Add close-ups of specific damage in "Extra Photos".</li>
                <li>Avoid blurry or extremely dark images.</li>
              </ul>
            </div>
          </motion.div>

          {/* Middle/Right Column: Upload Grid & Results */}
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.35, delay: 0.05 }}
            className="lg:col-span-2 space-y-8"
          >
            
            {/* Upload Grid */}
            <motion.div
              whileHover={{ y: -2 }}
              transition={{ type: 'spring', stiffness: 300, damping: 25 }}
              className="bg-white dark:bg-slate-900 p-8 rounded-2xl shadow-sm border border-gray-100 dark:border-slate-800"
            >
              <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-6">Vehicle Photos</h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                <UploadBox type="front" label="Front View" icon={PhotoIcon} required />
                <UploadBox type="back" label="Back View" icon={PhotoIcon} required />
                <UploadBox type="left" label="Left Side" icon={PhotoIcon} required />
                <UploadBox type="right" label="Right Side" icon={PhotoIcon} required />
                
                <UploadBox type="extras" label="Extra Photos (Optional close-ups)" icon={PlusIcon} />
              </div>

              <div className="flex flex-col items-center">
                {error && (
                  <div className="mb-4 p-4 bg-red-50 dark:bg-red-950/40 text-red-700 dark:text-red-200 rounded-xl text-sm flex items-center gap-2 w-full border border-red-100 dark:border-red-900">
                    <ExclamationCircleIcon className="h-5 w-5 flex-shrink-0" />
                    {error}
                  </div>
                )}
                
                <motion.button
                  onClick={analyzeClaim}
                  disabled={loading}
                  whileTap={{ scale: 0.98 }}
                  className={`
                    w-full md:w-auto min-w-[200px] py-4 px-8 rounded-xl font-bold text-lg shadow-lg transition-all duration-300 flex items-center justify-center gap-2
                    ${loading 
                      ? 'bg-gray-100 dark:bg-slate-800 text-gray-400 dark:text-slate-300 cursor-not-allowed shadow-none' 
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
                </motion.button>
              </div>
            </motion.div>

            {/* Results Section */}
            {result && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.35 }}
                className="space-y-6"
              >
                <div className="flex flex-wrap gap-3 justify-end">
                  <button
                    type="button"
                    onClick={exportPdf}
                    className="px-4 py-2 rounded-lg bg-white dark:bg-slate-950 border border-gray-200 dark:border-slate-800 text-gray-800 dark:text-slate-100 font-semibold hover:bg-gray-50 dark:hover:bg-slate-900 transition-colors"
                  >
                    Export PDF
                  </button>
                </div>
                <div className="p-6 rounded-2xl border bg-blue-50 dark:bg-slate-900/60 border-blue-200 dark:border-slate-800 text-blue-800 dark:text-slate-200">
                  <div className="flex items-start md:items-center gap-4">
                    <div className="p-3 rounded-full bg-blue-100 dark:bg-slate-950">
                      <CheckCircleIcon className="h-8 w-8" />
                    </div>
                    <div>
                      <h2 className="text-2xl font-bold">Estimate</h2>
                      <p className="opacity-90 mt-1">This is an automated cost estimate based on detected damages and part prices.</p>
                    </div>
                  </div>
                </div>

                <div className="grid md:grid-cols-2 gap-6">
                  {/* Vehicle Details */}
                  <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl shadow-sm border border-gray-100 dark:border-slate-800 md:col-span-2">
                    <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                      <TruckIcon className="h-5 w-5 text-blue-600" />
                      <span className="text-gray-900 dark:text-white">Vehicle Details</span>
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="p-4 bg-gray-50 dark:bg-slate-950 rounded-xl border border-gray-100 dark:border-slate-800">
                        <span className="text-xs font-semibold text-gray-500 dark:text-slate-400 uppercase tracking-wider block mb-1">Make & Model</span>
                        <span className="font-bold text-gray-900 dark:text-white text-lg">
                          {result?.damage_assessment?.car_info || "Unknown Car"}
                        </span>
                      </div>
                      <div className="p-4 bg-gray-50 dark:bg-slate-950 rounded-xl border border-gray-100 dark:border-slate-800">
                        <span className="text-xs font-semibold text-gray-500 dark:text-slate-400 uppercase tracking-wider block mb-1">Registration Number</span>
                        <span className="font-bold text-gray-900 dark:text-white text-lg font-mono">
                          {result?.damage_assessment?.registration_number || "Not Visible"}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Damage List */}
                  <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl shadow-sm border border-gray-100 dark:border-slate-800">
                    <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                      <DocumentTextIcon className="h-5 w-5 text-blue-600" />
                      <span className="text-gray-900 dark:text-white">Identified Damages</span>
                    </h3>
                    <div className="space-y-3 max-h-[400px] overflow-y-auto pr-2 custom-scrollbar">
                      {result?.damage_assessment?.damages?.map((damage, idx) => (
                        <div key={idx} className="p-4 bg-gray-50 dark:bg-slate-950 rounded-xl border border-gray-100 dark:border-slate-800 hover:border-blue-200 dark:hover:border-blue-500 transition-colors">
                          <div className="flex justify-between items-start mb-2">
                            <span className="font-bold text-gray-900 dark:text-white capitalize">
                              {damage?.part?.replace(/_/g, ' ') || 'Unknown Part'}
                            </span>
                            <span className={`px-2.5 py-1 text-xs font-bold rounded-full capitalize ${
                              damage.severity === 'severe' ? 'bg-red-100 text-red-700' :
                              damage.severity === 'moderate' ? 'bg-orange-100 text-orange-700' :
                              'bg-green-100 text-green-700'
                            }`}>
                              {damage.severity || 'moderate'}
                            </span>
                          </div>
                          <p className="text-sm text-gray-600 dark:text-slate-300 leading-relaxed">{damage.description || 'No description available.'}</p>
                        </div>
                      ))}
                      {(!result?.damage_assessment?.damages || result.damage_assessment.damages.length === 0) && (
                        <p className="text-gray-500 dark:text-slate-400 italic text-center py-8">No significant damages detected.</p>
                      )}
                    </div>
                  </div>

                  {/* Cost Breakdown */}
                  <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl shadow-sm border border-gray-100 dark:border-slate-800">
                    <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                      <CurrencyDollarIcon className="h-5 w-5 text-blue-600" />
                      <span className="text-gray-900 dark:text-white">Cost Summary</span>
                    </h3>
                    
                    <div className="space-y-4">
                      <div className="flex justify-between items-center p-3 bg-gray-50 dark:bg-slate-950 rounded-lg border border-gray-100 dark:border-slate-800">
                        <span className="text-gray-600 dark:text-slate-300">Parts Total</span>
                        <span className="font-semibold text-gray-900 dark:text-white">{formatCurrency(result?.cost_estimate?.summary?.total_parts_cost)}</span>
                      </div>
                      <div className="flex justify-between items-center p-3 bg-gray-50 dark:bg-slate-950 rounded-lg border border-gray-100 dark:border-slate-800">
                        <span className="text-gray-600 dark:text-slate-300">
                          Labor ({result?.cost_estimate?.summary?.total_labor_hours || 0} hrs)
                        </span>
                        <span className="font-semibold text-gray-900 dark:text-white">{formatCurrency(result?.cost_estimate?.summary?.total_labor_cost)}</span>
                      </div>
                      <div className="flex justify-between items-center p-3 bg-gray-50 dark:bg-slate-950 rounded-lg border border-gray-100 dark:border-slate-800">
                        <span className="text-gray-600 dark:text-slate-300">Tax (18% GST)</span>
                        <span className="font-semibold text-gray-900 dark:text-white">{formatCurrency(result?.cost_estimate?.summary?.tax)}</span>
                      </div>
                      
                      <div className="pt-4 mt-4 border-t border-gray-100 dark:border-slate-800">
                        <div className="flex justify-between items-end">
                          <span className="text-gray-500 dark:text-slate-400 font-medium">Grand Total</span>
                          <span className="text-3xl font-bold text-blue-600">
                            {formatCurrency(result?.cost_estimate?.summary?.total_cost)}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Line Items Table */}
                <div className="bg-white dark:bg-slate-900 rounded-2xl shadow-sm border border-gray-100 dark:border-slate-800 overflow-hidden">
                  <div className="px-6 py-5 border-b border-gray-100 dark:border-slate-800 bg-gray-50/50 dark:bg-slate-950">
                    <h3 className="font-bold text-gray-900 dark:text-white">Detailed Line Items</h3>
                  </div>
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm text-left">
                      <thead className="bg-gray-50 dark:bg-slate-950 text-gray-700 dark:text-slate-300 font-semibold uppercase text-xs tracking-wider">
                        <tr>
                          <th className="px-6 py-4">Part</th>
                          <th className="px-6 py-4">Severity</th>
                          <th className="px-6 py-4 text-right">Part Cost</th>
                          <th className="px-6 py-4 text-center">Source</th>
                          <th className="px-6 py-4 text-right">Labor</th>
                          <th className="px-6 py-4 text-right">Total</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-100 dark:divide-slate-800">
                        {result?.cost_estimate?.line_items?.map((item, idx) => (
                          <tr key={idx} className="hover:bg-blue-50/30 dark:hover:bg-slate-800/40 transition-colors">
                            <td className="px-6 py-4 font-medium capitalize text-gray-900 dark:text-white">
                              {item.part?.replace(/_/g, ' ') || 'Unknown'}
                            </td>
                            <td className="px-6 py-4">
                              <span className={`px-2 py-1 rounded text-xs font-semibold capitalize ${
                                item.severity === 'severe' ? 'bg-red-50 text-red-700' :
                                item.severity === 'moderate' ? 'bg-orange-50 text-orange-700' :
                                'bg-green-50 text-green-700'
                              }`}>
                                {item.severity || 'moderate'}
                              </span>
                            </td>
                            <td className="px-6 py-4 text-right text-gray-600 dark:text-slate-300 font-medium">
                              {formatCurrency(item.part_cost)}
                            </td>
                            <td className="px-6 py-4 text-center">
                              {item.source_url ? (
                                <a 
                                  href={item.source_url} 
                                  target="_blank" 
                                  rel="noopener noreferrer" 
                                  className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 hover:underline text-xs font-semibold bg-blue-50 dark:bg-slate-950 px-2.5 py-1 rounded-full border border-blue-100 dark:border-slate-800 inline-flex items-center gap-1"
                                >
                                  Web Search ↗
                                </a>
                              ) : (
                                <span className="text-gray-400 dark:text-slate-400 text-xs font-medium bg-gray-50 dark:bg-slate-950 px-2.5 py-1 rounded-full border border-gray-200 dark:border-slate-800">
                                  Database
                                </span>
                              )}
                            </td>
                            <td className="px-6 py-4 text-right text-gray-600 dark:text-slate-300">{formatCurrency(item.labor_cost)}</td>
                            <td className="px-6 py-4 text-right font-bold text-gray-900 dark:text-white">{formatCurrency(item.total)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </motion.div>
            )}
          </motion.div>
        </div>
      </main>
    </div>
  );
}

function EqualizerMark(props) {
  return (
    <svg {...props} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M6 6v12" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" />
      <path d="M10 4v16" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" />
      <path d="M14 8v8" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" />
      <path d="M18 6v12" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" />
    </svg>
  );
}
