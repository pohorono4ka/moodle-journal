import { Link, Outlet } from 'react-router-dom'

const links = [
  ['Дашборд', '/dashboard'],
  ['Мои дисциплины', '/disciplines'],
  ['Журнал посещаемости', '/attendance'],
  ['Журнал оценок', '/grades'],
  ['Отчёты', '/reports'],
  ['Синхронизация', '/sync'],
  ['Пользователи и роли', '/users-roles'],
  ['Аудит', '/audit']
]

export default function AppLayout() {
  return (
    <div className="app-shell">
      <aside>
        <h2>Электронный журнал</h2>
        <nav>
          {links.map(([label, path]) => (
            <Link key={path} to={path}>{label}</Link>
          ))}
        </nav>
      </aside>
      <main>
        <Outlet />
      </main>
    </div>
  )
}
