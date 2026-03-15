import { useEffect, useMemo, useState } from 'react'

import { apiClient } from '../api/client'
import FiltersBar from '../components/FiltersBar'
import GradesTable from '../components/GradesTable'

const defaultDate = new Date().toISOString().slice(0, 10)

const initialFilters = {
  academicYearId: 0,
  semesterId: 0,
  studyForm: '',
  courseId: 0,
  groupId: 0,
  disciplineId: 0,
  lessonDate: defaultDate,
  lessonTypeId: 1,
}

export default function GradesPage() {
  const [filters, setFilters] = useState(initialFilters)
  const [options, setOptions] = useState({
    academicYears: [],
    semesters: [],
    courses: [],
    groups: [],
    disciplines: [],
    gradeTypes: [],
  })
  const [rows, setRows] = useState([])
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    const loadDictionaries = async () => {
      try {
        const [academicYears, semesters, courses, groups, disciplines, gradeTypes] = await Promise.all([
          apiClient.get('/reference-data/academic-years'),
          apiClient.get('/reference-data/semesters'),
          apiClient.get('/reference-data/courses'),
          apiClient.get('/reference-data/groups'),
          apiClient.get('/reference-data/disciplines'),
          apiClient.get('/reference-data/grade-types'),
        ])

        setOptions({
          academicYears: academicYears.data,
          semesters: semesters.data,
          courses: courses.data,
          groups: groups.data,
          disciplines: disciplines.data,
          gradeTypes: gradeTypes.data,
        })
      } catch (apiError) {
        console.error(apiError)
        setError('Не удалось загрузить справочники журнала оценок.')
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
      setError('Заполните все параметры выбора журнала оценок.')
      return
    }

    setLoading(true)
    setError('')
    try {
      const response = await apiClient.get('/grades/journal', {
        params: {
          academic_year_id: filters.academicYearId,
          semester_id: filters.semesterId,
          study_form: filters.studyForm,
          course_id: filters.courseId,
          group_id: filters.groupId,
          discipline_id: filters.disciplineId,
          graded_at: filters.lessonDate,
        },
      })

      setRows(response.data.students.map((row) => ({
        ...row,
        value: row.value ?? '',
        grade_type_id: row.grade_type_id ?? '',
      })))
    } catch (apiError) {
      console.error(apiError)
      setError('Не удалось открыть журнал оценок.')
    } finally {
      setLoading(false)
    }
  }

  const saveJournal = async () => {
    setSaving(true)
    setError('')
    try {
      const items = rows
        .filter((row) => row.grade_type_id && row.value !== '' && row.value !== null)
        .map((row) => ({
          student_id: row.student_id,
          grade_type_id: Number(row.grade_type_id),
          value: Number(row.value),
        }))

      await apiClient.post('/grades/journal/save', {
        discipline_id: filters.disciplineId,
        graded_at: filters.lessonDate,
        items,
      })
    } catch (apiError) {
      console.error(apiError)
      setError('Не удалось сохранить журнал оценок.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <>
      <h1>Журнал оценок</h1>
      {error && <p className="error-text">{error}</p>}
      <FiltersBar
        filters={filters}
        options={options}
        onChange={onChangeFilter}
        onOpenJournal={openJournal}
        isLoading={loading}
      />

      {rows.length > 0 && (
        <GradesTable
          rows={rows}
          gradeTypes={options.gradeTypes}
          onRowsChange={setRows}
          onSave={saveJournal}
          saving={saving}
        />
      )}
    </>
  )
}
