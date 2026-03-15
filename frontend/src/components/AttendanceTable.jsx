import { useMemo, useState } from 'react'

export const statusByCode = {
  present: { id: 1, text: 'Присутствовал', color: '#d1fae5' },
  absent: { id: 2, text: 'Отсутствовал', color: '#fee2e2' },
  excused: { id: 3, text: 'Уважительная причина', color: '#fef3c7' },
  late: { id: 4, text: 'Опоздал', color: '#dbeafe' }
}

const statuses = [statusByCode.present, statusByCode.absent, statusByCode.excused, statusByCode.late]

export default function AttendanceTable({ rows, onRowsChange, onSave, saving }) {
  const [query, setQuery] = useState('')

  const filtered = useMemo(() => rows.filter((row) => row.full_name.toLowerCase().includes(query.toLowerCase())), [rows, query])

  const updateStatus = (studentId) => {
    onRowsChange(rows.map((row) => {
      if (row.student_id !== studentId) return row
      const currentIndex = statuses.findIndex((item) => item.id === row.status_id)
      const nextStatus = statuses[(currentIndex + 1 + statuses.length) % statuses.length]
      return { ...row, status_id: nextStatus.id }
    }))
  }

  const markAllPresent = () => {
    onRowsChange(rows.map((row) => ({ ...row, status_id: statusByCode.present.id })))
  }

  const getStatus = (statusId) => statuses.find((item) => item.id === statusId) || statusByCode.absent

  return (
    <section>
      <div className="toolbar">
        <input placeholder="Поиск по студенту" value={query} onChange={(e) => setQuery(e.target.value)} />
        <button onClick={markAllPresent}>Все присутствовали</button>
        <button onClick={onSave} disabled={saving}>{saving ? 'Сохранение...' : 'Сохранить'}</button>
      </div>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th className="sticky">ФИО студента</th>
              <th>Статус</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((row) => {
              const status = getStatus(row.status_id)
              return (
                <tr key={row.student_id}>
                  <td className="sticky">{row.full_name}</td>
                  <td>
                    <button style={{ background: status.color }} onClick={() => updateStatus(row.student_id)}>
                      {status.text}
                    </button>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </section>
  )
}
