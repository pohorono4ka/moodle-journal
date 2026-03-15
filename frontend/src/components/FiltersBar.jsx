export default function FiltersBar({
  filters,
  options,
  onChange,
  onOpenJournal,
  isLoading,
}) {
  return (
    <section className="filters-bar">
      <label>
        Учебный год
        <select value={filters.academicYearId} onChange={(e) => onChange('academicYearId', Number(e.target.value))}>
          <option value={0}>Выберите</option>
          {options.academicYears.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}
        </select>
      </label>

      <label>
        Семестр
        <select value={filters.semesterId} onChange={(e) => onChange('semesterId', Number(e.target.value))}>
          <option value={0}>Выберите</option>
          {options.semesters.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}
        </select>
      </label>

      <label>
        Форма обучения
        <select value={filters.studyForm} onChange={(e) => onChange('studyForm', e.target.value)}>
          <option value="">Выберите</option>
          <option value="full_time">Очное</option>
          <option value="part_time">Заочное</option>
        </select>
      </label>

      <label>
        Курс
        <select value={filters.courseId} onChange={(e) => onChange('courseId', Number(e.target.value))}>
          <option value={0}>Выберите</option>
          {options.courses.map((item) => <option key={item.id} value={item.id}>{item.number}</option>)}
        </select>
      </label>

      <label>
        Группа
        <select value={filters.groupId} onChange={(e) => onChange('groupId', Number(e.target.value))}>
          <option value={0}>Выберите</option>
          {options.groups.map((item) => <option key={item.id} value={item.id}>{item.code}</option>)}
        </select>
      </label>

      <label>
        Дисциплина
        <select value={filters.disciplineId} onChange={(e) => onChange('disciplineId', Number(e.target.value))}>
          <option value={0}>Выберите</option>
          {options.disciplines.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}
        </select>
      </label>

      <label>
        Дата занятия
        <input type="date" value={filters.lessonDate} onChange={(e) => onChange('lessonDate', e.target.value)} />
      </label>

      <button onClick={onOpenJournal} disabled={isLoading}>Открыть журнал</button>
    </section>
  )
}
