import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowRightIcon, CameraIcon, ShieldCheckIcon, ClockIcon } from '@heroicons/react/24/outline';

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50 overflow-hidden">
      {/* Navbar */}
      <nav className="flex justify-between items-center p-6 max-w-7xl mx-auto">
        <div className="flex items-center gap-2">
          <div className="bg-blue-600 p-2 rounded-lg">
            <ShieldCheckIcon className="h-6 w-6 text-white" />
          </div>
          <span className="text-xl font-bold text-gray-900 tracking-tight">ClaimEstimator AI</span>
        </div>
        <div className="hidden md:flex gap-6 text-gray-600 font-medium">
          <a href="#features" className="hover:text-blue-600 transition-colors">Features</a>
          <a href="#how-it-works" className="hover:text-blue-600 transition-colors">How it Works</a>
          <a href="#" className="hover:text-blue-600 transition-colors">Support</a>
        </div>
        <Link 
          to="/estimate" 
          className="bg-white text-blue-600 px-5 py-2.5 rounded-full font-semibold shadow-sm border border-blue-100 hover:shadow-md transition-all"
        >
          Start Now
        </Link>
      </nav>

      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-6 py-16 md:py-24 grid lg:grid-cols-2 gap-12 items-center">
        <motion.div 
          initial={{ opacity: 0, x: -50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8 }}
        >
          <div className="inline-flex items-center gap-2 bg-blue-100 text-blue-700 px-4 py-1.5 rounded-full text-sm font-semibold mb-6">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
            </span>
            AI-Powered Analysis 2.0
          </div>
          <h1 className="text-5xl md:text-6xl font-extrabold text-gray-900 leading-tight mb-6">
            Instant Car Damage <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600">
              Estimates in Seconds
            </span>
          </h1>
          <p className="text-xl text-gray-600 mb-8 leading-relaxed max-w-lg">
            Upload photos of your vehicle and let our advanced AI analyze the damage, estimate repair costs, and generate pre-approval reports instantly.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4">
            <Link 
              to="/estimate" 
              className="flex items-center justify-center gap-2 bg-blue-600 text-white px-8 py-4 rounded-xl font-bold text-lg shadow-lg shadow-blue-200 hover:bg-blue-700 hover:shadow-xl hover:-translate-y-1 transition-all"
            >
              Get Estimation
              <ArrowRightIcon className="h-5 w-5" />
            </Link>
            <button className="flex items-center justify-center gap-2 bg-white text-gray-700 px-8 py-4 rounded-xl font-bold text-lg shadow-sm border border-gray-200 hover:bg-gray-50 transition-all">
              Watch Demo
            </button>
          </div>

          <div className="mt-10 flex items-center gap-6 text-sm text-gray-500 font-medium">
            <div className="flex items-center gap-2">
              <CheckIcon className="h-5 w-5 text-green-500" />
              <span>98% Accuracy</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckIcon className="h-5 w-5 text-green-500" />
              <span>Instant Report</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckIcon className="h-5 w-5 text-green-500" />
              <span>Bank Level Security</span>
            </div>
          </div>
        </motion.div>

        <motion.div 
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="relative"
        >
          <div className="absolute -top-10 -right-10 w-72 h-72 bg-blue-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob"></div>
          <div className="absolute -bottom-10 -left-10 w-72 h-72 bg-indigo-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-2000"></div>
          
          <div className="relative bg-white/60 backdrop-blur-xl border border-white/50 rounded-3xl p-6 shadow-2xl transform rotate-2 hover:rotate-0 transition-all duration-500">
             {/* Mock UI Card */}
             <div className="space-y-4">
                <div className="h-48 bg-gray-200 rounded-xl w-full overflow-hidden relative">
                   <div className="absolute inset-0 flex items-center justify-center text-gray-400">
                      <CameraIcon className="h-12 w-12" />
                   </div>
                   {/* Overlay simulating scanning */}
                   <div className="absolute top-0 left-0 w-full h-1 bg-blue-500 shadow-[0_0_15px_rgba(59,130,246,0.8)] animate-scan"></div>
                </div>
                <div className="flex gap-4">
                   <div className="h-20 w-20 bg-gray-100 rounded-lg"></div>
                   <div className="h-20 w-20 bg-gray-100 rounded-lg"></div>
                   <div className="h-20 w-20 bg-gray-100 rounded-lg"></div>
                </div>
                <div className="space-y-2 pt-2">
                   <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                   <div className="h-4 bg-gray-200 rounded w-1/2"></div>
                </div>
                <div className="pt-4 flex justify-between items-center">
                   <div>
                      <div className="text-xs text-gray-500 uppercase font-bold">Estimated Cost</div>
                      <div className="text-2xl font-bold text-gray-900">$1,250.00</div>
                   </div>
                   <div className="bg-green-100 text-green-700 px-3 py-1 rounded-full text-sm font-bold">
                      Pre-Approved
                   </div>
                </div>
             </div>
          </div>
        </motion.div>
      </div>
      
      {/* Features Grid */}
      <div id="features" className="max-w-7xl mx-auto px-6 py-20">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">Why Choose ClaimEstimator?</h2>
          <p className="text-gray-600 max-w-2xl mx-auto">We combine cutting-edge computer vision with insurance expertise to deliver the fastest claim processing experience.</p>
        </div>
        
        <div className="grid md:grid-cols-3 gap-8">
          {[
            {
              icon: <ClockIcon className="h-8 w-8 text-white" />,
              title: "Lightning Fast",
              desc: "Get a complete damage assessment and cost estimate in under 60 seconds.",
              color: "bg-blue-500"
            },
            {
              icon: <CameraIcon className="h-8 w-8 text-white" />,
              title: "Multi-Angle Analysis",
              desc: "Our AI analyzes 4+ angles to ensure no damage is missed, just like a human adjuster.",
              color: "bg-indigo-500"
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
              whileHover={{ y: -5 }}
              className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100 hover:shadow-xl transition-all"
            >
              <div className={`${feature.color} w-14 h-14 rounded-xl flex items-center justify-center mb-6 shadow-lg`}>
                {feature.icon}
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">{feature.title}</h3>
              <p className="text-gray-600 leading-relaxed">{feature.desc}</p>
            </motion.div>
          ))}
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
