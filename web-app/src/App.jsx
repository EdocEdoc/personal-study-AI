import { useState } from "react";
import { ChevronLeft, ChevronRight, Upload } from "lucide-react";

function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 flex items-center justify-center p-6">
      <div className="bg-white rounded-3xl shadow-xl p-10 max-w-7xl w-full">
        <h1 className="text-2xl font-bold text-gray-900 mb-8">AI Study Tool</h1>

        <div className="flex gap-8">
          {/* Left Section */}
          <div className="flex-1 space-y-6">
            {/* Upload Section */}
            <div
              className="bg-gray-50 rounded-2xl p-5 border border-gray-200 flex items-center gap-4 hover:bg-white hover:cursor-pointer transition-all duration-200 hover:-translate-y-1 hover:shadow-lg active:translate-y-0 active:shadow-md active:scale-95"
              onClick={() => console.log("clicked")}
            >
              <div className="bg-white rounded-xl p-3 shadow-sm">
                <Upload className="w-6 h-6 text-gray-400" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 text-sm">
                  Upload your file
                </h3>
                <p className="text-xs text-gray-500">PDF / DOCX / TXT</p>
              </div>
            </div>

            {/* Question Card */}
            <div className="bg-gray-50 rounded-2xl p-6 border border-gray-200">
              <div className="flex items-start gap-3">
                <button className="mt-2 p-1 hover:bg-gray-200 rounded-lg transition-colors">
                  <ChevronLeft className="w-5 h-5 text-gray-400" />
                </button>
                <div className="flex-1">
                  <h2 className="text-lg font-bold text-gray-900 mb-2">
                    What is photosynthesis?
                  </h2>
                  <p className="text-sm text-gray-600">
                    The process by which plants convert sunlight into energy
                  </p>
                </div>
                <button className="mt-2 p-1 hover:bg-gray-200 rounded-lg transition-colors">
                  <ChevronRight className="w-5 h-5 text-gray-400" />
                </button>
              </div>
            </div>

            {/* Quiz Mode */}
            <div>
              <h3 className="font-bold text-gray-900 mb-4 text-sm">
                Quiz Mode
              </h3>
              <div className="grid grid-cols-2 gap-3">
                <button className="bg-white border border-gray-200 rounded-xl p-3 text-left hover:border-gray-300 transition-colors text-sm">
                  <span className="text-gray-500 font-medium">A.</span>
                  <span className="text-gray-700 ml-2">
                    Cellular respiration
                  </span>
                </button>
                <button className="bg-blue-50 border border-blue-400 rounded-xl p-3 text-left flex items-center gap-2 text-sm relative">
                  <span className="text-blue-600 font-medium">B.</span>
                  <span className="text-gray-900 ml-1">Photosynthesis</span>
                  <div className="ml-auto w-4 h-4 bg-blue-500 rounded-full flex items-center justify-center">
                    <svg
                      className="w-2.5 h-2.5 text-white"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" />
                    </svg>
                  </div>
                </button>
                <button className="bg-white border border-gray-200 rounded-xl p-3 text-left hover:border-gray-300 transition-colors text-sm">
                  <span className="text-gray-500 font-medium">C.</span>
                  <span className="text-gray-700 ml-2">Osmosis</span>
                </button>
                <button className="bg-white border border-gray-200 rounded-xl p-3 text-left hover:border-gray-300 transition-colors text-sm">
                  <span className="text-gray-500 font-medium">D.</span>
                  <span className="text-gray-700 ml-2">Mitosis</span>
                </button>
              </div>
            </div>
          </div>

          {/* Right Section - Progress */}
          <div className="w-48 space-y-6">
            <div>
              <h3 className="font-semibold text-gray-700 mb-3 text-sm">
                Progress
              </h3>
              <div className="text-5xl font-bold text-indigo-600 mb-1">85%</div>
              <p className="text-xs text-gray-500">Accuracy</p>
            </div>

            <div>
              <div className="text-4xl font-bold text-gray-900 mb-1">8</div>
              <p className="text-xs text-gray-500">Streak</p>
            </div>

            <div className="space-y-4">
              <div>
                <p className="text-xs text-gray-600 mb-2">Weak Topics</p>
                <div className="bg-gray-200 rounded-full h-2 overflow-hidden">
                  <div
                    className="bg-indigo-600 h-full rounded-full"
                    style={{ width: "65%" }}
                  ></div>
                </div>
              </div>
              <div>
                <p className="text-xs text-gray-600 mb-2">Strong Topics</p>
                <div className="bg-gray-200 rounded-full h-2 overflow-hidden">
                  <div
                    className="bg-indigo-600 h-full rounded-full"
                    style={{ width: "95%" }}
                  ></div>
                </div>
              </div>
            </div>

            {/* Chart */}
            <div className="h-24 mt-6">
              <svg
                viewBox="0 0 200 80"
                className="w-full h-full"
                preserveAspectRatio="none"
              >
                <path
                  d="M 0 60 Q 20 55, 40 50 T 80 45 T 120 35 T 160 40 T 200 30"
                  fill="none"
                  stroke="#4F46E5"
                  strokeWidth="2.5"
                  strokeLinecap="round"
                />
              </svg>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
