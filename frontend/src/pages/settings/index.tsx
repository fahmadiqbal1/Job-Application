import { motion } from 'framer-motion'
import { ProfileEditor } from './ProfileEditor'
import { CVEditor } from './CVEditor'
import { PortalsEditor } from './PortalsEditor'
import { APIKeys } from './APIKeys'

export default function SettingsPage() {
  return (
    <div className="p-8 space-y-6">
      <motion.div initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }}>
        <h1 className="text-2xl font-display font-bold text-white">Settings</h1>
        <p className="text-sm text-white/40 font-body mt-1">Configure your profile, CV, and portals</p>
      </motion.div>

      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-4">
          <ProfileEditor />
          <APIKeys />
        </div>
        <div className="space-y-4">
          <CVEditor />
          <PortalsEditor />
        </div>
      </div>
    </div>
  )
}
