import { lazy, Suspense } from 'react'
import { Routes, Route } from 'react-router-dom'
import { AppShell } from './layout/AppShell'
import { Skeleton } from './components/Skeleton'

const CommandCenter = lazy(() => import('./pages/command-center'))
const Evaluate = lazy(() => import('./pages/evaluate'))
const Compare = lazy(() => import('./pages/evaluate/compare'))
const Applications = lazy(() => import('./pages/applications'))
const CVStudio = lazy(() => import('./pages/cv-studio'))
const Discover = lazy(() => import('./pages/discover'))
const Prepare = lazy(() => import('./pages/prepare'))
const Outreach = lazy(() => import('./pages/outreach'))
const Insights = lazy(() => import('./pages/insights'))
const Settings = lazy(() => import('./pages/settings'))

function PageLoader() {
  return (
    <div className="p-8 space-y-4">
      <Skeleton className="h-8 w-48 rounded-xl" />
      <Skeleton className="h-4 w-64 rounded" />
      <div className="grid grid-cols-3 gap-4 mt-6">
        {[1, 2, 3].map(i => <Skeleton key={i} className="h-32 rounded-xl" />)}
      </div>
    </div>
  )
}

export default function App() {
  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route
          path="/*"
          element={
            <Suspense fallback={<PageLoader />}>
              <Routes>
                <Route index element={<CommandCenter />} />
                <Route path="evaluate" element={<Evaluate />} />
                <Route path="evaluate/compare" element={<Compare />} />
                <Route path="applications" element={<Applications />} />
                <Route path="cv-studio" element={<CVStudio />} />
                <Route path="discover" element={<Discover />} />
                <Route path="prepare" element={<Prepare />} />
                <Route path="outreach" element={<Outreach />} />
                <Route path="insights" element={<Insights />} />
                <Route path="settings" element={<Settings />} />
              </Routes>
            </Suspense>
          }
        />
      </Route>
    </Routes>
  )
}
