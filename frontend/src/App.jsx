import { Navigate, Route, Routes } from 'react-router-dom'
import AppLayout from './layouts/AppLayout'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import DisciplinesPage from './pages/DisciplinesPage'
import AttendancePage from './pages/AttendancePage'
import GradesPage from './pages/GradesPage'
import ReportsPage from './pages/ReportsPage'
import SyncPage from './pages/SyncPage'
import UsersRolesPage from './pages/UsersRolesPage'
import AuditPage from './pages/AuditPage'

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route element={<AppLayout />}>
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/disciplines" element={<DisciplinesPage />} />
        <Route path="/attendance" element={<AttendancePage />} />
        <Route path="/grades" element={<GradesPage />} />
        <Route path="/reports" element={<ReportsPage />} />
        <Route path="/sync" element={<SyncPage />} />
        <Route path="/users-roles" element={<UsersRolesPage />} />
        <Route path="/audit" element={<AuditPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  )
}
