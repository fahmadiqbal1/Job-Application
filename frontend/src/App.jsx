import { useState } from 'react'
import { PipelineContextProvider, usePipeline } from './context/PipelineContext'
import { TabBar } from './components/TabBar'
import { Dashboard } from './components/Dashboard'
import { ApproveQueue } from './components/ApproveQueue'
import { JobsTab } from './components/JobsTab'
import { ActivityTab } from './components/ActivityTab'
import { SettingsTab } from './components/SettingsTab'

function AppContent() {
  const { activeTab, setActiveTab } = usePipeline()

  const renderTab = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard />
      case 'approve':
        return <ApproveQueue />
      case 'jobs':
        return <JobsTab />
      case 'activity':
        return <ActivityTab />
      case 'settings':
        return <SettingsTab />
      default:
        return <Dashboard />
    }
  }

  return (
    <div className="h-screen flex flex-col bg-zinc-900 text-white">
      {/* Header */}
      <div className="bg-zinc-800 border-b border-zinc-700 px-6 py-4">
        <h1 className="text-2xl font-bold">Job Application Dashboard</h1>
        <p className="text-sm text-zinc-400">Automated job search & application system</p>
      </div>

      {/* Tab Bar */}
      <TabBar activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* Content */}
      <div className="flex-1 overflow-auto p-6">
        {renderTab()}
      </div>
    </div>
  )
}

export default function App() {
  return (
    <PipelineContextProvider>
      <AppContent />
    </PipelineContextProvider>
  )
}
