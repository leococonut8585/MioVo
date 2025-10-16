import { useState } from 'react'
import { ReadingMode } from './components/reading/ReadingMode'
import { SingingMode } from './components/singing/SingingMode'

function App() {
  const [mode, setMode] = useState<'reading' | 'singing'>('reading')

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100">
      {/* Header */}
      <header className="border-b border-slate-800 bg-slate-950">
        <div className="flex items-center justify-between px-6 py-4">
          <div className="flex items-center gap-4">
            <h1 className="text-2xl font-bold text-primary-400">MioVo</h1>
            <span className="text-sm text-slate-400">Local Voice Studio</span>
          </div>
          
          {/* Mode Selector */}
          <div className="flex gap-2">
            <button
              onClick={() => setMode('reading')}
              className={`px-4 py-2 rounded-lg transition-colors ${
                mode === 'reading'
                  ? 'bg-primary-600 text-white'
                  : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
              }`}
            >
              朗読モード
            </button>
            <button
              onClick={() => setMode('singing')}
              className={`px-4 py-2 rounded-lg transition-colors ${
                mode === 'singing'
                  ? 'bg-primary-600 text-white'
                  : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
              }`}
            >
              歌唱モード
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto p-6 h-[calc(100vh-80px)]">
        {mode === 'reading' ? <ReadingMode /> : <SingingMode />}
      </main>
    </div>
  )
}

export default App
