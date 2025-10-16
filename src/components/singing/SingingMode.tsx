/**
 * Singing Mode Component
 * Main UI for vocal separation and voice conversion
 */
import { useState, useCallback } from 'react'
import { motion, useReducedMotion } from 'motion/react'
import type { RVCParams } from '../../types/audio'

export function SingingMode() {
  const shouldReduceMotion = useReducedMotion()
  const [audioFile, setAudioFile] = useState<File | null>(null)
  const [isDragging, setIsDragging] = useState(false)
  const [separationStatus, setSeparationStatus] = useState<'idle' | 'separating' | 'done'>('idle')
  const [rvcParams, setRvcParams] = useState<RVCParams>({
    f0method: 'harvest',
    protect: 0.5,
    index_rate: 0.75,
    filter_radius: 3,
    resample_sr: 0,
    rms_mix_rate: 0.25
  })

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    
    const files = Array.from(e.dataTransfer.files)
    const audioFile = files.find(f => 
      f.type.startsWith('audio/') || f.name.match(/\.(wav|mp3|flac|ogg)$/i)
    )
    
    if (audioFile) {
      setAudioFile(audioFile)
      console.log('Audio file dropped:', audioFile.name)
    }
  }, [])

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback(() => {
    setIsDragging(false)
  }, [])

  return (
    <div className="grid grid-cols-[1fr_320px] gap-6 h-full">
      {/* Left: Vocal Separation UI */}
      <div className="flex flex-col gap-4">
        {/* Drop Zone */}
        <motion.div
          initial={shouldReduceMotion ? false : { opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          className={`
            min-h-[300px] rounded-lg border-2 border-dashed
            flex flex-col items-center justify-center
            transition-colors cursor-pointer
            ${isDragging
              ? 'border-primary-500 bg-primary-900/20'
              : 'border-slate-700 bg-slate-800/50 hover:border-slate-600'
            }
          `}
        >
          {!audioFile ? (
            <>
              <p className="text-lg text-slate-300 mb-2">
                曲ファイルをドロップ
              </p>
              <p className="text-sm text-slate-500">
                または選択してアップロード
              </p>
              <p className="text-xs text-slate-600 mt-4">
                対応形式: WAV, MP3, FLAC, OGG
              </p>
            </>
          ) : (
            <div className="text-center">
              <p className="text-primary-400 font-semibold mb-2">
                📁 {audioFile.name}
              </p>
              <p className="text-sm text-slate-400">
                {(audioFile.size / 1024 / 1024).toFixed(2)} MB
              </p>
            </div>
          )}
        </motion.div>

        {/* Separation Controls */}
        {audioFile && (
          <motion.div
            initial={shouldReduceMotion ? false : { opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="p-4 bg-slate-800/50 rounded-lg"
          >
            <h4 className="text-sm font-semibold text-slate-300 mb-3">
              音源分離
            </h4>
            
            <div className="space-y-3">
              {/* Separation button */}
              <motion.button
                onClick={() => {
                  setSeparationStatus('separating')
                  console.log('Start separation')
                }}
                disabled={separationStatus === 'separating'}
                className="w-full py-3 bg-primary-600 text-white rounded-lg font-semibold hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                whileHover={shouldReduceMotion ? {} : { scale: 1.02 }}
                whileTap={shouldReduceMotion ? {} : { scale: 0.98 }}
              >
                {separationStatus === 'separating' ? '分離中...' : '歌声と伴奏を分離'}
              </motion.button>

              {/* Progress */}
              {separationStatus === 'separating' && (
                <div className="w-full h-2 bg-slate-700 rounded-full overflow-hidden">
                  <motion.div
                    className="h-full bg-primary-500"
                    initial={{ width: '0%' }}
                    animate={{ width: '100%' }}
                    transition={{ duration: 3, ease: 'linear' }}
                  />
                </div>
              )}

              {/* Result */}
              {separationStatus === 'done' && (
                <div className="grid grid-cols-2 gap-2">
                  <div className="p-3 bg-slate-700 rounded-lg">
                    <p className="text-xs text-slate-400 mb-1">歌声</p>
                    <p className="text-sm text-slate-200">vocals.wav</p>
                  </div>
                  <div className="p-3 bg-slate-700 rounded-lg">
                    <p className="text-xs text-slate-400 mb-1">伴奏</p>
                    <p className="text-sm text-slate-200">accompaniment.wav</p>
                  </div>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </div>

      {/* Right: RVC Settings Panel */}
      <motion.div
        initial={shouldReduceMotion ? false : { opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        className="flex flex-col gap-4"
      >
        {/* Voice Model Selection */}
        <div className="p-4 bg-slate-800/50 rounded-lg">
          <h4 className="text-sm font-semibold text-slate-300 mb-3">
            変換先の声
          </h4>
          <select className="w-full p-2 bg-slate-700 border border-slate-600 rounded text-slate-200 focus:outline-none focus:ring-2 focus:ring-primary-500">
            <option>モデルを選択...</option>
          </select>
        </div>

        {/* RVC Parameters */}
        <div className="p-4 bg-slate-800/50 rounded-lg">
          <h4 className="text-sm font-semibold text-slate-300 mb-3">
            変換設定
          </h4>
          <div className="space-y-3">
            {/* f0 method */}
            <div>
              <label className="text-xs text-slate-400 mb-1 block">
                ピッチ抽出方法
              </label>
              <select
                value={rvcParams.f0method}
                onChange={(e) => setRvcParams(prev => ({
                  ...prev,
                  f0method: e.target.value as RVCParams['f0method']
                }))}
                className="w-full p-2 bg-slate-700 border border-slate-600 rounded text-sm text-slate-200 focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="harvest">harvest (歌唱推奨)</option>
                <option value="rmvpe">rmvpe (朗読推奨)</option>
                <option value="crepe">crepe (高精度)</option>
                <option value="pm">pm (高速)</option>
              </select>
            </div>

            {/* Protect */}
            <div>
              <label className="text-xs text-slate-400 mb-1 block">
                子音保護: {rvcParams.protect.toFixed(2)}
              </label>
              <input
                type="range"
                min="0.0"
                max="0.5"
                step="0.01"
                value={rvcParams.protect}
                onChange={(e) => setRvcParams(prev => ({
                  ...prev,
                  protect: parseFloat(e.target.value)
                }))}
                className="w-full"
              />
              <p className="text-xs text-slate-500 mt-1">
                値が大きいほど子音がクリア
              </p>
            </div>

            {/* Index Rate */}
            <div>
              <label className="text-xs text-slate-400 mb-1 block">
                インデックス比率: {rvcParams.index_rate.toFixed(2)}
              </label>
              <input
                type="range"
                min="0.0"
                max="1.0"
                step="0.05"
                value={rvcParams.index_rate}
                onChange={(e) => setRvcParams(prev => ({
                  ...prev,
                  index_rate: parseFloat(e.target.value)
                }))}
                className="w-full"
              />
            </div>
          </div>
        </div>

        {/* Convert Button */}
        <motion.button
          disabled={!audioFile || separationStatus !== 'done'}
          className="w-full py-3 bg-primary-600 text-white rounded-lg font-semibold hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          whileHover={shouldReduceMotion ? {} : { scale: 1.02 }}
          whileTap={shouldReduceMotion ? {} : { scale: 0.98 }}
        >
          声を変換
        </motion.button>

        {/* Export Button */}
        <motion.button
          disabled={true}
          className="w-full py-3 bg-slate-700 text-white rounded-lg font-semibold hover:bg-slate-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          whileHover={shouldReduceMotion ? {} : { scale: 1.02 }}
          whileTap={shouldReduceMotion ? {} : { scale: 0.98 }}
        >
          WAVで保存
        </motion.button>
      </motion.div>
    </div>
  )
}
