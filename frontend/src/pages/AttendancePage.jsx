import { useEffect, useMemo, useState } from 'react'

import { apiClient } from '../api/client'
import AttendanceTable, { statusByCode } from '../components/AttendanceTable'
import FiltersBar from '../components/FiltersBar'

const defaultDate = new Date().toISOString().slice(0, 10)

const initialFilters = {
  academicYearId: 0,
  semesterId: 0,
  studyForm: '',
  courseId: 0,
  groupId: 0,
  disciplineId: 0,
  lessonDate: defaultDate,
  lessonTypeId: 1
}

export default function AttendancePage() {
  const [filters, setFilters] = useState(initialFilters)
  const [options, setOptions] = useState({
    academicYears: [],
    semesters: [],
    courses: [],
    groups: [],
    disciplines: []
  })
  const [rows, setRows] = useState([])
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    const loadDictionaries = async () => {
      try {
        const [academicYears, semesters, courses, groups, disciplines] = await Promise.all([
          apiClient.get('/reference-data/academic-years'),
          apiClient.get('/reference-data/semesters'),
          apiClient.get('/reference-data/courses'),
          apiClient.get('/reference-data/groups'),
          apiClient.get('/reference-data/disciplines')
        ])
        setOptions({
          academicYears: academicYears.data,
          semesters: semesters.data,
          courses: courses.data,
          groups: groups.data,
          disciplines: disciplines.data
        })
      } catch (apiError) {
        console.error(apiError)
        setError('Не удалось загрузить справочники. Проверьте авторизацию и доступность backend.')
      }
    }

    loadDictionaries()
  }, [])

  const canOpenJournal = useMemo(() => (
    Boolean(filters.academicYearId && filters.semesterId && filters.studyForm && filters.courseId && filters.groupId && filters.disciplineId)
  ), [filters])

  const onChangeFilter = (key, value) => {
    setFilters((prev) => ({ ...prev, [key]: value }))
  }

  const openJournal = async () => {
    if (!canOpenJournal) {
      setError('Заполните все параметры выбора журнала.')
      return
    }

    setLoading(true)
    setError('')
    try {
      const response = await apiClient.get('/attendance/journal', {
        params: {
          academic_year_id: filters.academicYearId,
          semester_id: filters.semesterId,
          study_form: filters.studyForm,
          course_id: filters.courseId,
          group_id: filters.groupId,
          discipline_id: filters.disciplineId,
          lesson_date: filters.lessonDate,
          lesson_type_id: filters.lessonTypeId
        }
      })

      const hydratedRows = response.data.students.map((item) => ({
        ...item,
        status_id: item.status_id ?? statusByCode.absent.id
      }))

      setRows(hydratedRows)
    } catch (apiError) {
      console.error(apiError)
      setError('Не удалось открыть журнал. Проверьте корректность параметров и доступ к API.')
    } finally {
      setLoading(false)
    }
  }

  const saveJournal = async () => {
    setSaving(true)
    setError('')
    try {
      await apiClient.post('/attendance/journal/save', {
        discipline_id: filters.disciplineId,
        lesson_date: filters.lessonDate,
        lesson_type_id: filters.lessonTypeId,
        items: rows.map((row) => ({
          student_id: row.student_id,
          status_id: row.status_id
        }))
      })
    } catch (apiError) {
      console.error(apiError)
      setError('Не удалось сохранить посещаемость.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <>
      <h1>Журнал посещаемости</h1>
      {error && <p className="error-text">{error}</p>}
      <FiltersBar
        filters={filters}
        options={options}
        onChange={onChangeFilter}
        onOpenJournal={openJournal}
        isLoading={loading}
      />
      {rows.length > 0 && (
        <AttendanceTable
          rows={rows}
          onRowsChange={setRows}
          onSave={saveJournal}
          saving={saving}
        />
      )}
    </>
  )
}
