import { useState } from 'react'
import { Outlet, useLocation } from 'react-router-dom'
import { AnimatePresence, motion } from 'framer-motion'
import { Toaster } from 'sonner'
import { useHotkeys } from 'react-hotkeys-hook'
import { Sidebar } from './Sidebar'
import { CommandPalette } from '@/components/CommandPalette'

export function AppShell() {
  const location = useLocation()
  const [paletteOpen, setPaletteOpen] = useState(false)
  useHotkeys(['meta+k', 'ctrl+k'], () => setPaletteOpen(o => !o), { preventDefault: true })

  return (
    <div className="min-h-screen bg-navy-950 text-white font-body">
      {/* Background gradient */}
      <div className="fixed inset-0 bg-[radial-gradient(ellipse_at_top_left,rgba(12,74,110,0.15),transparent_50%),radial-gradient(ellipse_at_bottom_right,rgba(88,28,135,0.15),transparent_50%)] pointer-events-none" />

      <Sidebar onCommandPalette={() => setPaletteOpen(true)} />
      <CommandPalette open={paletteOpen} onClose={() => setPaletteOpen(false)} />

      {/* Main content */}
      <main className="ml-64 min-h-screen relative">
        <AnimatePresence mode="wait">
          <motion.div
            key={location.pathname}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.2, ease: 'easeOut' }}
            className="h-full"
          >
            <Outlet />
          </motion.div>
        </AnimatePresence>
      </main>

      <Toaster
        position="bottom-right"
        toastOptions={{
          style: { background: '#141b2d', border: '1px solid rgba(255,255,255,0.1)', color: 'white' },
        }}
      />
    </div>
  )
}
