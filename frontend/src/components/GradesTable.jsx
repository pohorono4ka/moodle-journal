import { useMemo, useState } from 'react'

export default function GradesTable({ rows, gradeTypes, onRowsChange, onSave, saving }) {
  const [query, setQuery] = useState('')

  const filtered = useMemo(() => rows.filter((row) => row.full_name.toLowerCase().includes(query.toLowerCase())), [rows, query])

  const updateRow = (studentId, key, value) => {
    onRowsChange(rows.map((row) => (row.student_id === studentId ? { ...row, [key]: value } : row)))
  }

  return (
    <section>
      <div className="toolbar">
        <input placeholder="Поиск по студенту" value={query} onChange={(e) => setQuery(e.target.value)} />
        <button onClick={onSave} disabled={saving}>{saving ? 'Сохранение...' : 'Сохранить оценки'}</button>
      </div>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th className="sticky">ФИО студента</th>
              <th>Вид контроля</th>
              <th>Оценка</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((row) => (
              <tr key={row.student_id}>
                <td className="sticky">{row.full_name}</td>
                <td>
                  <select
                    value={row.grade_type_id ?? ''}
                    onChange={(e) => updateRow(row.student_id, 'grade_type_id', Number(e.target.value))}
                  >
                    <option value="">Выберите</option>
                    {gradeTypes.map((type) => <option key={type.id} value={type.id}>{type.name}</option>)}
                  </select>
                </td>
                <td>
                  <input
                    type="number"
                    min="0"
                    max="100"
                    step="0.5"
                    value={row.value ?? ''}
                    onChange={(e) => updateRow(row.student_id, 'value', e.target.value === '' ? '' : Number(e.target.value))}
                  />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  )
}
