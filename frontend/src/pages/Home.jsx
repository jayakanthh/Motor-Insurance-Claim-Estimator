import { useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowRightIcon, CameraIcon, ShieldCheckIcon, ClockIcon, MoonIcon, SunIcon, MagnifyingGlassIcon, DocumentTextIcon, CpuChipIcon } from '@heroicons/react/24/outline';

export default function Home() {
  const [isDark, setIsDark] = useState(document.documentElement.classList.contains('dark'));

  const toggleTheme = () => {
    const next = !document.documentElement.classList.contains('dark');
    document.documentElement.classList.toggle('dark', next);
    localStorage.setItem('theme', next ? 'dark' : 'light');
    setIsDark(next);
  };

  return (
    <div id="top" className="min-h-screen bg-gradient-to-br from-white to-green-50 dark:from-black dark:to-neutral-950 overflow-hidden">
      <div className="fixed top-0 inset-x-0 z-50 pointer-events-none">
        <div className="max-w-7xl mx-auto px-6 pt-6 pointer-events-auto">
          <div className="rounded-full bg-white/20 dark:bg-black/40 backdrop-blur-2xl backdrop-saturate-150 bg-gradient-to-r from-white/40 via-green-50/40 to-green-100/40 dark:from-neutral-950/45 dark:via-neutral-950/40 dark:to-neutral-900/40 border border-white/55 dark:border-neutral-800/50 shadow-[0_18px_40px_-26px_rgba(2,6,23,0.6)]">
            <div className="flex items-center justify-between px-4 py-3">
              <Link to="/" className="flex items-center gap-2">
                <img src="/logo.png" alt="ClaimEX" className="h-16 w-auto object-contain ml-2 -my-3" />
              </Link>

              <div className="hidden md:flex items-center gap-8 text-gray-700 dark:text-neutral-200 font-medium">
                <a href="#features" className="hover:text-green-800 dark:hover:text-green-300 transition-colors">Features</a>
                <a href="#how-it-works" className="hover:text-green-800 dark:hover:text-green-300 transition-colors">How it Works</a>
                <a href="#support" className="hover:text-green-800 dark:hover:text-green-300 transition-colors">Contact</a>
              </div>

              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={toggleTheme}
                  className="h-10 w-10 rounded-full bg-white/70 dark:bg-neutral-900 border border-green-300/60 dark:border-neutral-700 text-gray-800 dark:text-neutral-200 hover:bg-white dark:hover:bg-neutral-800 transition-colors flex items-center justify-center"
                  aria-label="Toggle theme"
                >
                  {isDark ? <SunIcon className="h-5 w-5" /> : <MoonIcon className="h-5 w-5" />}
                </button>
                <Link
                  to="/estimate"
                  className="inline-flex items-center justify-center px-5 py-2 rounded-full bg-green-600 text-white font-semibold shadow-sm hover:bg-green-700 transition-colors"
                >
                  Start
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-6 pt-28 pb-12 md:pt-32 md:pb-20 grid lg:grid-cols-2 gap-12 items-center">
        <motion.div
          initial={{ opacity: 0, x: -50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8 }}
        >
          <h1 className="text-5xl md:text-6xl font-extrabold text-gray-900 dark:text-white leading-tight mb-6">
            Instant Car Damage <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-green-600 to-[#02b967]">
              Estimates in Seconds
            </span>
          </h1>
          <p className="text-xl text-gray-600 dark:text-neutral-300 mb-8 leading-relaxed max-w-lg">
            Upload photos of your vehicle and let our AI analyze the damage and generate a clean, itemized report instantly.
          </p>

          <div className="flex flex-col sm:flex-row gap-4">
            <Link
              to="/estimate"
              className="flex items-center justify-center gap-2 bg-green-600 text-white px-8 py-4 rounded-xl font-bold text-lg shadow-lg shadow-green-200 hover:bg-green-700 hover:shadow-xl hover:-translate-y-1 transition-all"
            >
              Get Estimation
              <ArrowRightIcon className="h-5 w-5" />
            </Link>
          </div>

          <div className="mt-10 flex flex-wrap items-center gap-6 text-sm text-gray-500 dark:text-neutral-400 font-semibold">
            <div className="flex items-center gap-2">
              <CheckIcon className="h-5 w-5 text-green-500" />
              <span>Multi-angle assessment</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckIcon className="h-5 w-5 text-green-500" />
              <span>Itemized estimate + PDF export</span>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="relative"
        >
          <div className="absolute -top-10 -right-10 w-72 h-72 bg-green-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob"></div>
          <div className="absolute -bottom-10 -left-10 w-72 h-72 bg-[#02b967] rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-2000"></div>

          <div className="relative bg-white/60 backdrop-blur-xl border border-white/50 dark:bg-neutral-900/40 dark:border-neutral-800 rounded-3xl p-6 shadow-2xl transform rotate-2 hover:rotate-0 transition-all duration-500 hover:shadow-3xl">
            <div className="space-y-4">
              <div className="h-72 bg-gray-200 rounded-xl w-full overflow-hidden relative">
                <img src="/sample-image.jpg" alt="Sample vehicle" className="absolute inset-0 w-full h-full object-cover" />
                <div className="absolute top-0 left-0 w-full h-1 bg-green-500 shadow-[0_0_15px_rgba(59,130,246,0.8)] animate-scan"></div>
              </div>
              <div className="space-y-2 pt-2">
                <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                <div className="h-4 bg-gray-200 rounded w-1/2"></div>
              </div>
              <div className="pt-4 flex justify-between items-center">
                <div>
                  <div className="text-xs text-gray-500 dark:text-neutral-400 uppercase font-bold">Estimated Cost</div>
                  <div className="text-2xl font-bold text-gray-900 dark:text-white">₹45,000.00</div>
                </div>
                <div className="bg-green-100 text-green-700 px-3 py-1 rounded-full text-sm font-bold">
                  Automated
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Features Grid */}
      <div id="features" className="max-w-7xl mx-auto px-6 py-20">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4">Why Choose Claim ex?</h2>
          <p className="text-gray-600 dark:text-neutral-300 max-w-2xl mx-auto">We combine computer vision with insurance expertise to deliver a fast and transparent estimation experience.</p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {[
            {
              icon: <ClockIcon className="h-8 w-8 text-white" />,
              title: "Lightning Fast",
              desc: "Get a complete damage assessment and cost estimate in under 60 seconds.",
              color: "bg-green-500"
            },
            {
              icon: <CameraIcon className="h-8 w-8 text-white" />,
              title: "Multi-Angle Analysis",
              desc: "Our AI analyzes 4+ angles to ensure no damage is missed, just like a human adjuster.",
              color: "bg-[#02b967]"
            },
            {
              icon: <ShieldCheckIcon className="h-8 w-8 text-white" />,
              title: "Fair & Accurate",
              desc: "Standardized parts database and labor rates ensure consistent and fair estimations.",
              color: "bg-purple-500"
            }
          ].map((feature, idx) => (
            <motion.div
              key={idx}
              whileHover={{ scale: 1.02 }}
              className="bg-gray-50/80 dark:bg-neutral-900 p-8 rounded-2xl shadow-[inset_0_2px_8px_rgba(0,0,0,0.06)] dark:shadow-[inset_0_1px_4px_rgba(0,0,0,0.4),0_0_30px_rgba(3,218,124,0.35)] border border-gray-200/60 dark:border-green-400/40 hover:shadow-xl dark:hover:shadow-[inset_0_1px_4px_rgba(0,0,0,0.4),0_0_40px_rgba(3,218,124,0.5)] transition-all"
            >
              <div className={`${feature.color} w-14 h-14 rounded-xl flex items-center justify-center mb-6 shadow-lg`}>
                {feature.icon}
              </div>
              <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-3">{feature.title}</h3>
              <p className="text-gray-600 dark:text-neutral-300 leading-relaxed">{feature.desc}</p>
            </motion.div>
          ))}
        </div>
      </div>

      <div id="how-it-works" className="max-w-7xl mx-auto px-6 pb-20">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4">How it Works</h2>
          <p className="text-gray-600 dark:text-neutral-300 max-w-3xl mx-auto">From 4 photos to a repair estimate: AI detects damages, enriches vehicle details using the registration number, prices parts using multiple sources, and generates a PDF report.</p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {[
            {
              icon: <CameraIcon className="h-8 w-8 text-white" />,
              title: "Upload required photos",
              desc: "Front, rear, left, and right angles; add optional close-ups for clarity.",
              color: "bg-green-600"
            },
            {
              icon: <CpuChipIcon className="h-8 w-8 text-white" />,
              title: "Pick an AI provider",
              desc: "Choose OpenAI GPT-4o or Google Gemini for AI-powered damage detection.",
              color: "bg-[#02b967]"
            },
            {
              icon: <MagnifyingGlassIcon className="h-8 w-8 text-white" />,
              title: "Add registration number",
              desc: "Used to enrich make/model/year for more accurate parts matching and pricing.",
              color: "bg-[#03da7c]"
            },
            {
              icon: <ShieldCheckIcon className="h-8 w-8 text-white" />,
              title: "Conservative detection",
              desc: "Built-in strict prompting + evidence filtering to reduce false positives.",
              color: "bg-purple-600"
            },
            {
              icon: <ClockIcon className="h-8 w-8 text-white" />,
              title: "Price parts intelligently",
              desc: "Tries web prices first, then falls back to a local parts DB or average values.",
              color: "bg-sky-600"
            },
            {
              icon: <DocumentTextIcon className="h-8 w-8 text-white" />,
              title: "Review + export PDF",
              desc: "Get damages, totals, detailed line-items, and a downloadable report.",
              color: "bg-green-700"
            }
          ].map((step, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 12 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, amount: 0.25 }}
              transition={{ duration: 0.5, delay: idx * 0.04 }}
              whileHover={{ scale: 1.02 }}
              className="bg-gray-50/80 dark:bg-neutral-900/70 backdrop-blur-xl p-8 rounded-2xl shadow-[inset_0_2px_8px_rgba(0,0,0,0.06)] dark:shadow-[inset_0_1px_4px_rgba(0,0,0,0.4),0_0_30px_rgba(3,218,124,0.35)] border border-gray-200/60 dark:border-green-400/40 hover:shadow-xl dark:hover:shadow-[inset_0_1px_4px_rgba(0,0,0,0.4),0_0_40px_rgba(3,218,124,0.5)] transition-all"
            >
              <div className={`${step.color} w-14 h-14 rounded-xl flex items-center justify-center mb-6 shadow-lg`}>
                {step.icon}
              </div>
              <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-3">{step.title}</h3>
              <p className="text-gray-700 dark:text-neutral-300 leading-relaxed">{step.desc}</p>
            </motion.div>
          ))}
        </div>

        <motion.div
          initial={{ opacity: 0, y: 12 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.2 }}
          transition={{ duration: 0.55, delay: 0.05 }}
          className="mt-10 bg-white/60 dark:bg-neutral-900/50 backdrop-blur-2xl border border-white/60 dark:border-neutral-800 rounded-3xl p-8"
        >
          <h3 className="text-xl font-extrabold text-gray-900 dark:text-white mb-3">Under the hood</h3>
          <div className="grid md:grid-cols-2 gap-6 text-gray-700 dark:text-neutral-300 leading-relaxed">
            <ul className="space-y-2">
              <li>Multi-angle input: 4 mandatory views + optional extras.</li>
              <li>Local-model support: combines angles when needed for single-image inference.</li>
              <li>False-positive control: strict prompts + evidence-based filtering.</li>
              <li>Standardized part keys: consistent mapping for estimation and reporting.</li>
            </ul>
            <ul className="space-y-2">
              <li>Pricing hierarchy: web search → local DB → average fallback.</li>
              <li>Fast UX: capped/parallel price lookups to keep runtime reasonable.</li>
              <li>Transparent results: itemized line-items with sources.</li>
              <li>Export: one-click PDF report for sharing and documentation.</li>
            </ul>
          </div>
        </motion.div>
      </div>

      <div id="support" className="max-w-7xl mx-auto px-6 pb-20">
        <div className="bg-white/70 dark:bg-neutral-900/40 backdrop-blur-xl border border-white/60 dark:border-neutral-800 rounded-3xl p-10 shadow-sm">
          <div className="grid md:grid-cols-2 gap-10 items-center">
            <div>
              <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-3">Support</h2>
              <p className="text-gray-600 dark:text-neutral-300 leading-relaxed">Need help with uploads, pricing, or model selection? Reach out and we’ll help you troubleshoot quickly.</p>
            </div>
            <div className="flex flex-col sm:flex-row gap-3 md:justify-end">
              <a
                href="mailto:support@claimestimator.ai"
                className="px-6 py-3 rounded-xl bg-white dark:bg-neutral-950 border border-gray-200 dark:border-neutral-800 text-gray-900 dark:text-white font-bold hover:bg-gray-50 dark:hover:bg-neutral-900 transition-colors text-center"
              >
                Email Support
              </a>
              <Link
                to="/estimate"
                className="px-6 py-3 rounded-xl bg-green-600 text-white font-bold hover:bg-green-700 transition-colors text-center"
              >
                Try Estimation
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function CheckIcon(props) {
  return (
    <svg {...props} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
    </svg>
  );
}


